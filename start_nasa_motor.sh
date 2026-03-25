#!/bin/bash
# motor driver only
gnome-terminal -x  $SHELL -ic " ros2 launch mdds30_serial_driver mdds30.launch.py; bash" 

