#!/bin/bash

xterm -e bash -ic "cd /tmp; ros2 bag play bag_panda1 --topics /unilidar/cloud /unilidar/imu --remap /unilidar/cloud:=/unilidar/cloud_raw --clock -r 0.8; bash"&
xterm -e bash -ic "python3 change_frame.py; bash"&
xterm -e bash -ic "rviz2 -d ws_pointlio/src/pointlio_tf_bridge/scan_baselink.rviz; bash"&
#xterm -e bash -ic  "ros2 run pointcloud_to_laserscan_logged pointcloud_to_laserscan_logged_node  --ros-args   --params-file pointcloud_to_laserscan_unitree.yaml   -r cloud_in:=/unilidar/cloud   -r scan:=/scan"&
#xterm -e bash -ic  "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node  --ros-args   --params-file pointcloud_to_laserscan_unitree.yaml   -r cloud_in:=/unilidar/cloud   -r scan:=/scan"&
xterm -e bash -ic  "ros2 launch pointlio_tf_bridge pointlio_tf_bridge.launch.py use_sim_time:=true; bash"&




