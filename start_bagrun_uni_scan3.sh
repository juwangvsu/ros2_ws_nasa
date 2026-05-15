#!/bin/bash
#bag play unitree lidar cloud frame_id remapped
# 5/10/26 diff ./start_bagrun_uni.sh:  scan merge node, scan3 
# 5/8/26 add scan2 and use scan3 for mapping 
# 5/2/26 now start_bagrun_uni.sh show local_plan and plan after give a goal

# ./start_bagrun_uni.sh ~/rosbag2_2026_03_25-18_31_53 True True
#							rviz fakescan
gnome-terminal -x  $SHELL -ic "cd ~/; ros2 bag play $1 --topics /unilidar/cloud /unilidar/imu /camera/camera_info /camera/image_raw /camera/camera/depth/color/points --remap /unilidar/cloud:=/unilidar/cloud --clock -r 0.2; bash"
#gnome-terminal -x  $SHELL -ic "python3 change_frame.py; bash"
#gnome-terminal -x  $SHELL -ic "python3 ceiling_filter.py --ros-args -p ceiling_z:=2.0; bash"
gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id baal/imu_initial --child-frame-id baal/imu  --ros-args -p use_sim_time:=true; bash"
gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id baal/imu --child-frame-id baal/base  --ros-args -p use_sim_time:=true; bash"
#gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id base_link --child-frame-id base_footprint  --ros-args -p use_sim_time:=true; bash"

gnome-terminal -x  $SHELL -ic "ros2 launch point_lio mapping_unilidar_l2.launch.py rviz:=$2 use_sim_time:=true; bash" # ws_pointlio/src/point_lio_ros2/config/unilidar_l2.yaml blind=1.0

gnome-terminal -x  $SHELL -ic "rviz2 -d ws_pointlio/src/pointlio_tf_bridge/scan.rviz  --ros-args -p use_sim_time:=true; bash"
#gnome-terminal -x  $SHELL -ic "ros2 run pointcloud_to_laserscan_logged pointcloud_to_laserscan_logged_node_rock  --ros-args   --params-file pointcloud_to_laserscan_unitree_logged.yaml   -r cloud_in:=/unilidar/cloud   -r scan:=/scan"
gnome-terminal -x  $SHELL -ic "ros2 run pointcloud_to_laserscan_logged pointcloud_to_laserscan_logged_node  --ros-args   --params-file pointcloud_to_laserscan_unitree_logged.yaml -p use_sim_time:=true  -r cloud_in:=/unilidar/cloud   -r scan:=/scan" # generate /scan range_min: 1.0 max_height: 2.0

gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ros2 run laser_filters scan_to_scan_filter_chain --ros-args --params-file scan_filter.yaml -r scan:=/scan3 -r scan_filtered:=/scan_filtered" # max_height=2 if too high ceiling points in scan. /scan3 -> /scan_filtered
#fake scan2 and scan+scan2->scan3

gnome-terminal -x  $SHELL -ic "ros2 run ira_laser_tools laserscan_multi_merger   --ros-args  -r __node:=laserscan_multi_merger --params-file laser_merger.yaml"
if [ "$3" = "True" ]; then
        echo "fake scan2"
        gnome-terminal -x  $SHELL -ic "ros2 run fake_scan2_publisher fake_scan2_node"
else
        echo "no fake scan2"
fi

gnome-terminal -x  $SHELL -ic "ros2 launch pointlio_tf_bridge pointlio_tf_bridge_winit.launch.py use_sim_time:=true static_pitch:=0.0 static_yaw:=-2.53 bridge_params_file:=bridge.yaml; bash" # 15 deg 0.26, 20 deg 0.348 , 30 deg 0.52 base_link -> baal/imu_initial cmdline param overwriten by bridge.yaml base_link to baal/imu_initial to correct the tf from point_lio
#gnome-terminal -x  $SHELL -ic "ros2 launch pointlio_tf_bridge pointlio_tf_bridge.launch.py use_sim_time:=true static_pitch:=0.0 static_yaw:=-2.53 bridge_params_file:=bridge.yaml; bash" # 15 deg 0.26, 20 deg 0.348 , 30 deg 0.52 base_link -> baal/imu_initial cmdline param overwriten by bridge.yaml base_link to baal/imu_initial to correct the tf from point_lio

gnome-terminal -x  $SHELL -ic "ros2 launch slam_toolbox online_async_launch.py   slam_params_file:=slam_async_pointlio.yaml use_sim_time:=true; bash" # use /scan_filtered
gnome-terminal -x  $SHELL -ic "ros2 launch nav2_bringup navigation_launch.py   use_sim_time:=true params_file:=nav2_pointlio.yaml;bash" # use /scan_filtered

