#!/bin/bash
gnome-terminal -x  $SHELL -ic "ros2 launch unitree_lidar_ros2 launch.py; bash"
gnome-terminal -x  $SHELL -ic "ros2 launch point_lio mapping_unilidar_l2.launch.py; bash"

