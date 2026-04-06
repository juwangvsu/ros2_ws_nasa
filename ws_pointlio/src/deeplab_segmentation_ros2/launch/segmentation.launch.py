from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config_file = LaunchConfiguration("config_file")
    return LaunchDescription([
        DeclareLaunchArgument("config_file"),
        Node(
            package="deeplab_segmentation_ros2",
            executable="segmentation_node",
            name="deeplab_segmentation_node",
            output="screen",
            parameters=[config_file],
        ),
    ])
