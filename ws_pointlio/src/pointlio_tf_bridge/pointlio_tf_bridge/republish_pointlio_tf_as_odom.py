#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
import tf2_ros


def quat_normalize(x, y, z, w):
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n == 0.0:
        return 0.0, 0.0, 0.0, 1.0
    return x / n, y / n, z / n, w / n


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

        self.source_parent = self.get_parameter("source_parent").get_parameter_value().string_value
        self.source_child = self.get_parameter("source_child").get_parameter_value().string_value
        self.target_parent = self.get_parameter("target_parent").get_parameter_value().string_value
        self.target_child = self.get_parameter("target_child").get_parameter_value().string_value
        self.publish_odom = self.get_parameter("publish_odom").get_parameter_value().bool_value
        self.rate_hz = self.get_parameter("rate").get_parameter_value().double_value
        self.tf_timeout = Duration(seconds=self.get_parameter("tf_timeout").get_parameter_value().double_value)

        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=10.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.odom_pub = None
        if self.publish_odom:
            self.odom_pub = self.create_publisher(Odometry, "odom", 10)

        period = 1.0 / max(1e-6, self.rate_hz)
        self.timer = self.create_timer(period, self.on_timer)

        self.get_logger().info(
            f"Republishing TF {self.source_parent}->{self.source_child} "
            f"as {self.target_parent}->{self.target_child}; "
            f"publish_odom={self.publish_odom}, rate={self.rate_hz}Hz"
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
        out.header.stamp = trans.header.stamp
        #out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = self.target_parent
        out.child_frame_id = self.target_child

        out.transform.translation.x = trans.transform.translation.x
        out.transform.translation.y = trans.transform.translation.y
        out.transform.translation.z = trans.transform.translation.z

        qx = trans.transform.rotation.x
        qy = trans.transform.rotation.y
        qz = trans.transform.rotation.z
        qw = trans.transform.rotation.w
        qx, qy, qz, qw = quat_normalize(qx, qy, qz, qw)

        out.transform.rotation.x = qx
        out.transform.rotation.y = qy
        out.transform.rotation.z = qz
        out.transform.rotation.w = qw

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
