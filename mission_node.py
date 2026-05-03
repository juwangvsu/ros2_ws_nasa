#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import Joy
from nav_msgs.msg import Odometry

import math
import time


class MissionNode(Node):

    def __init__(self):
        super().__init__('mission_node')

        # Subscribers
        self.create_subscription(String, '/usercmd', self.usercmd_callback, 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Publishers
        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.joy_pub = self.create_publisher(Joy, '/joy', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # State
        self.current_position = None
        self.started = False

        self.get_logger().info("Mission node ready. Waiting for 'go' command...")

    def usercmd_callback(self, msg):
        if msg.data == 'go' and not self.started:
            self.started = True
            self.get_logger().info("Received GO command. Starting mission.")
            self.run_mission()

    def odom_callback(self, msg):
        self.current_position = msg.pose.pose.position

    def send_goal(self, x, y):
        goal = PoseStamped()
        goal.header.frame_id = 'global'
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.orientation.w = 1.0

        self.goal_pub.publish(goal)
        self.get_logger().info(f"Goal sent: ({x}, {y})")

    def distance_to(self, x, y):
        if self.current_position is None:
            return float('inf')

        dx = self.current_position.x - x
        dy = self.current_position.y - y
        return math.sqrt(dx * dx + dy * dy)

    def wait_until_reached(self, x, y, threshold=0.5):
        self.get_logger().info("Waiting to reach goal...")
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            dist = self.distance_to(x, y)
            if dist < threshold:
                self.get_logger().info("Reached goal.")
                break

    def publish_joy(self, a3, a4):
        joy = Joy()
        joy.axes = [0.0] * 8
        joy.axes[3] = a3
        joy.axes[4] = a4
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

    def run_mission(self):
        # ---- GO TO FIRST GOAL ----
        self.send_goal(1.0, 4.0)
        self.wait_until_reached(1.0, 4.0)

        # ---- DIG ----
        self.get_logger().info("Digging...")
        self.publish_joy(1.0, 1.0)
        time.sleep(10)

        # ---- MOVE FORWARD ----
        self.get_logger().info("Moving forward...")
        self.move_forward(2.0)

        # ---- SCOOP UP ----
        self.get_logger().info("Scooping...")
        self.publish_joy(1.0, -1.0)
        time.sleep(5)

        # ---- GO TO SECOND GOAL ----
        self.send_goal(5.0, 4.0)
        self.wait_until_reached(5.0, 4.0)

        # ---- LOWER ----
        self.get_logger().info("Lowering...")
        self.publish_joy(-1.0, 0.0)
        time.sleep(5)

        # ---- DUMP ----
        self.get_logger().info("Dumping...")
        self.publish_joy(0.0, 1.0)

        self.get_logger().info("Mission complete.")


def main(args=None):
    rclpy.init(args=args)
    node = MissionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
