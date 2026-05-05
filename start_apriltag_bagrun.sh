#!/bin/bash
#this script send a go message intended for the starting slam map building after the fudicial apriltag pose estimate is done

# start_apriltag_bagrun.sh ~/bag23_113 false false
#					play bag, run slam and nav

# (1) fiducial node (2) bagrun (3) slam (4) rviz2 (5) nav2 (6) go (7) xbox tele

gnome-terminal -x  $SHELL -ic "conda deactivate;  ros2 launch fiducial_tb3_gazebo_demo sim_mapping_anchor.launch.py use_sim_time:=true apriltag_cfg:=apriltag_30.yaml; bash"

if [ "$2" = "true" ]; then
	gnome-terminal -x  $SHELL -ic "cd ~/;  ros2 bag play $1 --topics /unilidar/cloud /unilidar/imu /camera/camera_info /camera/image_raw --remap /unilidar/cloud:=/unilidar/cloud --clock -r 0.2; bash"
    echo "play bag is true"
else
    echo "play bag is not true"
fi

if [ "$3" = "true" ]; then
	gnome-terminal -x  $SHELL -ic "conda deactivate;  ros2 launch slam_toolbox online_async_launch.py use_sim_time:=True"
	gnome-terminal -x  $SHELL -ic "conda deactivate;  cd ~/ros2_ws_nasa; ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true params_file:=apriltagnav2_params.yaml"
else
    echo "run slam and nav bag is not true"
fi
gnome-terminal -x  $SHELL -ic "conda deactivate; rviz2 --ros-args -p use_sim_time:=true"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa;  sleep 10; ros2 topic pub /usercmd std_msgs/msg/String '{'data': 'go'}' -t 5; bash"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa;  ros2 launch teleop_twist_joy teleop-launch.py joy_config:='xbox'"


# issue and fix: static tf also need use_sim_time:=true, otherwise base_link tf error, 
#	with tf issue fixed, goal move still not work if rviz using global frame. but if set frame to map, nav2 works.
# 	not fixed, must map->odom->base_link->base_scan in a chain
# disable various node in /sim_mapping_anchor.launch.py to see which one messup base_link to base_scan tf lookup. could be gazebo of other heavy node make message missing? 
#	nav2 warning missing base_scan tf if cpu heavy load, this is confirmed. if comment off fiducial launch, mainly apriltag_node,
#	no tf missing issue.
#	if gazebo running in software rendering, also cause problem. tb3_model.sdf update_rate=10 fixed much of cpu load issue

