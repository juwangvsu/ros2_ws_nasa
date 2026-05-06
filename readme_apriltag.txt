sudo apt install ros-${ROS_DISTRO}-camera-calibration


---------5/6/26 ./start_apriltaggazebo.sh ------
updated with depth cloud, see realsense section

---------5/3/26 ./start_apriltaggazebo.sh ------
turtlebot3_waffle:
	model.sdf
	modified camera facing back, camera type change to depth
	now publish both
		/camera/image_raw
		/camera/points
turtlebot3_world.launch.py
	robot init pose (1,3) facing y-axis
./turtlebot3_gazebo/urdf/turtlebot3_waffle.urdf
	camera_joint modify


fiducial_tb3_gazebo_demo:
	publish static tf from base_footprint-> ...> camera_rgb_frame
gazebo launch:
	also publish base_footprint->... camera_rgb_frame, from urdf file.
	this seems overrule static tf from fiducial launch file. 
	the duplicate is ok but need to be consistent.

apriltag detection tf need to publish tf w.r.t camera link, not base_footprint
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

-------------------------caliberate------------
ros2 run v4l2_camera v4l2_camera_node --ros-args   -r image_raw:=/camera/image_raw   -r camera_info:=/camera/camera_info   -p camera_frame_id:=camera_rgb_optical_frame
ros2 run camera_calibration cameracalibrator   --size 7x5   --square 0.025 --ros-args --remap  image:=/camera/image_raw --remap camera:=/camera


tagsize:
  large  21 cm
  small 16 cma

walli tag detected:
  2.4 m

###################################### realsense section #################3
# Register the Intel server    
sudo mkdir -p /etc/apt/keyrings    
curl -sSf https://librealsense.intel.com/Debian/librealsense.pgp | sudo tee /etc
echo "deb [signed-by=/etc/apt/keyrings/librealsense.pgp] https://librealsense.in
    
# Install the SDK    
sudo apt update    
sudo apt install librealsense2-dkms librealsense2-utils librealsense2-dev librea
    
install:    
  sudo apt install ros-$ROS_DISTRO-realsense2-camera    
    
launch camera:    
  ros2 launch realsense2_camera rs_launch.py    
    
launch with point cloud:    
  ros2 launch realsense2_camera rs_launch.py pointcloud.enable:=true device_type
    
topic:    
  /camera/camera/depth/color/pointsa    
  frameid    
camera_depth_optical_frame    
    
----------------5/6/26 depth cloud to scan---------------------------    
pointcloud_to_laserscan_logged_node_depthcloud    
  cloud-> /scan2    
    cloud assume in camera_rgb_optical_frame    
    scan publish in camera_rgb_frame    
    add to slam? or just costmap?    
    skip entire frame if not level enough by lookup odom->base_link tf?    
    preprocess depthcloud remove floor points?    
    downsample needed if too heavy?    
    
gazebo:    
  ./start_apriltaggazebo.sh    
    gazebo camera type depth, resolution not too high    
real:    
  ./start_apriltagreal.sh    

