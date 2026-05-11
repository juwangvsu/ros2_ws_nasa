#!/bin/bash

# Check if exactly 3 arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <frame_id> <x> <y>"
    echo "Example: $0 map 1.5 2.0"
    exit 1
fi

# Assign arguments to variables
FRAME_ID=$1
X=$2
Y=$3

echo "Publishing goal pose to /goal_pose..."
echo "Frame: $FRAME_ID, X: $X, Y: $Y"

# Execute the ROS 2 publication
# The --once flag sends the message then exits
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped "{
  header: {
    stamp: {sec: 0, nanosec: 0},
    frame_id: '$FRAME_ID'
  },
  pose: {
    position: {x: $X, y: $Y, z: 0.0},
    orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
  }
}"
