#!/usr/bin/env python3

import argparse
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_pose_stamped


def yaw_to_quaternion(yaw: float):
    qz = math.sin(yaw / 2.0)
    qw = math.cos(yaw / 2.0)
    return 0.0, 0.0, qz, qw


class GoalPosePublisher(Node):
    def __init__(self, x, y, yaw, frame_id):
        super().__init__("goal_pose_publisher")

        self.pub = self.create_publisher(PoseStamped, "/goal_pose", 10)

        self.target_frame = frame_id
        self.global_frame = "global"

        self.x = x
        self.y = y
        self.yaw = yaw

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def make_global_pose(self):
        pose = PoseStamped()

        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = self.global_frame

        pose.pose.position.x = self.x
        pose.pose.position.y = self.y
        pose.pose.position.z = 0.0

        qx, qy, qz, qw = yaw_to_quaternion(self.yaw)

        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        return pose

    def transform_pose(self, pose):
        if self.target_frame == self.global_frame:
            return pose

        transform = self.tf_buffer.lookup_transform(
            self.target_frame,   # target frame
            self.global_frame,   # source frame
            rclpy.time.Time()
        )

        transformed = do_transform_pose_stamped(pose, transform)

        transformed.header.frame_id = self.target_frame
        transformed.header.stamp = self.get_clock().now().to_msg()

        return transformed

    def publish_goal(self):
        for i in range(5):

            rclpy.spin_once(self, timeout_sec=0.2)

            try:
                global_pose = self.make_global_pose()
                output_pose = self.transform_pose(global_pose)

                self.pub.publish(output_pose)

                self.get_logger().info(
                    f"Published /goal_pose {i+1}/5 "
                    f"frame={output_pose.header.frame_id} "
                    f"x={output_pose.pose.position.x:.3f} "
                    f"y={output_pose.pose.position.y:.3f}"
                )

            except Exception as e:
                self.get_logger().error(f"Failed: {e}")

            self.get_clock().sleep_for(
                rclpy.duration.Duration(seconds=1.0)
            )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--x", type=float, required=True)
    parser.add_argument("--y", type=float, required=True)

    parser.add_argument(
        "--yaw",
        type=float,
        required=True,
        help="Yaw in radians"
    )

    parser.add_argument(
        "--frame-id",
        required=True,
        help="Frame to publish goal in"
    )

    args = parser.parse_args()

    rclpy.init()

    node = GoalPosePublisher(
        args.x,
        args.y,
        args.yaw,
        args.frame_id
    )

    try:
        node.publish_goal()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
