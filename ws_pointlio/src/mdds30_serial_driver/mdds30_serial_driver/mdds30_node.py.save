import math
from typing import Optional

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

try:
    import serial
except ImportError as exc:
    serial = None
    _SERIAL_IMPORT_ERROR = exc
else:
    _SERIAL_IMPORT_ERROR = None


class MDDS30Serial:
    def __init__(self, port: str, baudrate: int) -> None:
        if serial is None:
            raise RuntimeError(
                'pyserial is required. Install with: sudo apt install python3-serial or pip install pyserial'
            ) from _SERIAL_IMPORT_ERROR
        self._ser = serial.Serial(port, baudrate, timeout=0.5)

    @staticmethod
    def encode_left(speed_pct: float) -> int:
        speed_pct = max(-100.0, min(100.0, speed_pct))
        if speed_pct >= 0.0:
            return int(round(speed_pct * 63.0 / 100.0))
        return 64 + int(round((-speed_pct) * 63.0 / 100.0))

    @staticmethod
    def encode_right(speed_pct: float) -> int:
        speed_pct = max(-100.0, min(100.0, speed_pct))
        if speed_pct >= 0.0:
            return 128 + int(round(speed_pct * 63.0 / 100.0))
        return 192 + int(round((-speed_pct) * 63.0 / 100.0))

    def write(self, left_pct: float, right_pct: float) -> None:
        packet = bytes([
            self.encode_left(left_pct),
            self.encode_right(right_pct),
        ])
        self._ser.write(packet)
        self._ser.flush()

    def close(self) -> None:
        if self._ser.is_open:
            self._ser.close()


class MDDS30Node(Node):
    def __init__(self) -> None:
        super().__init__('mdds30_serial_driver')

        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 9600)
        self.declare_parameter('max_percent', 30.0)
        self.declare_parameter('wheel_base', 0.40)
        self.declare_parameter('watchdog_sec', 0.5)
        self.declare_parameter('invert_left', False)
        self.declare_parameter('invert_right', False)

        port = self.get_parameter('port').value
        baudrate = int(self.get_parameter('baudrate').value)
        self._max_percent = float(self.get_parameter('max_percent').value)
        self._wheel_base = float(self.get_parameter('wheel_base').value)
        self._watchdog_sec = float(self.get_parameter('watchdog_sec').value)
        self._invert_left = bool(self.get_parameter('invert_left').value)
        self._invert_right = bool(self.get_parameter('invert_right').value)

        self._driver = MDDS30Serial(port, baudrate)
        self._last_cmd_time = self.get_clock().now()
        self._last_left = 0.0
        self._last_right = 0.0

        self.create_subscription(Twist, 'cmd_vel', self._on_cmd_vel, 10)
        self.create_timer(0.1, self._watchdog)

        self.get_logger().info(
            f'MDDS30 serial driver started on {port} at {baudrate} baud. Waiting for /cmd_vel.'
        )

    def _map_twist_to_percent(self, msg: Twist) -> tuple[float, float]:
        linear = float(msg.linear.x)
        angular = float(msg.angular.z)

        left = linear - (angular * self._wheel_base / 2.0)
        right = linear + (angular * self._wheel_base / 2.0)

        max_mag = max(abs(left), abs(right), 1.0)
        left_norm = left / max_mag
        right_norm = right / max_mag

        left_pct = left_norm * self._max_percent
        right_pct = right_norm * self._max_percent

        if self._invert_left:
            left_pct = -left_pct
        if self._invert_right:
            right_pct = -right_pct

        return left_pct, right_pct

    def _send(self, left_pct: float, right_pct: float) -> None:
        left_pct = max(-100.0, min(100.0, left_pct))
        right_pct = max(-100.0, min(100.0, right_pct))
        self._driver.write(left_pct, right_pct)
        self._last_left = left_pct
        self._last_right = right_pct

    def _on_cmd_vel(self, msg: Twist) -> None:
        left_pct, right_pct = self._map_twist_to_percent(msg)
        self._send(left_pct, right_pct)
        self._last_cmd_time = self.get_clock().now()
        self.get_logger().debug(f'Sent left={left_pct:.1f}% right={right_pct:.1f}%')

    def _watchdog(self) -> None:
        age = (self.get_clock().now() - self._last_cmd_time).nanoseconds / 1e9
        if age > self._watchdog_sec and (self._last_left != 0.0 or self._last_right != 0.0):
            self._send(0.0, 0.0)
            self.get_logger().warn('cmd_vel timeout; motors stopped')

    def destroy_node(self) -> bool:
        try:
            self._driver.write(0.0, 0.0)
            self._driver.close()
        finally:
            return super().destroy_node()


def main(args: Optional[list[str]] = None) -> None:
    rclpy.init(args=args)
    node = None
    try:
        node = MDDS30Node()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
