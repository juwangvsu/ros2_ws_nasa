ros2 launch webots_ros2_universal_robot single_launch.py 
ros2 topic echo /ur5e/ur_joint_trajectory_controller/joint_trajectory
cd /opt/ros/humble/share/webots_ros2_universal_robot

------wired ip addr, login, pass ---------------
panda 192.168.1.5 robot, vsu@2026
pi    192.168.1.4 vsu, vsu@2026
alienserver 192.168.1.7 vsu, vsu@2026
lidar   192.168.1.62

----  build note --------------
(if ros2 key issue, check FAQ 3/24/26)
sudo apt install ros-humble-pointcloud-to-laserscan
sudo apt install -y ros-humble-slam-toolbox --allow-unauthenticated
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
sudo apt install ros-humble-pcl-ros ros-humble-pcl-conversions ros-humble-visualization-msgs
python3 -m pip install --user rosbags
sudo apt install ros-humble-rosbag2-storage-default-plugins

-------------------------------------------------------
hplaptop
chatgpt:
	https://chatgpt.com/g/g-p-69a50c866d248191a5290b56b1f044d0/c/69e2edce-abd8-832e-a353-85512fd463de
4/17/26: apriltag:
	sudo apt install   ros-humble-ros-gz-sim   ros-humble-ros-gz-bridge   ros-humble-tf-transformations ros-humble-apriltag-ros
	sudo apt install ros-humble-image-proc
cd unilidar_sdk2/unitree_lidar_ros2/; colcon build
  (unilidar_sdk2 binary optional)
cd ws_pointlio/; 
	colcon build
	colcon build --symlink-install
source ws_pointlio/install/setup.bash

gazebo sim:
	ros2 launch fiducial_tb3_gazebo_demo sim_mapping_anchor.launch.py

./humble/share/turtlebot3_gazebo/models/turtlebot3_waffle/model.sdf
	lidar range change

status:
	rviz 3 apriltags show at high z. check apriltag node tf part
 
-----3/28/26 point_lio test bag7_egr hm20ea -----------------
result is good

-----3/27/26 datasets -----------------
bag6_systimefalse
bag7_egr/
bag6_systimefalse/
bag4_panda/

msbuild
hm20ea
-----3/27/26 start_bagrun_uni.sh bag6 -----------------
./start_bagrun_uni.sh ~/bag6_systimefalse
bag6:
 	recorded with use_system_time=False
	unilidar_sdk2/unitree_lidar_ros2/src/unitree_lidar_ros2/launch/launch.py
pointcloud_to_laserscan_uni.yaml:
	max height 0.9 (kitchen ceiling low)
result good.

png:
	slam_bag6.png

note:
	if use_system_time=True, bag data imu timestamp delta not consistent
	if use_system_time=False, bag data imu timestamp delta much consistent
	this might explain point_lio drift due to imu timestamp out of sync when use system time

-----3/26/26 sabertooth driver -----------------
cd ros2_ws_nasa
ros2 launch sabertooth_2x32_serial sabertooth.launch.py  params_file:=sabertooth.yaml
ros2 launch sabertooth_2x32_serial_twist sabertooth_twist.launch.py   params_file:=sabertooth_twist.yaml
ros2 topic pub /motor_power std_msgs/msg/Float32MultiArray '{data: [0.2, 0.2]}' --once

ros2 topic pub /cmd_vel geometry_msgs/msg/Twist   '{linear: {x: 0.2}, angular: {z: 0.0}}' --once

----------3/24/26/ regress test start_bagrun_docker.sh  --------------------
hptitan, aliensrv
  to be done

----------3/22/26/ start_nasa_full.sh  --------------------

panda2:
  cd ros2_ws_nasa; ./start_nasa_full.sh

laptop:
  cd ros2_ws_nasa; ./start_nasa_teleop.sh
 
check /cmd_vel

 ----------3/14/26/ cleanup start_###.sh  --------------------               
                                                                             
 oked: uni bag3 and msbuild bag3, live uni                                   
   start_bagrun.sh                                                           
   start_bagrun_uni.sh                                                       
   start_nasa_full.sh                                                        
                                                                             
 remaing to dbg:                                                             
   why uni data converted scan sparse and have many holes?  

----------3/14/26/ point_lio tf  --------------------
using panda sigma more powerful vmachine

cpu overload, tf might be it:
unitree imu 800hz, much higher than usual
point_lio publish tf per imu, causing tf 2000hz
this overload tf, and anything listen to tf. 
even republish tf node use 100% cpu. even if it only publish at 50 hz, it has to listen to 2000hz tf

fix 1: lidar driver tf disabled now                                             
  tf published by unilidar driver might also cause problem since it is not publi
  there is not reason for lidar driver to publish tf as live tf since lidar and 
                                                                                
fix 2:                                                                          
  point_lio publish_odometry_without_downsample set to false in yaml file 

before this fix nav2 stack will crush the cpu load and cause point_lio 
  to miss data and fail quickly.

after this fix full stack seems to run well

----- 3/14/26 tf who publish what start_nasa_full.sh--------------------
lidar_driver:
  commented off the tf publishing part,
  two static publish nodes
  baal/imu_initial -> baal/imu -> baal/base
  use_system_time true is ok,

point_lio:
  tf pub:
  camera_initial -> aft_mapped

point_cloud_laserscan:
  target_frame in params file
  needed tf:
    frame_id (cloud_in) -> target_frame
pointlio_tf_bridge_uni repub node:
  tf pub:
  odom -> base_link
pointlio_tf_bridge_uni static tf node:
  tf pub:
  base_link -> baal/imu_initial
slam_toolbox:
  tf pub:
    map->odom
  tf need:
    odom -> frame_id (laserscan /scan)
    odom -> base_frame (see param file)

----------3/12/26/ point_lio unitree lidar  --------------------

lidar driver don't use system time
  unitree_lidar_ros2/launch/launch.py 

point_lio only last about 3 minutes, then it fail to compute, stuck

cpu power related?


----------3/10/26/ unitree lidar bag test --------------------
start_bagrun_uni.sh
  change_frame.py to change frame_id of cloud to baal/base 
  bag play should only play two data topics, don't pub tf from bag

unitree lidar to scan sparse:
 ./test_lidarscan_unitree_docker.sh
 [pointcloud_to_laserscan_logged]: cloud points=5312 converted=548 filled_bins=49
[pointlio_mapping-1] feats_undistort size5293
[pointlio_mapping-1] feats_down_body size1952

./test_lidarscan_msbuild_docker.sh
pointcloud_to_laserscan_logged]: cloud points=25721 converted=9810 filled_bins=350

[pointlio_mapping-1] feats_undistort size5452
[pointlio_mapping-1] feats_down_body size724
 
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

start_bagrun.sh: ok                                                             
      msbuild data launch point_lio, slamtool, nav2, bag play                   
  tf: map->odom->base_link->baal/base                                           
    camera_init-?aft_mapped                                                     
  dense laserscan good reconstruct                                              
  raw data 2500 points/frame, about 700 converted to scan stable.               
                                                                                
start_bagrun_uni.sh:                                                            
  change_frame.py                                                               
  tf: map->odom->base_link->baal/base                                           
    camera_init-?aft_mapped                                                     
  unitree data set stationary,                                                  
  sparse laserscan, many laser point inf value, jumpy why?                      
  raw data 5000 points/frame, only 50 converted to scan                         
                                                                                
start_bagrun_docker.sh                                                          
      similar above, for docker setup      

start_nasa.sh: ok                                                               
  live data unilidar quick test                                                 
start_nasa_full.sh: ok                                                          
  live data full stack test: point_lio, slam, nav2                              
  tf: map->odom->base_link->baal/imu_initial->baal/imu->baal/base               
    camera_init-?aft_mapped                                                     
yaml:                                                                           
nav2_pointlio.yaml                    pointcloud_to_laserscan.yaml              
pointcloud_to_laserscan_unitree.yaml  slam_async_pointlio_uni.yaml              
pointcloud_to_laserscan_uni.yaml      slam_async_pointlio.yaml  

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

----ros2 update 3/24/26---------------
  rm /etc/apt/sources.list.d/ros2.list
  rm /etc/apt/sources.list.d/ros2*
  apt update
  curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key |   sudo gpg --dearmor -o /etc/apt/keyrings/ros-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" |   sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
  apt update
    

sudo mkdir -p /etc/apt/keyrings

# 1) Remove old ROS source entries if they exist
sudo rm -f /etc/apt/sources.list.d/ros2.list
sudo rm -f /etc/apt/sources.list.d/ros-latest.list

# 2) Make sure Universe is enabled
sudo apt install -y software-properties-common
sudo add-apt-repository -y universe

# 3) Install the current ROS apt source package (official current method)
sudo apt install -y curl
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

rm /var/lib/apt/lists/*ros*; apt update

 13 ros2 topic echo dropping msg:                                                                                 
 14   sudo apt update && sudo apt install ros-$ROS_DISTRO-rmw-cyclonedds-cpp                                      
 15   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp                                                                
 16   ros2 topic echo /imu/data --qos-reliability best_effort  
