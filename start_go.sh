#!/bin/bash

# this script send 'go' to start autonomous run
#    it got picked up by start_apriltagreal.sh
#	it get picked up by mission_node.py

gnome-terminal -x  $SHELL -ic "cd ~/ros2_ws_nasa; export ROS_DOMAIN_ID=3; sleep 10; ros2 topic pub /usercmd std_msgs/msg/String '{'data': 'go'}' -t 5; bash"

