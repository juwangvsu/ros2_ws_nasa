from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('mode', default_value='keyboard', description='keyboard or joystick'),
        DeclareLaunchArgument('port', default_value='/dev/ttyUSB0', description='ESP32 serial port'),
        DeclareLaunchArgument('baud', default_value='9600', description='ESP32 baud rate'),
        DeclareLaunchArgument('speed', default_value='30', description='Actuator speed 0-63'),
        DeclareLaunchArgument('joy_topic', default_value='/joy', description='Joystick topic'),
        DeclareLaunchArgument('deadzone', default_value='0.25', description='Joystick axis deadzone'),
        DeclareLaunchArgument('send_period', default_value='0.10', description='Command send period in seconds'),
        Node(
            package='esp32_actuator_control',
            executable='actuator_control_node',
            name='actuator_control_node',
            output='screen',
            emulate_tty=True,
            parameters=[{
                'mode': LaunchConfiguration('mode'),
                'port': LaunchConfiguration('port'),
                'baud': LaunchConfiguration('baud'),
                'speed': LaunchConfiguration('speed'),
                'joy_topic': LaunchConfiguration('joy_topic'),
                'deadzone': LaunchConfiguration('deadzone'),
                'send_period': LaunchConfiguration('send_period'),
            }],
        ),
    ])
