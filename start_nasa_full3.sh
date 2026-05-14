#!/bin/bash
# debug slam crash, 
# ./start_nasa_full2.sh True True
#			rviz fakescan2
# ./start_nasa_full2.sh False False
#       $1 True to show pointlio rviz
#	$2 True to run fakescan2

gnome-terminal -x  $SHELL -ic "ros2 launch unitree_lidar_ros2 launch.py cloud_topic:=/unilidar/cloud ; bash"
gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id baal/imu_initial --child-frame-id baal/imu ; bash"
gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id baal/imu --child-frame-id baal/base; bash"

gnome-terminal -x  $SHELL -ic "ros2 launch point_lio mapping_unilidar_l2.launch.py rviz:=$1; bash"
#gnome-terminal -x  $SHELL -ic "python3 change_frame.py; bash"

gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; rviz2 -d ws_pointlio/src/pointlio_tf_bridge/scan.rviz; bash"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ros2 run pointcloud_to_laserscan_logged pointcloud_to_laserscan_logged_node  --ros-args   --params-file pointcloud_to_laserscan_unitree_logged.yaml   -r cloud_in:=/unilidar/cloud   -r scan:=/scan"
gnome-terminal -x  $SHELL -ic "ros2 run laser_filters scan_to_scan_filter_chain --ros-args --params-file scan_filter.yaml -r scan:=/scan3 -r scan_filtered:=/scan_filtered"

#fake scan2 and scan+scan2->scan3

gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; sleep 5; ros2 run ira_laser_tools laserscan_multi_merger   --ros-args  -r __node:=laserscan_multi_merger --params-file laser_merger.yaml"
if [ "$2" = "True" ]; then
	echo "fake scan2"
	gnome-terminal -x  $SHELL -ic "ros2 run fake_scan2_publisher fake_scan2_node"
else
	echo "no fake scan2"
fi


#5/10/26 copied from start_bagrun_uni_scan3.sh, tb tested... launch file diff in loading param file or not
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ros2 launch pointlio_tf_bridge pointlio_tf_bridge_winit.launch.py use_sim_time:=false static_pitch:=0.0 static_yaw:=-2.53 bridge_params_file:=bridge.yaml; bash" # 15 deg 0.26, 20 deg 0.348 , 30 deg 0.52 base_link -> baal/imu_initial cmdline param overwriten by bridge.yaml base_link to baal/imu_initial to correct the tf from point_lio
#gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ros2 launch pointlio_tf_bridge pointlio_tf_bridge_uni.launch.py static_pitch:=0.0 static_yaw:=3.14 rate:=10.0; bash" 
#default rate 50, low to 10 help something? base_link -> baal/imu_initial lidar face robot back so 3.14 yaw, if flat pitch is 0

gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ros2 launch slam_toolbox online_async_launch.py   slam_params_file:=slam_async_pointlio.yaml use_sim_time:=false; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch nav2_bringup navigation_launch.py   params_file:=nav2_pointlio.yaml;bash"
#gnome-terminal -x  $SHELL -ic " ros2 launch mdds30_serial_driver mdds30.launch.py; bash" 

