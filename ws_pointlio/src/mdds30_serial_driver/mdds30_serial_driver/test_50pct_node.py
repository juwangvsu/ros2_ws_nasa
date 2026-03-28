from typing import Optional

import rclpy
from rclpy.node import Node

from mdds30_serial_driver.mdds30_node import MDDS30Serial


class MDDS30FixedRunNode(Node):
    def __init__(self) -> None:
        super().__init__('mdds30_test_50pct')

        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 9600)
        self.declare_parameter('percent', 50.0)
        self.declare_parameter('duration_sec', 5.0)
        self.declare_parameter('invert_left', False)
        self.declare_parameter('invert_right', False)

        port = str(self.get_parameter('port').value)
        baudrate = int(self.get_parameter('baudrate').value)
        percent = float(self.get_parameter('percent').value)
        duration_sec = float(self.get_parameter('duration_sec').value)
        invert_left = bool(self.get_parameter('invert_left').value)
        invert_right = bool(self.get_parameter('invert_right').value)

        left = -percent if invert_left else percent
        right = -percent if invert_right else percent

        self._driver = MDDS30Serial(port, baudrate)
        self._stopped = False

        self.get_logger().info(
            f'Starting fixed motor test on {port} at {baudrate} baud: '
            f'left={left:.1f}% right={right:.1f}% for {duration_sec:.1f}s'
        )
        self._driver.write(left, right)
        self.create_timer(duration_sec, self._pause1)
        #self._driver.write(20.0, 80.0)
        self.create_timer(2*duration_sec, self._finish)

    def _pause1(self)-> None:
        print(f"xxx ")
        self._driver.write(20.0, 80.0)
        return

    def _finish(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self._driver.write(0.0, 0.0)
        self.get_logger().info('Test complete. Motors stopped.')
        self.destroy_node()
        rclpy.shutdown()

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
        node = MDDS30FixedRunNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()
        if node is not None:
            try:
                node.destroy_node()
            except Exception:
                pass


if __name__ == '__main__':
    main()
