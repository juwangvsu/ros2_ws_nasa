#!/bin/bash
gnome-terminal -x  $SHELL -ic "ros2 launch unitree_lidar_ros2 launch.py cloud_topic:=/unilidar/cloud_raw ; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch point_lio mapping_unilidar_l2.launch.py; bash"
gnome-terminal -x  $SHELL -ic "python3 change_frame.py; bash"

#gnome-terminal -x  $SHELL -ic "rviz2 -d ws_pointlio/src/pointlio_tf_bridge/scan.rviz; bash"
gnome-terminal -x  $SHELL -ic "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node  --ros-args   --params-file pointcloud_to_laserscan.yaml   -r cloud_in:=/unilidar/cloud   -r scan:=/scan"
gnome-terminal -x  $SHELL -ic "ros2 launch pointlio_tf_bridge pointlio_tf_bridge.launch.py ; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch slam_toolbox online_async_launch.py   slam_params_file:=slam_async_pointlio.yaml; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch nav2_bringup navigation_launch.py   use_sim_time:=true params_file:=nav2_pointlio.yaml;bash"

