import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('fiducial_tb3_gazebo_demo')
    tb3_gazebo_share = get_package_share_directory('turtlebot3_gazebo')
    gazebo_ros_share = get_package_share_directory('gazebo_ros')

    world = os.path.join(pkg_share, 'worlds', 'tag_wall_tb3.world')
    apriltag_cfg = os.path.join(pkg_share, 'config', 'apriltag.yaml')
    slam_cfg = os.path.join(pkg_share, 'config', 'slam_toolbox_mapping.yaml')
    anchor_cfg = os.path.join(pkg_share, 'config', 'global_anchor.yaml')

    sdf_candidates = [
        os.path.join(tb3_gazebo_share, 'models', 'turtlebot3_waffle', 'model.sdf'),
        os.path.join(tb3_gazebo_share, 'models', 'turtlebot3_waffle', 'model-1_4.sdf'),
    ]
    robot_sdf = None
    for c in sdf_candidates:
        if os.path.exists(c):
            robot_sdf = c
            break
    if robot_sdf is None:
        robot_sdf = sdf_candidates[0]

    existing_model_path = os.environ.get('GAZEBO_MODEL_PATH', '')
    model_path = os.path.join(pkg_share, 'models') + ':' + os.path.join(tb3_gazebo_share, 'models')
    if existing_model_path:
        model_path += ':' + existing_model_path

    existing_resource_path = os.environ.get('GAZEBO_RESOURCE_PATH', '')
    resource_path = pkg_share
    if existing_resource_path:
        resource_path += ':' + existing_resource_path

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle'),
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_path),
        SetEnvironmentVariable('GAZEBO_RESOURCE_PATH', resource_path),

        #IncludeLaunchDescription(
        #    PythonLaunchDescriptionSource(os.path.join(gazebo_ros_share, 'launch', 'gazebo.launch.py')),
        #    launch_arguments={'world': world, 'verbose': 'true'}.items(),
        #),

        #Node(
        #    package='gazebo_ros',
        #    executable='spawn_entity.py',
        #    arguments=['-entity', 'tb3_waffle', '-file', robot_sdf, '-x', '1.0', '-y', '3.0', '-z', '0.02', '-Y', '-1.57'],
        #    output='screen'
        #),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_scan_tf',
            arguments=['-0.064', '0.0', '0.121', '0', '0', '0', 'base_link', 'base_scan'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_footprint_to',
            arguments=['-0.064', '0.0', '0.121', '0', '0', '0', 'base_footprint', 'base_link'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_camera_tf',
            arguments=['0.069', '-0.047', '0.107', '0', '0', '0', 'base_footprint', 'camera_rgb_frame'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='camera_frame_to_camera_optical',
            arguments=['0.0', '0.0', '0.0', '-1.57079632679', '0', '-1.57079632679', 'camera_rgb_frame', 'camera_rgb_optical_frame'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),

        Node(
            package='image_proc',
            executable='rectify_node',
            name='rectify',
            remappings=[
                ('image', '/camera/image_raw'),
                ('camera_info', '/camera/camera_info'),
                ('image_rect', '/camera/image_rect'),
            ],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
            output='screen',
        ),

        Node(
            package='apriltag_ros',
            executable='apriltag_node',
            name='apriltag',
            remappings=[
                ('image_rect', '/camera/image_raw'),
                ('camera_info', '/camera/camera_info'),
            ],
            parameters=[apriltag_cfg, {'use_sim_time': LaunchConfiguration('use_sim_time')}],
            output='screen',
        ),

        #Node(
        #    package='slam_toolbox',
        #    executable='async_slam_toolbox_node',
        #    name='slam_toolbox',
        #    parameters=[slam_cfg, {'use_sim_time': LaunchConfiguration('use_sim_time')}],
        #    output='screen',
        #),

        Node(
            package='fiducial_tb3_gazebo_demo',
            executable='global_anchor_node',
            name='global_anchor_node',
            parameters=[anchor_cfg, {'use_sim_time': LaunchConfiguration('use_sim_time')}],
            output='screen',
        ),
    ])
