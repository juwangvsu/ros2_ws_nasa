#!/bin/bash

xterm -e bash -ic "cd /tmp; ros2 bag play msbuild --clock -r 0.8; bash"&
xterm -e bash -ic "rviz2 -d ws_pointlio/src/pointlio_tf_bridge/scan_baselink.rviz; bash"&
#xterm -e bash -ic  "ros2 run pointcloud_to_laserscan_logged pointcloud_to_laserscan_logged_node  --ros-args   --params-file pointcloud_to_laserscan.yaml   -r cloud_in:=/baal/lidar_points   -r scan:=/scan"&
#xterm -e bash -ic  "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node  --ros-args   --params-file pointcloud_to_laserscan.yaml   -r cloud_in:=/baal/lidar_points   -r scan:=/scan"&
xterm -e bash -ic  "ros2 launch pointlio_tf_bridge pointlio_tf_bridge.launch.py use_sim_time:=true; bash"&




