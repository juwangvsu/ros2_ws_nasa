#!/usr/bin/env python3
import select
import sys
import termios
import tty
from dataclasses import dataclass
from typing import Optional, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import serial

ARM = 0
BUCKET = 1
FORWARD = 1
REVERSE = 0
STOP = 0


@dataclass
class ActuatorCommand:
    arm_dir: int = REVERSE
    arm_speed: int = STOP
    bucket_dir: int = REVERSE
    bucket_speed: int = STOP


class KeyboardReader:
    def __init__(self):
        self.old_settings = None

    def __enter__(self):
        if sys.stdin.isatty():
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.old_settings is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def read_key(self) -> Optional[str]:
        if not sys.stdin.isatty():
            return None
        readable, _, _ = select.select([sys.stdin], [], [], 0.0)
        if readable:
            return sys.stdin.read(1)
        return None


class ActuatorControlNode(Node):
    def __init__(self):
        super().__init__('actuator_control_node')

        self.declare_parameter('mode', 'keyboard')
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', 9600)
        self.declare_parameter('speed', 30)
        self.declare_parameter('joy_topic', '/joy')
        self.declare_parameter('deadzone', 0.25)
        self.declare_parameter('send_period', 0.10)

        self.mode = str(self.get_parameter('mode').value).lower()
        self.port = str(self.get_parameter('port').value)
        self.baud = int(self.get_parameter('baud').value)
        self.speed = max(0, min(63, int(self.get_parameter('speed').value)))
        self.joy_topic = str(self.get_parameter('joy_topic').value)
        self.deadzone = float(self.get_parameter('deadzone').value)
        self.send_period = float(self.get_parameter('send_period').value)

        if self.mode not in ('keyboard', 'joystick'):
            raise ValueError("mode must be 'keyboard' or 'joystick'")

        self.serial = serial.Serial(self.port, self.baud, timeout=1)
        self.command = ActuatorCommand()
        self.keyboard = KeyboardReader() if self.mode == 'keyboard' else None
        self.keyboard_context = None

        if self.mode == 'keyboard':
            self.keyboard_context = self.keyboard.__enter__()
            self.print_keyboard_help()
        else:
            self.create_subscription(Joy, self.joy_topic, self.on_joy, 10)
            self.get_logger().info(
                f'Joystick mode: listening to {self.joy_topic}. '
                'Left stick vertical controls arm, right stick vertical controls bucket. '
                'Positive axis extends, negative axis retracts.'
            )

        self.timer = self.create_timer(self.send_period, self.on_timer)
        self.get_logger().info(f'Connected to ESP32 on {self.port} at {self.baud} baud')

    def destroy_node(self):
        try:
            self.stop_all()
            if self.keyboard is not None:
                self.keyboard.__exit__(None, None, None)
            if self.serial is not None and self.serial.is_open:
                self.serial.close()
        finally:
            super().destroy_node()

    def print_keyboard_help(self):
        self.get_logger().info(
            "Keyboard mode:\n"
            "  i: extend both actuators  = raise arm + dump bucket\n"
            "  k: retract both actuators = lower arm + raise bucket\n"
            "  j: bucket up only\n"
            "  u: bucket down only\n"
            "  o: arm up only\n"
            "  l: arm down only\n"
            "  space: stop both\n"
            "  q: quit"
        )

    def build_actuator_byte(self, channel: int, direction: int, speed: int) -> int:
        byte = 0
        byte |= (channel & 0x01) << 7
        byte |= (direction & 0x01) << 6
        byte |= speed & 0x3F
        return byte

    def send_command(self, cmd: ActuatorCommand):
        b1 = self.build_actuator_byte(ARM, cmd.arm_dir, cmd.arm_speed)
        b2 = self.build_actuator_byte(BUCKET, cmd.bucket_dir, cmd.bucket_speed)
        self.serial.write(bytes([b1, b2]))

    def stop_all(self):
        self.command = ActuatorCommand()
        if self.serial is not None and self.serial.is_open:
            self.send_command(self.command)

    def on_timer(self):
        #print("get on_timer")
        if self.mode == 'keyboard':
            key = self.keyboard.read_key()

            print("get on_timer", key)
            if key is not None:
                self.handle_key(key)

        self.send_command(self.command)

    def handle_key(self, key: str):
        s = self.speed

        # Direction convention follows the uploaded ESP test script:
        # direction 1 extends, direction 0 retracts.
        if key == 'i':
            self.get_logger().info(f" get key {key}")
            self.command = ActuatorCommand(FORWARD, s, REVERSE, s)
        elif key == 'k':
            self.command = ActuatorCommand(REVERSE, s, FORWARD, s)
        elif key == 'j':
            self.command = ActuatorCommand(REVERSE, 0, REVERSE, s)  # bucket up only
        elif key == 'u':
            self.command = ActuatorCommand(REVERSE, 0, FORWARD, s)  # bucket down only
        elif key == 'o':
            self.command = ActuatorCommand(FORWARD, s, REVERSE, 0)  # arm up only
        elif key == 'l':
            self.command = ActuatorCommand(REVERSE, s, REVERSE, 0)  # arm down only
        elif key == ' ':
            self.command = ActuatorCommand()
        elif key == 'q':
            self.get_logger().info('Quit requested')
            rclpy.shutdown()
        else:
            return

        self.get_logger().info(f'key={repr(key)} command={self.command}')

    def axis_to_dir_speed(self, value: float) -> Tuple[int, int]:
        if abs(value) < self.deadzone:
            return REVERSE, 0
        direction = FORWARD if value > 0.0 else REVERSE
        speed = int(min(63, max(1, round(abs(value) * self.speed))))
        return direction, speed

    def on_joy(self, msg: Joy):
        # Default mapping for common Xbox controllers through joy_node:
        # axes[1] = left stick vertical, axes[4] = right stick vertical.
        arm_axis = msg.axes[4] if len(msg.axes) > 4 else 0.0
        bucket_axis = msg.axes[3] if len(msg.axes) > 3 else 0.0

        arm_dir, arm_speed = self.axis_to_dir_speed(arm_axis)
        bucket_dir, bucket_speed = self.axis_to_dir_speed(bucket_axis)
        self.command = ActuatorCommand(arm_dir, arm_speed, bucket_dir, bucket_speed)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = ActuatorControlNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
