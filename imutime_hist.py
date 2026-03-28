#!/usr/bin/env python3

import math
from collections import Counter

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu


class ImuDtHistogram(Node):
    def __init__(self):
        super().__init__('imu_dt_histogram')

        self.declare_parameter('topic', '/imu')
        self.declare_parameter('bin_ms', 1.0)
        self.declare_parameter('use_header_stamp', True)

        topic = self.get_parameter('topic').get_parameter_value().string_value
        self.bin_ms = self.get_parameter('bin_ms').get_parameter_value().double_value
        self.use_header_stamp = (
            self.get_parameter('use_header_stamp').get_parameter_value().bool_value
        )

        self.prev_t = None
        self.count = 0
        self.dts = []
        self.hist = Counter()

        self.sub = self.create_subscription(
            Imu,
            topic,
            self.imu_callback,
            1000,
        )

        self.get_logger().info(f'Listening on topic: {topic}')
        self.get_logger().info(f'Histogram bin size: {self.bin_ms} ms')
        self.get_logger().info(f'Use header stamp: {self.use_header_stamp}')

    def msg_time_sec(self, msg: Imu) -> float:
        if self.use_header_stamp:
            sec = msg.header.stamp.sec
            nanosec = msg.header.stamp.nanosec
            if sec != 0 or nanosec != 0:
                return float(sec) + float(nanosec) * 1e-9

        return self.get_clock().now().nanoseconds * 1e-9

    def imu_callback(self, msg: Imu):
        t = self.msg_time_sec(msg)

        if self.prev_t is not None:
            dt = t - self.prev_t
            if dt >= 0.0:
                self.dts.append(dt)
                self.count += 1

                dt_ms = dt * 1000.0
                bin_index = int(math.floor(dt_ms / self.bin_ms))
                bin_start = bin_index * self.bin_ms
                self.hist[bin_start] += 1
            else:
                self.get_logger().warn(f'Negative dt detected: {dt:.9f} s')

        self.prev_t = t

    def print_report(self):
        print()
        print('========== IMU DT HISTOGRAM ==========')

        if not self.dts:
            print('No time differences collected.')
            return

        dt_min = min(self.dts)
        dt_max = max(self.dts)
        dt_mean = sum(self.dts) / len(self.dts)

        sorted_dts = sorted(self.dts)
        n = len(sorted_dts)

        def percentile(p):
            idx = min(int(p * (n - 1)), n - 1)
            return sorted_dts[idx]

        print(f'Samples           : {len(self.dts)}')
        print(f'Min dt            : {dt_min*1000.0:.3f} ms')
        print(f'Max dt            : {dt_max*1000.0:.3f} ms')
        print(f'Mean dt           : {dt_mean*1000.0:.3f} ms')
        print(f'P50 dt            : {percentile(0.50)*1000.0:.3f} ms')
        print(f'P90 dt            : {percentile(0.90)*1000.0:.3f} ms')
        print(f'P99 dt            : {percentile(0.99)*1000.0:.3f} ms')
        print()
        print('Histogram:')

        max_count = max(self.hist.values())
        bar_width = 50

        for bin_start in sorted(self.hist.keys()):
            count = self.hist[bin_start]
            bin_end = bin_start + self.bin_ms
            bar_len = max(1, int(count / max_count * bar_width))
            bar = '#' * bar_len
            print(f'{bin_start:8.3f} - {bin_end:8.3f} ms | {count:6d} | {bar}')


def main(args=None):
    rclpy.init(args=args)
    node = ImuDtHistogram()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.print_report()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
