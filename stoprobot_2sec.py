#!/usr/bin/env python3
# listen to /odominit_update, upon msg pub zero to /cmd_vel for 2 sec

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist


class OdomInitStopNode(Node):

    def __init__(self):
        super().__init__('odominit_stop_node')

        self.sub = self.create_subscription(
            String,
            '/odominit_update',
            self.callback,
            10
        )

        self.pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.timer = None
        self.publish_count = 0
        self.max_count = 80  # 2 sec * 40 Hz

        self.get_logger().info('Listening on /odominit_update')

    def callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')

        # restart stop sequence if already running
        if self.timer is not None:
            self.timer.cancel()

        self.publish_count = 0

        self.timer = self.create_timer(
            1.0 / 40.0,
            self.publish_zero_velocity
        )

    def publish_zero_velocity(self):
        twist = Twist()

        # all values already zero by default
        self.pub.publish(twist)

        self.publish_count += 1

        if self.publish_count >= self.max_count:
            self.timer.cancel()
            self.timer = None
            self.get_logger().info('Finished publishing zero velocity')


def main(args=None):
    rclpy.init(args=args)

    node = OdomInitStopNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
