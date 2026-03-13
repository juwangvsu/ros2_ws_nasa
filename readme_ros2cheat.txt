ros2 cheatsheet:

colcon build --symlink-install
source install/setup.bash
ros2 node list
ros2 topic pub /chatter std_msgs/msg/String '{"data": "Hello"}' -r 0.5
ros2 bag record -o output_bag_name -a
ros2 bag record -o output_bag_name <topic1> <topic2>
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.0}}"
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo odom base_link
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel

ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --yaw 0 --pitch 0 --roll 0 --frame-id base_link --child-frame-id lidar_link
ros2 launch teleop_twist_joy teleop-launch.py joy_config:='xbox'

nav:
ros2 action list | grep navigate_to_pose

ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}"
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped "{header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}"

ros2 topic echo /goal_pose

ros2 service call /navigate_to_pose/_action/cancel_goal action_msgs/srv/CancelGoal "{}"


