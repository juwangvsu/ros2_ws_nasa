from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    source_parent = LaunchConfiguration("source_parent")
    source_child = LaunchConfiguration("source_child")
    target_parent = LaunchConfiguration("target_parent")
    target_child = LaunchConfiguration("target_child")
    publish_odom = LaunchConfiguration("publish_odom")
    rate = LaunchConfiguration("rate")
    tf_timeout = LaunchConfiguration("tf_timeout")

    static_x = LaunchConfiguration("static_x")
    static_y = LaunchConfiguration("static_y")
    static_z = LaunchConfiguration("static_z")
    static_roll = LaunchConfiguration("static_roll")
    static_pitch = LaunchConfiguration("static_pitch")
    static_yaw = LaunchConfiguration("static_yaw")
    static_parent = LaunchConfiguration("static_parent")
    static_child = LaunchConfiguration("static_child")

    bridge = Node(
        package="pointlio_tf_bridge",
        executable="republish_pointlio_tf_as_odom",
        name="pointlio_tf_republisher",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "source_parent": source_parent,
            "source_child": source_child,
            "target_parent": target_parent,
            "target_child": target_child,
            "publish_odom": publish_odom,
            "rate": rate,
            "tf_timeout": tf_timeout,
        }],
    )

    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="base_link_to_baal_base_static_tf",
        output="screen",
        arguments=[
            "--x", static_x,
            "--y", static_y,
            "--z", static_z,
            "--roll", static_roll,
            "--pitch", static_pitch,
            "--yaw", static_yaw,
            "--frame-id", static_parent,
            "--child-frame-id", static_child,
        ],
        parameters=[{"use_sim_time": use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("source_parent", default_value="camera_init"),
        DeclareLaunchArgument("source_child", default_value="aft_mapped"),
        DeclareLaunchArgument("target_parent", default_value="odom"),
        DeclareLaunchArgument("target_child", default_value="base_link"),
        DeclareLaunchArgument("publish_odom", default_value="true"),
        DeclareLaunchArgument("rate", default_value="50.0"),
        DeclareLaunchArgument("tf_timeout", default_value="0.2"),

        DeclareLaunchArgument("static_parent", default_value="base_link"),
        DeclareLaunchArgument("static_child", default_value="baal/base"),
        DeclareLaunchArgument("static_x", default_value="0"),
        DeclareLaunchArgument("static_y", default_value="0"),
        DeclareLaunchArgument("static_z", default_value="0"),
        DeclareLaunchArgument("static_roll", default_value="0"),
        DeclareLaunchArgument("static_pitch", default_value="0"),
        DeclareLaunchArgument("static_yaw", default_value="0"),

        bridge,
        static_tf,
    ])
