from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value='config/sabertooth_twist.yaml',
            description='Path to the Sabertooth parameter file',
        ),
        Node(
            package='sabertooth_2x32_serial_twist',
            executable='sabertooth_twist_node',
            name='sabertooth_2x32_serial_twist',
            output='screen',
            parameters=[params_file],
        ),
    ])
