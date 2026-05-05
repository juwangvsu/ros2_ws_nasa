ros2 run apriltag_ros apriltag_node --ros-args \
    -r image_rect:=/camera/image_raw \
    -r camera_info:=/camera_info
