#!/bin/bash
#this script send a go message intended for the starting slam map building after the fudicial apriltag pose estimate is done
gnome-terminal -x  $SHELL -ic "sleep 10; ros2 topic pub /usercmd std_msgs/msg/String '{'data': 'go'}' -t 5; bash"

