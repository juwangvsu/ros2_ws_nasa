#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import Joy
from nav_msgs.msg import Odometry

import math
import time
import sys
import argparse
from rclpy.utilities import remove_ros_args

class MissionNode(Node):

    def __init__(self, target_x=4.0, target_y=1.0):
        super().__init__('mission_node')

	# Store coordinates for the first goal
        self.target_x = target_x
        self.target_y = target_y

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

        self.get_logger().info(
	f"Mission node ready. Targeted goal: ({self.target_x}, {self.target_y})."
	" Waiting for 'go' command...")

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
    
    #turn at angular velocity for some duration
    def turn_deg(self, duration=2.0, speed=0.5):
        twist = Twist()
        twist.angular.z = speed

        start = time.time()
        while time.time() - start < duration:
            self.cmd_vel_pub.publish(twist)
            time.sleep(0.1)

        # Stop
        self.cmd_vel_pub.publish(Twist())

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
        # ---- Wait for 10 secs ----
        #time.sleep(10)

        # ---- Drive forward slowly send /cmd_vel for 3 secs ----
        self.get_logger().info("Moving forward...")
        self.move_forward(3.0, speed=0.5)
        time.sleep(3)

        # Wait 15 secs for map building
        #time.sleep(15)

        # ---- GO TO FIRST GOAL ----
        self.send_goal(self.target_x, self.target_y)
        self.wait_until_reached(self.target_x, self.target_y)

        # ---- DIG ----
        self.get_logger().info("Priming...")
        self.publish_joy(-1.0, -1.0)
        time.sleep(33)

        # ---- MOVE FORWARD ----
        self.get_logger().info("Moving forward...")
        self.move_forward(2.0, speed=0.5)
        time.sleep(5)

        # ---- Turn Test  ----
        self.get_logger().info("turning . ...")
        self.turn_deg(2.0, speed=0.5)

        # ---- BUCKET UP ----
        self.get_logger().info("Scooping...")
        self.publish_joy(1.0, 0.0)
        time.sleep(5)

        # ---- ARM UP ----
        self.get_logger().info("Lifting...")
        self.publish_joy(0.0, 1.0)
        time.sleep(23)

        # ---- GO TO SECOND GOAL ----
        self.send_goal(0.0, 0.0)
        self.wait_until_reached(0.0, 0.0)

        # ---- LOWER ----
        self.get_logger().info("Lowering...")
        self.publish_joy(0.0, -1.0)
        time.sleep(15)

        # ---- DUMP ----
        self.get_logger().info("Dumping...")
        self.publish_joy(-1.0, 0.0)

        self.get_logger().info("Mission complete.")

def main(args=None):
    # 1. Strip away internal ROS arguments from command line strings
    clean_args = remove_ros_args(args=sys.argv)

    # 2. Setup standard argparse to capture --x and --y flags
    parser = argparse.ArgumentParser(description="Launch mission with explicit coordinates.")
    parser.add_argument('--x', type=float, default=1.0, help='Target X coordinate for first goal')
    parser.add_argument('--y', type=float, default=4.0, help='Target Y coordinate for first goal')
    
    # Parse the custom flags (ignoring the script name itself at index 0)
    parsed_args = parser.parse_args(clean_args[1:])

    # 3. Spin up the ROS environment
    rclpy.init(args=args)
    
    # 4. Pass the extracted CLI floats into the node initialization
    node = MissionNode(target_x=parsed_args.x, target_y=parsed_args.y)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
