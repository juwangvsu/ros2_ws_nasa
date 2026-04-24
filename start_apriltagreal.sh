#!/bin/bash
#this script send a go message intended for the starting slam map building after the fudicial apriltag pose estimate is done
gnome-terminal -x  $SHELL -ic "conda deactivate; v4l2-ctl -d /dev/video0 --set-parm=10; sleep 3; ros2 run v4l2_camera v4l2_camera_node --ros-args     -r image_raw:=/camera/image_raw     -r camera_info:=/camera/camera_info     -p camera_info_url:='file:///home/robot/.ros/camera_info/my_camera.yaml'     -p image_size:='[640,480]'     -p output_encoding:='mono8'  -p camera_frame_id:='camera_rgb_optical_frame'   -p qos_overrides./camera/image_raw.publisher.reliability:=reliable     -p qos_overrides./camera/camera_info.publisher.reliability:=reliable "
gnome-terminal -x  $SHELL -ic "conda deactivate; ros2 launch fiducial_tb3_gazebo_demo sim_mapping_anchor.launch.py ;bash"
gnome-terminal -x  $SHELL -ic "conda deactivate; ros2 launch slam_toolbox online_async_launch.py "
gnome-terminal -x  $SHELL -ic "conda deactivate; rviz2 "
gnome-terminal -x  $SHELL -ic "conda deactivate; cd ~/ros2_ws_nasa; ros2 launch nav2_bringup navigation_launch.py params_file:=apriltagnav2_params.yaml"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; sleep 10; ros2 topic pub /usercmd std_msgs/msg/String '{'data': 'go'}' -t 5; bash"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa;  ros2 launch teleop_twist_joy teleop-launch.py joy_config:='xbox'"
#gnome-terminal -x  $SHELL -ic "ctt nav2; ros2 launch nav2_bringup navigation_launch.py params_file:=nav2_pointlio.yaml use_sim_time:=true ;bash"


# issue and fix: static tf also need use_sim_time:=true, otherwise base_link tf error, 
#	with tf issue fixed, goal move still not work if rviz using global frame. but if set frame to map, nav2 works.
# 	not fixed, must map->odom->base_link->base_scan in a chain
# disable various node in /sim_mapping_anchor.launch.py to see which one messup base_link to base_scan tf lookup. could be gazebo of other heavy node make message missing? 
#	nav2 warning missing base_scan tf if cpu heavy load, this is confirmed. if comment off fiducial launch, mainly apriltag_node,
#	no tf missing issue.
#	if gazebo running in software rendering, also cause problem. tb3_model.sdf update_rate=10 fixed much of cpu load issue

