#!/bin/bash
#this script send a go message intended for the starting slam map building after the fudicial apriltag pose estimate is done

# ./start_apriltagreal.sh True
#			  true to also run rviz, slam, nav2
# (1) v4l2 (2)  fiducial (3) slam (4) nav2 (5) go (6) xbox tele (7) realsense (8) pointcloud_to_laserscan_logged_node_depthcloud
# (3) (4) should be commented off, since start_nasa_full2.sh get these

echo " ./start_apriltagreal.sh True|False true to run slam and nav2"
LOGI_DEV=$(v4l2-ctl --list-devices | grep -A 1 "C920" | grep -o '/dev/video[0-9]\+' | head -n 1)
if [ -z "$LOGI_DEV" ]; then
    #LOGI_DEV="/dev/video0"
    echo "Error: Logitech C920 not found."

fi

echo "Found Logitech C920 at: $LOGI_DEV"
# /dev/video0

#v4l2-ctl -d "$LOGI_DEV" --list-ctrls

gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; conda deactivate; v4l2-ctl -d $LOGI_DEV --set-parm=10; sleep 3; ros2 run v4l2_camera v4l2_camera_node --ros-args     -r image_raw:=/camera/image_raw     -r camera_info:=/camera/camera_info  -p video_device:=$LOGI_DEV   -p camera_info_url:='file://$(pwd)/camera_info/my_camera.yaml'     -p image_size:='[640,480]'     -p output_encoding:='mono8'  -p camera_frame_id:='camera_rgb_optical_frame'   -p qos_overrides./camera/image_raw.publisher.reliability:=reliable     -p qos_overrides./camera/camera_info.publisher.reliability:=reliable "

#global anchor (default global->map tf in scan time too), apriltag node, tf_repub2 (tag_0_map tf in scan time so we can see in map frame) 
gnome-terminal -x  $SHELL -ic "conda deactivate; ros2 launch fiducial_tb3_gazebo_demo sim_mapping_anchor.launch.py apriltag_cfg:=apriltag_20.yaml;bash"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; python3 tf_repub2.py"

if [ "$1" = "True" ]; then
	gnome-terminal -x  $SHELL -ic "conda deactivate; ros2 launch slam_toolbox online_async_launch.py "
	gnome-terminal -x  $SHELL -ic "conda deactivate; cd ~/ros2_ws_nasa; ros2 launch nav2_bringup navigation_launch.py params_file:=apriltagnav2_params.yaml"
else
	echo "run slam and nav bag is not true"
fi

#start realsense node and tf and cloud_to_scan2
gnome-terminal -x  $SHELL -ic "ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 3.14 --frame-id base_link --child-frame-id camera_link ; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch realsense2_camera rs_launch.py pointcloud.enable:=true device_type:=d455 align_depth.enable:=true"
gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; ros2 run pointcloud_to_laserscan_logged pointcloud_to_laserscan_logged_node_depthcloud  --ros-args   --params-file pointcloud_to_laserscan_camcloud_realsense.yaml -r __node:=pointcloud_to_laser_scan2 " 


gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; sleep 10; ros2 topic pub /usercmd std_msgs/msg/String '{'data': 'go'}' -t 5; bash"
#gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa;  ros2 launch teleop_twist_joy teleop-launch.py joy_config:='xbox'"


# issue and fix: static tf also need use_sim_time:=true, otherwise base_link tf error, 
#	with tf issue fixed, goal move still not work if rviz using global frame. but if set frame to map, nav2 works.
# 	not fixed, must map->odom->base_link->base_scan in a chain
# disable various node in /sim_mapping_anchor.launch.py to see which one messup base_link to base_scan tf lookup. could be gazebo of other heavy node make message missing? 
#	nav2 warning missing base_scan tf if cpu heavy load, this is confirmed. if comment off fiducial launch, mainly apriltag_node,
#	no tf missing issue.
#	if gazebo running in software rendering, also cause problem. tb3_model.sdf update_rate=10 fixed much of cpu load issue

