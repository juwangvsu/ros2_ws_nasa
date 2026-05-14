ps aux | grep laserM | grep -v grep | awk "{print \$2}" | xargs kill -9
ros2 launch point_lio mapping_unilidar_l2.launch.py rviz:=False
