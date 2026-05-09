from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='fake_scan2_publisher',
            executable='fake_scan2_node',
            name='fake_scan2_publisher',
            output='screen',
            parameters=[{
                'input_topic': '/scan',
                'output_topic': '/scan2',
                'line_x_m': 1.5,
                'line_y_min_m': -0.2,
                'line_y_max_m': 0.2,
            }],
        )
    ])
