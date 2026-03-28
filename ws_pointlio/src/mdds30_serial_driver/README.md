# mdds30_serial_driver

Minimal ROS 2 Python package for the Cytron SmartDriveDuo-30 (MDDS30) in **Serial Simplified** mode.

## Assumptions

- Board DIP switches are set for **Serial Simplified** mode.
- USB serial adapter is available at `/dev/ttyUSB0`.
- Adapter **TX -> IN1** on the MDDS30.
- Adapter **GND -> GND** on the MDDS30.
- Baud rate is **9600**.

## Subscribed topic

- `/cmd_vel` (`geometry_msgs/msg/Twist`)

Mapping:

- `linear.x` controls forward/reverse.
- `angular.z` applies differential steering.

## Build

```bash
cd ~/ros2_ws/src
unzip /path/to/mdds30_serial_driver.zip
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select mdds30_serial_driver
source install/setup.bash
```

## Run

```bash
ros2 launch mdds30_serial_driver mdds30.launch.py
```

Or override parameters:

```bash
ros2 run mdds30_serial_driver mdds30_node --ros-args \
  -p port:=/dev/ttyUSB0 \
  -p baudrate:=9600 \
  -p max_percent:=20.0
```

## Test

Straight forward:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.0}}'
```

Stop:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.0}, angular: {z: 0.0}}'
```

Turn in place:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.0}, angular: {z: 1.0}}'
```

## Permissions

If `/dev/ttyUSB0` gives permission denied:

```bash
sudo usermod -aG dialout $USER
```

Then log out and back in.


## Fixed test node

Run both motors at 50% for 5 seconds, then stop and exit:

```bash
ros2 run mdds30_serial_driver mdds30_test_50pct
```

Optional overrides:

```bash
ros2 run mdds30_serial_driver mdds30_test_50pct --ros-args   -p port:=/dev/ttyUSB0   -p baudrate:=9600   -p percent:=50.0   -p duration_sec:=5.0
```
