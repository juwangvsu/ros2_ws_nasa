#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from std_msgs.msg import String
import tf2_ros


def quat_to_yaw(x, y, z, w):
    # ROS quaternion order is x, y, z, w.
    # yaw = atan2(2(wz + xy), 1 - 2(y^2 + z^2))
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


class OdomInitPublisher(Node):
    def __init__(self):
        super().__init__("odominit_update_publisher")

        self.declare_parameter("parent_frame", "odom")
        self.declare_parameter("child_frame", "baal/imu_initial")
        self.declare_parameter("output_topic", "/odominit_update")
        self.declare_parameter("tf_timeout", 1.0)
        self.declare_parameter("publish_delay", 0.5)
        self.declare_parameter("publish_count", 5)

        self.parent_frame = self.get_parameter("parent_frame").get_parameter_value().string_value
        self.child_frame = self.get_parameter("child_frame").get_parameter_value().string_value
        self.output_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        self.tf_timeout = Duration(
            seconds=self.get_parameter("tf_timeout").get_parameter_value().double_value
        )
        self.publish_delay = self.get_parameter("publish_delay").get_parameter_value().double_value
        self.publish_count = self.get_parameter("publish_count").get_parameter_value().integer_value

        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=10.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.pub = self.create_publisher(String, self.output_topic, 10)

        # Delay first lookup slightly so the TF listener has time to receive TF data.
        self.timer = self.create_timer(self.publish_delay, self.on_timer)

        self.done = False

        self.get_logger().info(
            f"Will read TF {self.parent_frame}->{self.child_frame} "
            f"and publish x, y, yaw to {self.output_topic}"
        )

    def on_timer(self):
        if self.done:
            return

        try:
            trans = self.tf_buffer.lookup_transform(
                self.parent_frame,
                self.child_frame,
                rclpy.time.Time(),  # latest available transform
                timeout=self.tf_timeout,
            )
        except Exception as e:
            self.get_logger().warn(
                f"TF lookup failed for {self.parent_frame}->{self.child_frame}: {e}",
                throttle_duration_sec=1.0,
            )
            return

        x = trans.transform.translation.x
        y = trans.transform.translation.y

        q = trans.transform.rotation
        #yaw = 0.0
        yaw = quat_to_yaw(q.x, q.y, q.z, q.w)

        msg = String()
        msg.data = f"{x}, {y}, {yaw}"

        #for _ in range(max(1, self.publish_count)):
        self.pub.publish(msg)

        self.get_logger().info(f"Published to {self.output_topic}: {msg.data}")

        self.done = True
        self.timer.cancel()


def main(args=None):
    rclpy.init(args=args)

    node = OdomInitPublisher()

    try:
        # Use spin_once so main can detect node.done and exit cleanly.
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
