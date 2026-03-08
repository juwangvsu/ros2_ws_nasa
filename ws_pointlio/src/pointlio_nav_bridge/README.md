# pointlio_nav_bridge

ROS 2 package that bridges Point-LIO outputs into Nav2-friendly topics:

- subscribes to `/Laser_map` (`sensor_msgs/msg/PointCloud2`) and publishes `/map` (`nav_msgs/msg/OccupancyGrid`)
- subscribes to `/baal/lidar_points` (`sensor_msgs/msg/PointCloud2`) and publishes `/scan` (`sensor_msgs/msg/LaserScan`)
- launch file also publishes simple static TFs:
  - `map -> odom` identity
  - `base_link -> lidar_link` identity

This is intended for **bag playback / quick testing**. For a real robot, replace the identity TF values with your actual mounting offsets and remove `map -> odom` if another localization node already provides it.

## Build

```bash
cd ~/ws/src
cp -r /path/to/pointlio_nav_bridge .
cd ~/ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select pointlio_nav_bridge
source install/setup.bash
```

## Run

```bash
ros2 launch pointlio_nav_bridge pointlio_nav_bridge.launch.py \
  use_sim_time:=true \
  laser_map_topic:=/Laser_map \
  lidar_points_topic:=/baal/lidar_points
```

## Typical stack for playback

Terminal 1:
```bash
ros2 bag play YOUR_BAG --clock
```

Terminal 2:
```bash
ros2 run your_pkg republish_pointlio_tf_as_odom.py --use-sim-time --publish-odom
```

Terminal 3:
```bash
ros2 launch pointlio_nav_bridge pointlio_nav_bridge.launch.py use_sim_time:=true
```

Then confirm:
```bash
ros2 topic echo /map --once
ros2 topic echo /scan --once
```

## Save a map for Nav2

After `/map` looks reasonable:

```bash
ros2 run nav2_map_server map_saver_cli -f pointlio_map --ros-args -p use_sim_time:=true
```

This writes `pointlio_map.yaml` and `pointlio_map.pgm`.

## Notes

The `/map` conversion is intentionally simple:
- filter `/Laser_map` points by `z`
- project `x,y` to a 2D grid
- mark those cells occupied

It does **not** raytrace free space. That is usually good enough to create a first planning map from a dense global cloud, but you may want to post-process or tune:
- `resolution`
- `map_z_min`
- `map_z_max`
- `scan_z_min`
- `scan_z_max`

## Useful launch arguments

- `resolution` default `0.05`
- `map_z_min` default `-0.30`
- `map_z_max` default `0.80`
- `scan_z_min` default `-0.15`
- `scan_z_max` default `0.15`
- `range_min` default `0.20`
- `range_max` default `40.0`
- `map_publish_period_sec` default `5.0`

Example with tighter Z slicing:

```bash
ros2 launch pointlio_nav_bridge pointlio_nav_bridge.launch.py \
  use_sim_time:=true \
  map_z_min:=0.00 map_z_max:=0.30 \
  scan_z_min:=-0.05 scan_z_max:=0.05
```
