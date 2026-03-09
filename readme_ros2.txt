ros2 launch webots_ros2_universal_robot single_launch.py 
ros2 topic echo /ur5e/ur_joint_trajectory_controller/joint_trajectory
cd /opt/ros/humble/share/webots_ros2_universal_robot

----  build note --------------
cd unilidar_sdk2/unitree_lidar_ros2/; colcon build
cd ws_pointlio/; 
	colcon build
	colcon build --symlink-install
source ws_pointlio/install/setup.bash

----------3/7/26/ ros2 point_lio docker --------------------
hptitan22:
docker exec -it ros2_ws bash
export DISPLAY=:0
./start_bagrun_docker.sh

----------3/7/26/ ros2 point_lio - --------------------
panda2
msbuild sim test
global map:
  PCD/scans.pcd, 415712 pts
  /Laser_map
ros2 topic echo /Laser_map --full-length > lasermsg.txt

----------3/6/26/ ros2 nasa robotic- --------------------
ros2 run tf2_tools view_frames
/laserMapping:
  camera_init
  aft_mapped

ros2 run tf2_ros tf2_echo camera_init aft_mapped
ros2 topic echo 
topics ok:
/path
  published relative slow
  frame_id:camera_init
/cloud_registered
  frame_id:camera_init
  
topics no messgage :
  /Laser_map
  /Odometry
  /cloud_effected
  /cloud_registered_body
     frame_id: body
      scan_bodyframe_pub_en: true 

/transform_listener_impl_562dcb38d300

start_bagrun.sh
start_nasa.sh


----------3/1/26/ ros2 nasa robotic- --------------------
chatgpt: nasa robot
https://github.com/juwangvsu/ros2_ws_nasa.git
docker pull jwang3vsu/ros-humble-ros1-bridge-builder
cd ros2_ws; docker run -t -d --restart always -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v $PWD:/workspace -v /data:/data -w /workspace --net host --name ros2_ws jwang3vsu/ros-humble-ros1-bridge-builder:latest bash

alien3, hptitan ros2_ws (docker)
	host ~/ros2_ws -> /workspace/ros2_ws
docker apt pkgs:
	apt update
	apt install ros-humble-pcl-ros ros-humble-pcl-conversions ros-humble-visualization-msgs
	python3 -m pip install --user rosbags
	apt install ros-humble-rosbag2-storage-default-plugins

unitree repo:
	git clone https://github.com/unitreerobotics/unilidar_sdk2.git
	cd /workspace/unilidar_sdk2/unitree_lidar_ros2#
	colcon build --symlink-install
	source install/setup.bash

Point-LIO-ROS2 (Unilidar L1/L2 supported)
	mkdir -p ws_pointlio/src
	cd ws_pointlio/src
	git clone https://github.com/dfloreaa/point_lio_ros2.git
	edit .yaml under config/ and set lid_topic, imu_topic
	cd ws_pointlio
	colcon build --symlink-install
	source install/setup.bash

bag file:
	/tmp/test2_2022-08-01-17-29-29.bag   ros1 bag file
	/tmp/msbuild/	
		converted to ros2 format, only convert two topics. converting all topics resulting format error when play
		/tmp# ~/.local/bin/rosbags-convert --src test2_2022-08-01-17-29-29.bag --dst msbuild --include-topic /baal/imu/data /baal/lidar_points

		/tmp/msbuild# mv msbuild.db3 msbuild_0.db3
		/tmp# ros2 bag reindex msbuild/
		/media/student/datar/msbuild_ros2.bag	backup of converted, onedrive

test: (in docker)
	
	DISPLAY=:1
	ros2 bag play msbuild/ --clock
	root@alien3:/workspace/ws_pointlio# source install/setup.bash
		ros2 launch point_lio mapping_velody16.launch.py use_sim_time:=true
			work well, tf published, 
		ros2 launch point_lio mapping_unilidar_l2.launch.py
			slow map and path update, due to lidar type mismatch

	pcl_viewer ros2_ws_nasa/ws_pointlio/src/point_lio_ros2/PCD/scans_30.pcd

 
----------6/26/25 ros2 python- --------------------
 ros2 default use system python3
 /usr/bin/python3.10

how to use pyenv's environment for ros2 python? good reason for not doing that?


------------4/18/25 docker ros2 comm with host ros2 issue ------------
https://chatgpt.com/c/6802c765-07e0-800c-8031-85b16f639e4c
tested on ws2
issue:
	 ROS 2 DDS middleware configuration issues,
	the container is launched with --net=host, but the topic I published at host is not getting through to the container
fix:
	inside docker container: 
		ros:humble (x86-64) 
		ros:humble-perception-jammy (arm64 v8)
		rm /var/lib/apt/lists/*ros*
		 apt update --allow-insecure-repositories
		apt install ros-humble-rmw-cyclonedds-cpp
	docker exec -it -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp ros1b bash
		export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

to be tested on pi

---------------4/13/25 ros2 docker kdl pxtt ---------------------
tang/VisionRobot/nv8arm/foxy/nv6_ws
	docker run -t -d --restart always -v $PWD:/workspace -v /data:/data -w /workspace --net host --name ros1b jwang3vsu/ros-humble-ros1-bridge-builder:latest bash

-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro

cd ~/ros2_ws
	docker run -t -d --restart always -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v $PWD:/workspace -v /data:/data -w /workspace --net host --name ros2_ws jwang3vsu/ros-humble-ros1-bridge-builder:latest bash
	must run from X11 env to use display. run from ssh terminal will not have display setup.

docker exec -it ros1b bash  


----------------3/8/25 ros2 ros1_bridge --------------
https://github.com/TommyChangUMD/ros-humble-ros1-bridge-builder/
	same machine:
		run ros1 docker, run roscore insdie
		run ros1_bridge @ host

note: ros1_bridge build inside a docker image and copied to host machine, but
	run on host machine.

note: tbt ros1 one another machine, 
---FAQ-------------
colcon:
	apt install ros-dev-tools
