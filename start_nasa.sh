#!/bin/bash
gnome-terminal -x  $SHELL -ic "ros2 launch unitree_lidar_ros2 launch.py cloud_topic:=/unilidar/cloud; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch point_lio mapping_unilidar_l2.launch.py rviz:=False; bash"

