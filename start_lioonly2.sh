#!/bin/bash

# Define how many times you want the loop to run
ITERATIONS=15
python3 stoprobot_2sec.py > /dev/null 2>&1 &
for ((i=1; i<=$ITERATIONS; i++))
do
    echo "--- Iteration $i of $ITERATIONS ---"

    cd ~/ros2_ws_nasa; python3 publish_current_odominit_exit.py
    # 1. Kill existing laserM processes
    # We use -r in xargs to prevent it from running if the grep comes up empty
    echo "Cleaning up old laserM processes..."
    ps aux | grep laserM | grep -v grep | awk '{print $2}' | xargs -r kill -9

    sleep 5 
    # 2. Launch ROS2 in the background
    # '&' at the end sends it to the background
    echo "Launching point_lio..."
    ros2 launch point_lio mapping_unilidar_l2.launch.py rviz:=False > /dev/null 2>&1 &

    # 3. Sleep for 8 seconds
    echo "Waiting 15 seconds..."
    sleep 15
done

echo "Loop completed."
