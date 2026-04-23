sudo apt install ros-${ROS_DISTRO}-camera-calibration

--------------------------
debug real:

ros2 run v4l2_camera v4l2_camera_node --ros-args     -r image_raw:=/camera/image_raw     -r camera_info:=/camera/camera_info     -p camera_info_url:='file:///home/robot/.ros/camera_info/my_camera.yaml'     -p image_size:='[640,480]'     -p output_encoding:='mono8' -p camera_frame_id:='camera_rgb_optical_frame'    -p qos_overrides./camera/image_raw.publisher.reliability:=reliable     -p qos_overrides./camera/camera_info.publisher.reliability:=reliable

ros2 run apriltag_ros apriltag_node --ros-args   -r image_rect:=/camera/image_raw   -r camera_info:=/camera/camera_info -r use_sim_time:=True --params-file ~/ros2_ws_nasa/ws_pointlio/src/fiducial_tb3_gazebo_demo/config/apriltag.yaml 

	rviz2 tf should show tag_0 xyz position updating
ros2 topic echo /detections 

apriltag_node tips:
	image_raw frame_id must match with camera driver published image
	tag size specified via a yaml file
	publish /tf for tag's 3d pose if succeful, publish detectons. detection does not have 3d pose
