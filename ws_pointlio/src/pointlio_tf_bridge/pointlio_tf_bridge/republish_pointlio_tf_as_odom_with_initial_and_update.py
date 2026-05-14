#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import tf2_ros


def quat_conjugate(q):
    x, y, z, w = q
    return (-x, -y, -z, w)


def quat_multiply(q1, q2):
    return quat_normalize(*quat_multiply_raw(q1, q2))


def quat_multiply_raw(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return (
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
    )


def rotate_vec(q, v):
    q = quat_normalize(*q)
    qv = (v[0], v[1], v[2], 0.0)
    qr = quat_multiply_raw(
        quat_multiply_raw(q, qv),
        quat_conjugate(q),
    )
    return qr[0], qr[1], qr[2]


def invert_transform(t, q, logger):
    qi = quat_conjugate(q)
    rt = rotate_vec(qi, (-t[0], -t[1], -t[2]))
    return rt, qi


def compose_transform(t1, q1, t2, q2):
    rt2 = rotate_vec(q1, t2)
    t = (
        t1[0] + rt2[0],
        t1[1] + rt2[1],
        t1[2] + rt2[2],
    )
    q = quat_multiply(q1, q2)
    return t, q


def quat_normalize(x, y, z, w):
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n == 0.0:
        return 0.0, 0.0, 0.0, 1.0
    return x / n, y / n, z / n, w / n


def rpy_to_quat(roll, pitch, yaw):
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)

    return quat_normalize(
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


class TFRepublisher(Node):
    def __init__(self):
        super().__init__("pointlio_tf_republisher")

        self.declare_parameter("source_parent", "camera_init")
        self.declare_parameter("source_child", "aft_mapped")
        self.declare_parameter("target_parent", "odom")
        self.declare_parameter("target_child", "base_link")
        self.declare_parameter("publish_odom", True)
        self.declare_parameter("rate", 50.0)
        self.declare_parameter("tf_timeout", 0.2)

        self.declare_parameter("base_to_lidar_xyz", [0.0, 0.0, 0.0])
        self.declare_parameter("base_to_lidar_rpy", [0.0, 0.0, math.pi])

        self.declare_parameter("initial_odom_to_base_link_xyz", [0.0, 0.0, 0.0])
        self.declare_parameter("initial_odom_to_base_link_rpy", [0.0, 0.0, 0.0])

        self.base_to_lidar_xyz = list(
            self.get_parameter("base_to_lidar_xyz").get_parameter_value().double_array_value
        )
        self.base_to_lidar_rpy = list(
            self.get_parameter("base_to_lidar_rpy").get_parameter_value().double_array_value
        )

        self.initial_odom_to_base_link_xyz = list(
            self.get_parameter("initial_odom_to_base_link_xyz").get_parameter_value().double_array_value
        )
        self.initial_odom_to_base_link_rpy = list(
            self.get_parameter("initial_odom_to_base_link_rpy").get_parameter_value().double_array_value
        )

        self.source_parent = self.get_parameter("source_parent").get_parameter_value().string_value
        self.source_child = self.get_parameter("source_child").get_parameter_value().string_value
        self.target_parent = self.get_parameter("target_parent").get_parameter_value().string_value
        self.target_child = self.get_parameter("target_child").get_parameter_value().string_value
        self.publish_odom = self.get_parameter("publish_odom").get_parameter_value().bool_value
        self.rate_hz = self.get_parameter("rate").get_parameter_value().double_value
        self.tf_timeout = Duration(
            seconds=self.get_parameter("tf_timeout").get_parameter_value().double_value
        )

        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=10.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.odom_pub = None
        if self.publish_odom:
            self.odom_pub = self.create_publisher(Odometry, "odom", 10)

        self.odominit_sub = self.create_subscription(
            String,
            "/odominit_update",
            self.on_odominit_update,
            10,
        )

        period = 1.0 / max(1e-6, self.rate_hz)
        self.timer = self.create_timer(period, self.on_timer)

        self.get_logger().info("TF republisher initialized")

    def on_odominit_update(self, msg):
        try:
            parts = [float(x.strip()) for x in msg.data.split(",")]

            if len(parts) != 3:
                raise ValueError("Expected format: x, y, yaw")

            x, y, yaw = parts

            self.initial_odom_to_base_link_xyz = [x, y, 0.0]
            self.initial_odom_to_base_link_rpy = [0.0, 0.0, yaw]

            self.get_logger().info(
                f"Updated initial odom transform: x={x}, y={y}, yaw={yaw}"
            )

        except Exception as e:
            self.get_logger().error(
                f"Failed to parse /odominit_update message '{msg.data}': {e}"
            )

    def on_timer(self):
        try:
            trans = self.tf_buffer.lookup_transform(
                self.source_parent,
                self.source_child,
                rclpy.time.Time(),
                timeout=self.tf_timeout,
            )
        except Exception as e:
            self.get_logger().warn(
                f"TF lookup failed for {self.source_parent}->{self.source_child}: {e}",
                throttle_duration_sec=2.0,
            )
            return

        out = TransformStamped()
        # tf: for odom -> base_link, should use now()?
        #out.header.stamp = trans.header.stamp
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = self.target_parent
        out.child_frame_id = self.target_child

        t_odom_lidar = (
            trans.transform.translation.x,
            trans.transform.translation.y,
            trans.transform.translation.z,
        )

        q_odom_lidar = quat_normalize(
            trans.transform.rotation.x,
            trans.transform.rotation.y,
            trans.transform.rotation.z,
            trans.transform.rotation.w,
        )

        t_base_lidar = tuple(self.base_to_lidar_xyz)
        q_base_lidar = rpy_to_quat(*self.base_to_lidar_rpy)

        t_lidar_base, q_lidar_base = invert_transform(
            t_base_lidar,
            q_base_lidar,
            self.get_logger(),
        )

        t_initial = tuple(self.initial_odom_to_base_link_xyz)
        q_initial = rpy_to_quat(*self.initial_odom_to_base_link_rpy)

        t_camera_base, q_camera_base = compose_transform(
            t_odom_lidar,
            q_odom_lidar,
            t_lidar_base,
            q_lidar_base,
        )

        t_odom_base, q_odom_base = compose_transform(
            t_initial,
            q_initial,
            t_camera_base,
            q_camera_base,
        )

        out.transform.translation.x = t_odom_base[0]
        out.transform.translation.y = t_odom_base[1]
        out.transform.translation.z = t_odom_base[2]

        out.transform.rotation.x = q_odom_base[0]
        out.transform.rotation.y = q_odom_base[1]
        out.transform.rotation.z = q_odom_base[2]
        out.transform.rotation.w = q_odom_base[3]

        self.tf_broadcaster.sendTransform(out)

        if self.publish_odom and self.odom_pub is not None:
            odom = Odometry()

            odom.header.stamp = out.header.stamp
            odom.header.frame_id = self.target_parent
            odom.child_frame_id = self.target_child

            odom.pose.pose.position.x = out.transform.translation.x
            odom.pose.pose.position.y = out.transform.translation.y
            odom.pose.pose.position.z = out.transform.translation.z

            odom.pose.pose.orientation.x = out.transform.rotation.x
            odom.pose.pose.orientation.y = out.transform.rotation.y
            odom.pose.pose.orientation.z = out.transform.rotation.z
            odom.pose.pose.orientation.w = out.transform.rotation.w

            self.odom_pub.publish(odom)


def main(args=None):
    rclpy.init(args=args)

    node = TFRepublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
