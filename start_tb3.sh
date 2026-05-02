#!/bin/bash
#launch gazebo tb3 sim, to verify the system software is good
# 5/2/26 add scan filter node /scan -> /scan_filtered, cap minimum dist
# and nav2 use /scan_filtered 
gnome-terminal -x  $SHELL -ic "conda deactivate; export ROS_DOMAIN_ID=3; ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py use_sim_time:=true; bash"

gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; export ROS_DOMAIN_ID=3; ros2 run laser_filters scan_to_scan_filter_chain --ros-args --params-file scan_filter_tb3.yaml -r scan:=/scan -r scan_filtered:=/scan_filtered --ros-args -p use_sim_time:=True"

gnome-terminal -x  $SHELL -ic "conda deactivate; export ROS_DOMAIN_ID=3; ros2 launch slam_toolbox online_async_launch.py slam_params_file:=mapper_params_online_async_tb3.yaml use_sim_time:=True"
gnome-terminal -x  $SHELL -ic "conda deactivate; export ROS_DOMAIN_ID=3;ros2 run rviz2 rviz2 --ros-args -p use_sim_time:=True"
gnome-terminal -x  $SHELL -ic "conda deactivate; export ROS_DOMAIN_ID=3; ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true"
gnome-terminal -x  $SHELL -ic "export ROS_DOMAIN_ID=3; sleep 10; ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped '{header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}'"


