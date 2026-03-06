#!/bin/bash
gnome-terminal -x  $SHELL -ic "ros2 bag play msbuild/ --clock"
gnome-terminal -x  $SHELL -ic "ros2 launch point_lio mapping_velody16.launch.py use_sim_time:=true; bash"

