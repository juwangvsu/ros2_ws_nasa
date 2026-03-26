# sabertooth_2x32_serial_twist

ROS 2 Python package for the **Dimension Engineering Sabertooth 2x32** motor driver using **serial control**.

This second version explicitly subscribes to:
- `/cmd_vel` (`geometry_msgs/msg/Twist`) for differential-drive control
- `/motor_power` (`std_msgs/msg/Float32MultiArray`) for direct left/right motor commands in `[-1.0, 1.0]`
- `stop_motors` (`std_srvs/srv/Trigger`) to immediately stop both motors

## Main difference from the first version
- this package defaults the Twist topic to the absolute ROS topic `/cmd_vel`
- topic names are configurable with parameters `cmd_vel_topic` and `motor_power_topic`

## Supported serial protocols

### 1) Packet serial (default)
Recommended for TTL serial wiring to `S1` because it is compact and checksum-protected.

This package uses packet serial motor commands:
- M1 forward: command `0`
- M1 reverse: command `1`
- M2 forward: command `4`
- M2 reverse: command `5`
- magnitude: `0..127`
- checksum: `(address + command + value) & 0x7F`

### 2) Plain text serial
Examples sent by the node:
- `M1:500\n`
- `M2:-300\n`

## Build

```bash
cd ~/ros2_ws/src
cp -r /path/to/sabertooth_2x32_serial_twist .
cd ~/ros2_ws
rosdep install --from-paths src -yi
colcon build --packages-select sabertooth_2x32_serial_twist
source install/setup.bash
```

## Launch

```bash
ros2 launch sabertooth_2x32_serial_twist sabertooth_twist.launch.py \
  params_file:=/absolute/path/to/sabertooth_twist.yaml
```

## Publish Twist on /cmd_vel

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.2}, angular: {z: 0.0}}' --once
```

## Publish direct motor commands

```bash
ros2 topic pub /motor_power std_msgs/msg/Float32MultiArray '{data: [0.25, 0.25]}' --once
```

## Stop motors

```bash
ros2 service call /stop_motors std_srvs/srv/Trigger '{}'
```
