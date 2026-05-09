import math
from typing import List

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class FakeScan2Publisher(Node):
    """Subscribe to /scan and publish a fake horizontal line segment on /scan2.

    The fake obstacle is a horizontal segment in the laser frame:
      - from (150 cm, -20 cm) to (150 cm, 20 cm)
      - equivalent to x = 1.5 m and y in [-0.2 m, 0.2 m]

    For each output ray angle theta, the node computes the intersection with
    x = 1.5 m. If the intersection y coordinate lies on the segment, that ray
    gets range = 1.5 / cos(theta). Otherwise the range is +inf.
    """

    def __init__(self) -> None:
        super().__init__('fake_scan2_publisher')

        self.declare_parameter('input_topic', '/scan')
        self.declare_parameter('output_topic', '/scan2')
        self.declare_parameter('line_x_m', 1.5)
        self.declare_parameter('line_y_min_m', -0.2)
        self.declare_parameter('line_y_max_m', 0.2)

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        self._publisher = self.create_publisher(LaserScan, output_topic, 10)
        self._subscription = self.create_subscription(
            LaserScan,
            input_topic,
            self._scan_callback,
            10,
        )

        self.get_logger().info(
            f'Listening to {input_topic} and publishing fake scan to {output_topic}'
        )

    def _scan_callback(self, msg: LaserScan) -> None:
        out = LaserScan()

        # Reuse the incoming header and scan metadata.
        out.header = msg.header
        out.angle_min = msg.angle_min
        out.angle_max = msg.angle_max
        out.angle_increment = msg.angle_increment
        out.time_increment = msg.time_increment
        out.scan_time = msg.scan_time
        out.range_min = msg.range_min
        out.range_max = msg.range_max

        out.ranges = self._make_line_ranges(msg)
        out.intensities = []

        self._publisher.publish(out)

    def _make_line_ranges(self, msg: LaserScan) -> List[float]:
        line_x = float(self.get_parameter('line_x_m').value)
        y_min = float(self.get_parameter('line_y_min_m').value)
        y_max = float(self.get_parameter('line_y_max_m').value)

        if y_min > y_max:
            y_min, y_max = y_max, y_min

        count = self._range_count(msg)
        ranges: List[float] = []

        for i in range(count):
            theta = msg.angle_min + i * msg.angle_increment
            cos_theta = math.cos(theta)

            # The segment is in front at x > 0. Rays pointing away from it do
            # not intersect it with a positive range.
            if cos_theta <= 1e-9:
                ranges.append(math.inf)
                continue

            r = line_x / cos_theta
            y = r * math.sin(theta)

            if y_min <= y <= y_max and msg.range_min <= r <= msg.range_max:
                ranges.append(float(r))
            else:
                ranges.append(math.inf)

        return ranges

    @staticmethod
    def _range_count(msg: LaserScan) -> int:
        """Prefer incoming ranges length; otherwise derive count from angles."""
        if len(msg.ranges) > 0:
            return len(msg.ranges)
        if msg.angle_increment == 0.0:
            return 0
        return max(0, int(round((msg.angle_max - msg.angle_min) / msg.angle_increment)) + 1)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = FakeScan2Publisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
