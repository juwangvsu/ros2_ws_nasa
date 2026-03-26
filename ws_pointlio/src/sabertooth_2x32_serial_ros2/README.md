# sabertooth_2x32_serial

ROS 2 Python package for the **Dimension Engineering Sabertooth 2x32** motor driver using **serial control**.

It provides one node that can:
- subscribe to `cmd_vel` (`geometry_msgs/msg/Twist`) for differential-drive control
- subscribe to `motor_power` (`std_msgs/msg/Float32MultiArray`) for direct left/right motor commands in the range `[-1.0, 1.0]`
- expose a `stop_motors` (`std_srvs/srv/Trigger`) service
- stop motors automatically when commands time out

## Supported serial protocols

### 1) Packet serial (default)
Recommended for TTL serial wiring to `S1` because it is compact and checksum-protected.

This package uses legacy packet-serial motor commands compatible with non-USB Sabertooth packet serial style:
- M1 forward: command `0`
- M1 reverse: command `1`
- M2 forward: command `4`
- M2 reverse: command `5`
- magnitude: `0..127`
- checksum: `(address + command + value) & 0x7F`

### 2) Plain text serial
Useful when you want the easiest bring-up and are using a serial port that accepts the Sabertooth 2x32 plain text serial commands.

Examples sent by the node:
- `M1:500\n`
- `M2:-300\n`

## Wiring

### TTL serial mode
- Host TX -> Sabertooth `S1`
- Host GND -> Sabertooth `0V`
- Optional host RX <- Sabertooth `S2` (not used by this package yet)

### USB mode
If you connect the Sabertooth 2x32 over USB, Linux will usually expose it as `/dev/ttyACM*`. In that case, plain text serial is often the simplest place to start.

## Sabertooth setup notes
For the Sabertooth 2x32 manual:
- serial mode uses `9600 baud, 8N1 TTL serial levels` by default
- in serial mode, `S1` receives commands and `S2` can be used for readback
- if DIP switch 4 is ON, the controller listens for packet serial or plain text serial commands
- packet serial default address is 128 when DIP switch 5 is ON

Adjust exact switch positions in DEScribe / the official manual to match your configuration.

## Build

```bash
cd ~/ros2_ws/src
cp -r /path/to/sabertooth_2x32_serial .
cd ~/ros2_ws
rosdep install --from-paths src -yi
colcon build --packages-select sabertooth_2x32_serial
source install/setup.bash
```

## Launch

```bash
ros2 launch sabertooth_2x32_serial sabertooth.launch.py \
  params_file:=/absolute/path/to/sabertooth.yaml
```

## Publish direct motor commands

```bash
ros2 topic pub /motor_power std_msgs/msg/Float32MultiArray '{data: [0.25, 0.25]}' --once
```

## Publish cmd_vel

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.2}, angular: {z: 0.0}}' --once
```

## Stop motors

```bash
ros2 service call /stop_motors std_srvs/srv/Trigger '{}'
```

## Parameters

- `port`: serial device, e.g. `/dev/ttyUSB0` or `/dev/ttyACM0`
- `baudrate`: default `9600`
- `address`: packet serial address, default `128`
- `protocol`: `packet` or `plain_text`
- `serial_timeout_sec`: pyserial read/write timeout
- `command_timeout_sec`: watchdog timeout before forced stop
- `max_linear_x`: scales `cmd_vel.linear.x` into `[-1, 1]`
- `max_angular_z`: scales `cmd_vel.angular.z` into `[-1, 1]`
- `motor_1_reversed`: invert left motor
- `motor_2_reversed`: invert right motor
- `deadband`: commands below this magnitude go to zero
- `publish_zero_on_timeout`: stop motors when commands go stale

## Notes

- The node assumes a differential drive robot.
- The `cmd_vel` mixer is intentionally simple: `left = linear - angular`, `right = linear + angular` after normalization.
- If your wiring or gearbox orientation is flipped, change `motor_1_reversed` or `motor_2_reversed`.
- For first bring-up, lift the wheels off the ground and test with very small commands.
