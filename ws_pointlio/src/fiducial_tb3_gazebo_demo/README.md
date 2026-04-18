# fiducial_tb3_gazebo_demo

ROS 2 Humble demo package for:
- Gazebo classic
- TurtleBot3 Waffle
- `slam_toolbox` mapping from `/scan`
- `apriltag_ros` detections from the built-in Waffle camera
- one-shot startup anchor `global -> map`

The startup gate waits until:
1. at least **two** AprilTag frames are visible, and
2. a `std_msgs/String` with value `go` is received on `/usercmd`

Then it computes and latches a single `global -> map` transform.

## World layout

The world has a single side wall at `x = 3.0` with three AprilTags mounted on it:
- tag 0 at `(x=3.0, y=-1.0, z=1.0)`
- tag 1 at `(x=3.0, y= 0.0, z=1.0)`
- tag 2 at `(x=3.0, y= 1.0, z=1.0)`

Each tag is 0.20 m square and uses the AprilTag 36h11 dictionary.

## Assumptions

This package assumes the following packages are installed in the ROS 2 Humble environment:
- `gazebo_ros`
- `slam_toolbox`
- `apriltag_ros`
- `image_proc`
- `turtlebot3_gazebo`
- `turtlebot3_description`

## Build

```bash
cd ~/ros2_ws/src
unzip fiducial_tb3_gazebo_demo.zip
cd ..
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select fiducial_tb3_gazebo_demo
source install/setup.bash
```

## Run

```bash
ros2 launch fiducial_tb3_gazebo_demo sim_mapping_anchor.launch.py
```

In another terminal:

```bash
source ~/ros2_ws/install/setup.bash
ros2 run fiducial_tb3_gazebo_demo go_publisher
```

## Notes

- This package expects the TurtleBot3 Waffle Gazebo SDF to expose `/scan`, `/camera/image_raw`, and `/camera/camera_info`.
- Some TurtleBot3 / Gazebo package versions differ slightly in model file names and camera topic/frame names. The launch file already falls back between `model.sdf` and `model-1_4.sdf`, but you may still need to adjust the camera frame in `config/global_anchor.yaml` if your image pipeline uses a different frame ID.
- The anchor node republishes the latched transform on `/tf` rather than `/tf_static` to keep the implementation simple.
