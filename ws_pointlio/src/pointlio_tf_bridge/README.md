# pointlio_tf_bridge

ROS 2 package to:
- republish Point-LIO TF `camera_init -> aft_mapped` as `odom -> base_link`
- publish `/odom` as `nav_msgs/msg/Odometry`
- publish a static TF `base_link -> baal/imu_initial` at launch

## Build
```bash
cd ~/ws/src
unzip pointlio_tf_bridge_updated.zip
cd ~/ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select pointlio_tf_bridge
source install/setup.bash
```

## Run
```bash
ros2 launch pointlio_tf_bridge pointlio_tf_bridge.launch.py use_sim_time:=true
```
