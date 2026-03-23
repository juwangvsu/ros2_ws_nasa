#!/bin/bash
gnome-terminal -x  $SHELL -ic " ros2 launch teleop_twist_joy teleop-launch.py joy_config:='xbox'
; bash"

