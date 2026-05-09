sudo apt install ros-${ROS_DISTRO}-camera-calibration

---------5/8/26 realsense pointcloud to scan ----------------
test:

	ros2 run pointcloud_to_laserscan_logged pointcloud_to_laserscan_logged_node_depthcloud  --ros-args   --params-file pointcloud_to_laserscan_camcloud_realsense.yaml -r __node:=pointcloud_to_laser_scan2
	ros2 bag play bag26/ --clock --topics /camera/camera/depth/color/points /tf /tf_static /camera/camera/color/image_raw

rviz2: 
	in base_link frame, the /camera/camera/depth/color/points and /scan2 should lineup

note:
	pointcloud_to_laserscan_camcloud_realsense.yaml
	point cloud in optical_frame, published scan2 should be in rgb_frame
	in cpp node, 180 deg yaw was added as a dirty hack, to count for the upside down layout of the realsense camera.

	pointcloud_to_laserscan_camcloud_realsense.yaml
	for gazebo tb3 sim, not regress test yet

---------5/6/26 ./start_apriltagreal.sh ------
updated with depth cloud, see realsense section

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

tf:
fiducial_tb3_gazebo_demo:
	global_anchor_node.py 
		publish global->map tf 
		assume two tags observed, assume map->base->camera_rgb_frame tf
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
/apt/keyrings/librealsense.pgp > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/librealsense.pgp] https://librealsense.intel.com/Debian/apt-repo `lsb_release -cs` main" | sudo tee /etc/apt/local.sources.d/realsense.sources
    
# Install the SDK    
sudo apt update   
sudo apt install librealsense2-dkms librealsense2-utils librealsense2-dev librealsense2-dbg 
    
install:    
  sudo apt install ros-$ROS_DISTRO-realsense2-camera    
    
launch camera:    
  ros2 launch realsense2_camera rs_launch.py    
    
launch with point cloud:    
  ros2 launch realsense2_camera rs_launch.py pointcloud.enable:=true device_type:=d455 align_depth.enable:=true
    
topic:    
  /camera/camera/depth/color/pointsa    
  frameid    
camera_depth_optical_frame    
 
--------------5/8/26 start_apriltagreal.sh ---
pointcloud_to_laserscan_logged_node_depthcloud:
  for realsense (diff from gazebo)
      input_topic: /camera/camera/depth/color/points
      output_topic: /scan2

  _sub don't use qos
  now use param file for config
  /scan2 data show up, need to verify about frame_id and data nature

--------------5/7/26 realsense l515 hack -----------
hpzlaptop:
	same usb port may choose usb2 or usb3 depending on cable used.
		both usb2 and usb3 is ok with rebuild sdk.	
	l515 stock driver and ros package dont work
	rebuild source both the sdk and ros package

sudo apt remove ros-humble-realsense2-* ros-humble-librealsense2 
sudo apt remove librealsense2 librealsense2-dev librealsense2-utils librealsense2-dkms librealsense2-udev-rules
sudo apt autoremove

/media/student/ttt/librealsense (sdk)
	23b0904ba126e87327bc2908c1a5f79342eae867 commit
	git checkout v2.53.1
	mkdir build && cd build
	cmake .. -DBUILD_EXAMPLES=true -DBUILD_GRAPHICAL_EXAMPLES=true -DFORCE_RSUSB_BACKEND=true
	make -j$(nproc)
	sudo make install

	cd /media/student/ttt/librealsense
	sudo ./scripts/setup_udev_rules.sh
	sudo udevadm control --reload-rules
	sudo udevadm trigger
/media/student/ttt/ros2_ws2/src/realsense-ros
	2a65533ee7431bdc05fe5744798efc7f5713f866 commit
	colcon build \
  --packages-select realsense2_camera realsense2_camera_msgs \
  --cmake-clean-cache \
  --cmake-args \
    -DCMAKE_PREFIX_PATH=/usr/local \
    -Drealsense2_DIR=/usr/local/lib/cmake/realsense2

test:
	LIBRS_FORCE_RSUSB_BACKEND=1 ros2 run realsense2_camera realsense2_camera_node --ros-args   -p enable_depth:=true   -p enable_color:=true   -p pointcloud.enable:=true   -p pointcloud.stream_filter:=2   -p pointcloud.stream_index_filter:=0   -p align_depth.enable:=true

	    
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

