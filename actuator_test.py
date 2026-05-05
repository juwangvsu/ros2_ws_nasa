#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import time


class ActuatorTest(Node):

    def __init__(self):
        super().__init__('actuator_test')

        self.joy_pub = self.create_publisher(Joy, '/joy', 10)

        # Run after short delay so publisher connects
        self.create_timer(1.0, self.start_once)
        self.started = False

    def start_once(self):
        if not self.started:
            self.started = True
            self.run_sequence()
            self.get_logger().info("Actuator test complete.")
            # Proper shutdown trigger
            rclpy.shutdown()

    def publish_joy(self, a3, a4):
        msg = Joy()
        msg.axes = [0.0] * 8
        msg.axes[3] = a3
        msg.axes[4] = a4

        self.joy_pub.publish(msg)
        self.get_logger().info(f"axes[3]={a3}, axes[4]={a4}")

    def run_sequence(self):
        # ---- low and DIG ----
        self.get_logger().info("DIG")
        self.publish_joy(-1.0, -1.0)
        time.sleep(33)

        # ---- BUCKET UP ----
        self.get_logger().info("BUCKET UP")
        self.publish_joy(1.0, 0.0)
        time.sleep(5)

        # ---- ARM UP ----
        self.get_logger().info("ARM UP")
        self.publish_joy(0.0, 1.0)
        time.sleep(23)

        # ---- LOWER ----
        self.get_logger().info("LOWER")
        self.publish_joy(0.0, -1.0)
        time.sleep(15)

        # ---- DUMP ----
        self.get_logger().info("DUMP")
        self.publish_joy(-1.0, 0.0)


def main(args=None):
    rclpy.init(args=args)
    node = ActuatorTest()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
