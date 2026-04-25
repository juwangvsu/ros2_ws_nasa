#  double check ttyUSB2 or 1 or 0
#  if joystick mode, the node should just listen to the joystick msg.
#  for keyboard mode
# 'i' to extend both acuators (this will raise the arm and dump the bucket).
# 'k' to retract both acuators (that will low the arm and raise the bucket).
# 'j' to only raise the bucket
# 'u' to only dump the bucket
# 'o' to only raise the arm
# 'l' to only lower the arm

ros2 run esp32_actuator_control actuator_control_node   --ros-args   -p mode:=joystick   -p port:=/dev/bucket
