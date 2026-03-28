from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mdds30_serial_driver',
            executable='mdds30_node',
            name='mdds30_serial_driver',
            output='screen',
            parameters=[{
                'port': '/dev/ttyUSB0',
                'baudrate': 9600,
                'max_percent': 60.0,
                'wheel_base': 0.40,
                'watchdog_sec': 0.5,
                'invert_left': False,
                'invert_right': False,
            }],
        )
    ])
