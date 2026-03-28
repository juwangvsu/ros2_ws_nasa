#!/bin/bash
# motor driver only
gnome-terminal -x  $SHELL -ic "ros2 launch sabertooth_2x32_serial_twist sabertooth_twist.launch.py   params_file:=sabertooth_twist.yaml; bash" 

