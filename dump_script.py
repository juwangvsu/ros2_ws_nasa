#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Joy
import time

class DumpActuatorsNode(Node):

    def __init__(self):
        super().__init__('dump_actuators_node')

        # Subscribers
        self.create_subscription(String, '/usercmd', self.usercmd_callback, 10)

        # Publishers
        self.joy_pub = self.create_publisher(Joy, '/joy', 10)

        self.started = False
        self.get_logger().info("Dump script ready. Send 'go' to /usercmd to begin.")

    def usercmd_callback(self, msg):
        if msg.data == 'go' and not self.started:
            self.started = True
            self.get_logger().info("Starting actuator dump sequence...")
            self.execute_dump()

    def publish_joy(self, a3, a4):
        """
        a3: Bucket Axis (Right Stick Horizontal)
        a4: Arm Axis (Right Stick Vertical)
        """
        joy = Joy()
        joy.axes = [0.0] * 8
        joy.axes[3] = a3
        joy.axes[4] = a4
        self.joy_pub.publish(joy)

    def execute_dump(self):
        # ---- STEP 1: LOWER ARM ----
        self.get_logger().info("Lowering arm...")
        self.publish_joy(0.0, -1.0)
        time.sleep(7)

        # ---- STEP 2: DUMP BUCKET ----
        self.get_logger().info("Dumping bucket...")
        self.publish_joy(-1.0, 0.0)
        time.sleep(5.5)

        # ---- STEP 3: RETRACT BUCKET ----
        self.get_logger().info("Retracting bucket...")
        self.publish_joy(1.0, 0.0)
        time.sleep(5.5)

        # ---- STEP 4: STOP ALL ----
        self.get_logger().info("Sequence complete. Stopping actuators.")
        self.publish_joy(0.0, 0.0)

        self.started = False

def main(args=None):
    rclpy.init(args=args)
    node = DumpActuatorsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
