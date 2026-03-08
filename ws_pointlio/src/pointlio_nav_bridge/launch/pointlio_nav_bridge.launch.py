from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    laser_map_topic = LaunchConfiguration('laser_map_topic')
    lidar_points_topic = LaunchConfiguration('lidar_points_topic')
    map_topic = LaunchConfiguration('map_topic')
    scan_topic = LaunchConfiguration('scan_topic')
    map_frame = LaunchConfiguration('map_frame')
    odom_frame = LaunchConfiguration('odom_frame')
    base_frame = LaunchConfiguration('base_frame')
    lidar_frame = LaunchConfiguration('lidar_frame')
    resolution = LaunchConfiguration('resolution')
    map_z_min = LaunchConfiguration('map_z_min')
    map_z_max = LaunchConfiguration('map_z_max')
    scan_z_min = LaunchConfiguration('scan_z_min')
    scan_z_max = LaunchConfiguration('scan_z_max')
    range_min = LaunchConfiguration('range_min')
    range_max = LaunchConfiguration('range_max')
    map_publish_period_sec = LaunchConfiguration('map_publish_period_sec')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('laser_map_topic', default_value='/Laser_map'),
        DeclareLaunchArgument('lidar_points_topic', default_value='/baal/lidar_points'),
        DeclareLaunchArgument('map_topic', default_value='/map'),
        DeclareLaunchArgument('scan_topic', default_value='/scan'),
        DeclareLaunchArgument('map_frame', default_value='map'),
        DeclareLaunchArgument('odom_frame', default_value='odom'),
        DeclareLaunchArgument('base_frame', default_value='base_link'),
        DeclareLaunchArgument('lidar_frame', default_value='lidar_link'),
        DeclareLaunchArgument('resolution', default_value='0.15'),
        DeclareLaunchArgument('map_z_min', default_value='0.30'),
        DeclareLaunchArgument('map_z_max', default_value='0.80'),
        DeclareLaunchArgument('scan_z_min', default_value='0.1'),
        DeclareLaunchArgument('scan_z_max', default_value='0.15'),
        DeclareLaunchArgument('range_min', default_value='0.80'),
        DeclareLaunchArgument('range_max', default_value='40.0'),
        DeclareLaunchArgument('map_publish_period_sec', default_value='5.0'),

        # Identity map->odom is only for simple playback/testing. Remove it if some
        # other node already publishes a proper map->odom transform.
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='map_to_odom_tf',
            arguments=['0', '0', '0', '0', '0', '0', map_frame, odom_frame],
        ),

        # Adjust this transform to your actual LiDAR mounting relative to base_link.
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_lidar_tf',
            arguments=['0', '0', '0', '0', '0', '0', base_frame, lidar_frame],
        ),

        Node(
            package='pointlio_nav_bridge',
            executable='map_and_scan_node',
            name='pointlio_map_and_scan_node',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'laser_map_topic': laser_map_topic,
                'lidar_points_topic': lidar_points_topic,
                'map_topic': map_topic,
                'scan_topic': scan_topic,
                'map_frame': map_frame,
                'scan_frame': base_frame,
                'resolution': resolution,
                'map_z_min': map_z_min,
                'map_z_max': map_z_max,
                'scan_z_min': scan_z_min,
                'scan_z_max': scan_z_max,
                'range_min': range_min,
                'range_max': range_max,
                'map_publish_period_sec': map_publish_period_sec,
            }],
        ),
    ])
