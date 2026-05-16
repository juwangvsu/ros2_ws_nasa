#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Joy
import time

class DigActuatorsNode(Node):

    def __init__(self):
        super().__init__('dig_actuators_node')

        # Subscriber for the trigger command
        self.create_subscription(String, '/usercmd', self.usercmd_callback, 10)

        # Publisher to control the actuators via Joy topic
        self.joy_pub = self.create_publisher(Joy, '/joy', 10)

        self.started = False
        self.get_logger().info("Dig script ready. Send 'go' to /usercmd to begin digging.")

    def usercmd_callback(self, msg):
        if msg.data == 'go' and not self.started:
            self.started = True
            self.get_logger().info("Starting digging sequence...")
            self.execute_dig()

    def publish_joy(self, bucket_val, arm_val):
        """
        bucket_val: Axis 3 (Right Stick Horizontal)
        arm_val: Axis 4 (Right Stick Vertical)
        """
        joy = Joy()
        joy.axes = [0.0] * 8
        joy.axes[3] = bucket_val
        joy.axes[4] = arm_val

        joy.buttons = [0] * 12
        joy.buttons[5] = 1

        self.joy_pub.publish(joy)

    def move_forward(self, duration=2.0, speed=0.5):
        twist = Twist()
        twist.linear.x = speed

        start = time.time()
        while time.time() - start < duration:
            self.cmd_vel_pub.publish(twist)
            time.sleep(0.1)

        # Stop
        self.cmd_vel_pub.publish(Twist())

    def execute_dig(self):
        # ---- STEP 1: PRIME (Lower Arm and Bucket) ----
        self.get_logger().info("Lowering arm and bucket into digging position...")
        self.publish_joy(-1.0, -1.0)
        time.sleep(33)

        # ---- STEP 2: STOP ----
        self.get_logger().info("Digging position reached. Stopping actuators.")
        self.publish_joy(0.0, 0.0)
	time.sleep(1)

        # ---- STEP 3: Drive forward ----
        self.get_logger().info("Digging")
	self.move_forward(duration=3.0, speed=0.5)
	time.sleep(3)

        # ---- STEP 4: Lift ----
        self.get_logger().info("Raising arm and bucket into travel position...")
        self.publish_joy(1.0, 1.0)
        time.sleep(33)

	self.get_logger().info("Dig complete")

        self.started = False  # Reset for next 'go' command

def main(args=None):
    rclpy.init(args=args)
    node = DigActuatorsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
