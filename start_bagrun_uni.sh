#!/bin/bash
#bag play unitree lidar cloud frame_id remapped
# ./start_bagrun_uni.sh ~/rosbag2_2026_03_25-18_31_53
gnome-terminal -x  $SHELL -ic "cd ~/; ros2 bag play $1 --topics /unilidar/cloud /unilidar/imu --remap /unilidar/cloud:=/unilidar/cloud --clock -r 0.6; bash"
#gnome-terminal -x  $SHELL -ic "cd ~/; ros2 bag play $1 --topics /unilidar/cloud /unilidar/imu --remap /unilidar/cloud:=/unilidar/cloud_raw --clock -r 0.2; bash"
#gnome-terminal -x  $SHELL -ic "python3 change_frame.py; bash"
#gnome-terminal -x  $SHELL -ic "python3 ceiling_filter.py --ros-args -p ceiling_z:=2.0; bash"
gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id baal/imu_initial --child-frame-id baal/imu ; bash"
gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id baal/imu --child-frame-id baal/base; bash"

gnome-terminal -x  $SHELL -ic "ros2 launch point_lio mapping_unilidar_l2.launch.py use_sim_time:=true; bash"
gnome-terminal -x  $SHELL -ic "rviz2 -d ws_pointlio/src/pointlio_tf_bridge/scan.rviz; bash"
gnome-terminal -x  $SHELL -ic "ros2 run pointcloud_to_laserscan_logged pointcloud_to_laserscan_logged_node  --ros-args   --params-file pointcloud_to_laserscan_unitree_logged.yaml   -r cloud_in:=/unilidar/cloud   -r scan:=/scan"
gnome-terminal -x  $SHELL -ic "ros2 launch pointlio_tf_bridge pointlio_tf_bridge.launch.py use_sim_time:=true static_pitch:=0.26 ; bash" # 15 deg 0.26, 20 deg 0.348 , 30 deg 0.52
gnome-terminal -x  $SHELL -ic "ros2 launch slam_toolbox online_async_launch.py   slam_params_file:=slam_async_pointlio.yaml; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch nav2_bringup navigation_launch.py   use_sim_time:=true params_file:=nav2_pointlio.yaml;bash"

