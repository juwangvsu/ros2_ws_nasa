#!/bin/bash
# debug slam crash, 
gnome-terminal -x  $SHELL -ic "ros2 launch unitree_lidar_ros2 launch.py cloud_topic:=/unilidar/cloud ; bash"
gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id baal/imu_initial --child-frame-id baal/imu ; bash"
gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id baal/imu --child-frame-id baal/base; bash"

gnome-terminal -x  $SHELL -ic "ros2 launch point_lio mapping_unilidar_l2.launch.py rviz:=False; bash"
#gnome-terminal -x  $SHELL -ic "python3 change_frame.py; bash"

#gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; rviz2 -d ws_pointlio/src/pointlio_tf_bridge/scan.rviz; bash"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ros2 run pointcloud_to_laserscan_logged pointcloud_to_laserscan_logged_node  --ros-args   --params-file pointcloud_to_laserscan.yaml   -r cloud_in:=/unilidar/cloud   -r scan:=/scan"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ros2 launch pointlio_tf_bridge pointlio_tf_bridge_uni.launch.py rate:=10.0; bash"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ros2 launch slam_toolbox online_async_launch.py   slam_params_file:=slam_async_pointlio_uni.yaml; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch nav2_bringup navigation_launch.py   params_file:=nav2_pointlio.yaml;bash"
#gnome-terminal -x  $SHELL -ic " ros2 launch mdds30_serial_driver mdds30.launch.py; bash" 

