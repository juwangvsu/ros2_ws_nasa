#!/bin/bash
#this script send a go message intended for the starting slam map building after the fudicial apriltag pose estimate is done
gnome-terminal -x  $SHELL -ic "ros2 launch fiducial_tb3_gazebo_demo sim_mapping_anchor.launch.py use_sim_time:=true;bash"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ./start_nasa_go.sh; bash"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ./start_nasa_teleop.sh"
gnome-terminal -x  $SHELL -ic "rviz2"
gnome-terminal -x  $SHELL -ic "ctt nav2; ros2 launch nav2_bringup navigation_launch.py params_file:=nav2_pointlio.yaml use_sim_time:=true ;bash"
#gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id base_link --child-frame-id base_scan --ros-args -p use_sim_time:=true; bash"

# issue and fix: static tf also need use_sim_time:=true, otherwise base_link tf error, 
#	with tf issue fixed, goal move still not work if rviz using global frame. but if set frame to map, nav2 works.
# 	not fixed, must map->odom->base_link->base_scan in a chain
# disable various node in /sim_mapping_anchor.launch.py to see which one messup base_link to base_scan tf lookup. could be gazebo of other heavy node make message missing? 
