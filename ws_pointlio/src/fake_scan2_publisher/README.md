# fake_scan2_publisher

ROS 2 Python package that subscribes to `/scan` and publishes a fake `sensor_msgs/msg/LaserScan` on `/scan2`.

The fake scan represents a horizontal line segment in the laser frame:

- Start: `(150 cm, -20 cm)`
- End: `(150 cm, 20 cm)`
- In meters: `x = 1.5`, `y in [-0.2, 0.2]`

The outgoing message reuses the incoming scan header and scan metadata. Rays that intersect the segment get the computed range. Other rays are set to `inf`.

## Build

Place this package in a ROS 2 workspace `src` directory, then run:

```bash
colcon build --packages-select fake_scan2_publisher
source install/setup.bash
```

## Run

```bash
ros2 run fake_scan2_publisher fake_scan2_node
```

or:

```bash
ros2 launch fake_scan2_publisher fake_scan2.launch.py
```

## Parameters

- `input_topic`: default `/scan`
- `output_topic`: default `/scan2`
- `line_x_m`: default `1.5`
- `line_y_min_m`: default `-0.2`
- `line_y_max_m`: default `0.2`
