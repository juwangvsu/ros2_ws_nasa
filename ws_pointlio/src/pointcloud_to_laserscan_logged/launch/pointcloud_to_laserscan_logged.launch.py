from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='pointcloud_to_laserscan_logged',
            executable='pointcloud_to_laserscan_logged_node',
            name='pointcloud_to_laserscan_logged',
            output='screen',
            parameters=[{
                'input_topic': '/baal/lidar_points',
                'output_topic': '/scan',
                'min_height': -0.3,
                'max_height': 0.3,
                'angle_min': -3.141592653589793,
                'angle_max': 3.141592653589793,
                'angle_increment': 0.017453292519943295,
                'range_min': 0.1,
                'range_max': 100.0,
                'scan_time': 0.1,
                'use_inf': True,
                'inf_epsilon': 1.0,
                'print_per_message': True,
            }],
            remappings=[],
        )
    ])
