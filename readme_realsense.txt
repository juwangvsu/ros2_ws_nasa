# Register the Intel server
sudo mkdir -p /etc/apt/keyrings
curl -sSf https://librealsense.intel.com/Debian/librealsense.pgp | sudo tee /etc/apt/keyrings/librealsense.pgp > /dev/null
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

----------------depth cloud to scan---------------------------
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

