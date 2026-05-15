#!/bin/bash

# Check if exactly 3 arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <frame_id> <x> <y>  "
    echo "Usage:  <frame_id> map or global, use map mostly  "
    echo "Usage:  x y are alway global target position, if right arena, flip x and y value"
    echo "Example for left arena: $0 map 5 2.0"
    echo "Example for right arena: $0 map 2 5.0"
    exit 1
fi

# Assign arguments to variables
FRAME_ID=$1
X=$2
Y=$3

echo "Publishing goal pose to /goal_pose..."
echo "Frame: $FRAME_ID, X: $X, Y: $Y"
cd ~/ros2_ws_nasa

# The --once flag sends the message then exits
python3 goal_pose.py --x $X --y $Y --yaw 1.57 --frame-id $FRAME_ID

