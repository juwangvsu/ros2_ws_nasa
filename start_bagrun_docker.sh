#!/bin/bash

gnome-terminal -x  $SHELL -ic "cd /tmp; ros2 bag play msbuild/ --clock -r 0.5; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch point_lio mapping_velody16.launch.py use_sim_time:=true; bash"
gnome-terminal -x  $SHELL -ic "rviz2 -d ws_pointlio/src/pointlio_tf_bridge/scan.rviz; bash"
#gnome-terminal -x  $SHELL -ic "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node --ros-args -p use_sim_time:=true  -p target_frame:=base_link   -p transform_tolerance:=0.1   -p min_height:=0.3   -p max_height:=0.9   -p angle_min:=-3.14159   -p angle_max:=3.14159   -p angle_increment:=0.0087   -p range_min:=0.2   -p range_max:=30.0   -p queue_size:=10   -p scan_time:=0.1   -p use_inf:=true   -p inf_epsilon:=1.0   -p output_qos:=reliable   -r cloud_in:=/baal/lidar_points   -r scan:=/scan; bash"
gnome-terminal -x  $SHELL -ic "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node  --ros-args   --params-file ~pointcloud_to_laserscan.yaml   -r cloud_in:=/baal/lidar_points   -r scan:=/scan"
gnome-terminal -x  $SHELL -ic "ros2 launch pointlio_tf_bridge pointlio_tf_bridge.launch.py use_sim_time:=true; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch slam_toolbox online_async_launch.py   slam_params_file:=slam_async_pointlio.yaml; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch nav2_bringup navigation_launch.py   use_sim_time:=true;bash"




