robot (panda2 or 5):
ros2 run v4l2_camera v4l2_camera_node --ros-args   -p video_device:=/dev/video0   -r /image_raw:=/camera/image_raw

laptop (panda6):
conda activate deepseg
ros2 launch deeplab_segmentation_ros2 segmentation.launch.py config_file:=src/deeplab_segmentation_ros2/config/segmentation_params.yaml

ros2 topic echo /segmentation/mask --once --full-length> rst.txt

mask and obstacle_mask are mono image, overlay is rgb image
mask pixel value is the straight from pred, classification value 0-20. so rqt_image_view show all dark color.
obstacle_mask change all non background obstcle point to 255.

ros2 topic echo dropping msg:
  sudo apt update && sudo apt install ros-$ROS_DISTRO-rmw-cyclonedds-cpp
  export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
  ros2 topic echo /imu/data --qos-reliability best_effort
