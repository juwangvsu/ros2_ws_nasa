from typing import List

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from std_srvs.srv import Trigger

from .driver import SabertoothConfig, SabertoothSerialDriver


class SabertoothNode(Node):
    def __init__(self) -> None:
        super().__init__('sabertooth_2x32_serial')

        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 9600)
        self.declare_parameter('address', 128)
        self.declare_parameter('protocol', 'packet')
        self.declare_parameter('serial_timeout_sec', 0.1)
        self.declare_parameter('command_timeout_sec', 0.5)
        self.declare_parameter('max_linear_x', 1.0)
        self.declare_parameter('max_angular_z', 1.0)
        self.declare_parameter('motor_1_reversed', False)
        self.declare_parameter('motor_2_reversed', True)
        self.declare_parameter('deadband', 0.02)
        self.declare_parameter('publish_zero_on_timeout', True)

        cfg = SabertoothConfig(
            port=self.get_parameter('port').get_parameter_value().string_value,
            baudrate=self.get_parameter('baudrate').get_parameter_value().integer_value,
            address=self.get_parameter('address').get_parameter_value().integer_value,
            protocol=self.get_parameter('protocol').get_parameter_value().string_value,
            timeout_sec=self.get_parameter('serial_timeout_sec').get_parameter_value().double_value,
            motor_1_reversed=self.get_parameter('motor_1_reversed').get_parameter_value().bool_value,
            motor_2_reversed=self.get_parameter('motor_2_reversed').get_parameter_value().bool_value,
        )

        self._command_timeout_sec = self.get_parameter('command_timeout_sec').value
        self._max_linear_x = self.get_parameter('max_linear_x').value
        self._max_angular_z = self.get_parameter('max_angular_z').value
        self._deadband = self.get_parameter('deadband').value
        self._publish_zero_on_timeout = self.get_parameter('publish_zero_on_timeout').value
        self._last_command_time = self.get_clock().now()
        self._last_left = 0.0
        self._last_right = 0.0

        self._driver = SabertoothSerialDriver(cfg)
        self.get_logger().info(
            f'Opened {cfg.port} at {cfg.baudrate} baud using {cfg.protocol} protocol '
            f'(address={cfg.address}).'
        )

        self.create_subscription(Twist, 'cmd_vel', self._on_cmd_vel, 20)
        self.create_subscription(Float32MultiArray, 'motor_power', self._on_motor_power, 20)
        self.create_service(Trigger, 'stop_motors', self._on_stop_service)
        self.create_timer(0.05, self._on_watchdog)

    def destroy_node(self):
        try:
            self._driver.stop()
            self._driver.close()
        finally:
            super().destroy_node()

    def _on_cmd_vel(self, msg: Twist) -> None:
        linear = self._normalize(msg.linear.x, self._max_linear_x)
        angular = self._normalize(msg.angular.z, self._max_angular_z)

        left = self._apply_deadband(self._clamp(linear - angular))
        right = self._apply_deadband(self._clamp(linear + angular))
        self._send(left, right)

    def _on_motor_power(self, msg: Float32MultiArray) -> None:
        data: List[float] = list(msg.data)
        if len(data) < 2:
            self.get_logger().warn('motor_power must contain [left, right] normalized values.')
            return
        left = self._apply_deadband(self._clamp(float(data[0])))
        right = self._apply_deadband(self._clamp(float(data[1])))
        self._send(left, right)

    def _on_stop_service(self, _request, response):
        self._send(0.0, 0.0)
        response.success = True
        response.message = 'Motors stopped.'
        return response

    def _on_watchdog(self) -> None:
        age = (self.get_clock().now() - self._last_command_time).nanoseconds / 1e9
        if age > self._command_timeout_sec and self._publish_zero_on_timeout:
            if self._last_left != 0.0 or self._last_right != 0.0:
                self.get_logger().warn('Command timeout exceeded. Stopping motors.')
                self._driver.stop()
                self._last_left = 0.0
                self._last_right = 0.0

    def _send(self, left: float, right: float) -> None:
        self._driver.set_motor_power(left, right)
        self._last_left = left
        self._last_right = right
        self._last_command_time = self.get_clock().now()

    @staticmethod
    def _clamp(value: float) -> float:
        return max(-1.0, min(1.0, value))

    @staticmethod
    def _normalize(value: float, limit: float) -> float:
        if limit <= 0.0:
            raise ValueError('Normalization limit must be > 0')
        return max(-1.0, min(1.0, value / limit))

    def _apply_deadband(self, value: float) -> float:
        if abs(value) < self._deadband:
            return 0.0
        return value


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SabertoothNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
