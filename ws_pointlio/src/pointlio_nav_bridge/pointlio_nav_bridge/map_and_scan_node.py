#!/usr/bin/env python3
import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from builtin_interfaces.msg import Time
from nav_msgs.msg import OccupancyGrid, MapMetaData
from sensor_msgs.msg import LaserScan, PointCloud2, PointField
from sensor_msgs_py import point_cloud2


def _field_names(msg: PointCloud2) -> List[str]:
    return [f.name for f in msg.fields]


def _cloud_points(msg: PointCloud2, want_intensity: bool = False):
    names = _field_names(msg)
    if want_intensity and 'intensity' in names:
        fields = ('x', 'y', 'z', 'intensity')
    else:
        fields = ('x', 'y', 'z')
    return point_cloud2.read_points(msg, field_names=fields, skip_nans=True)


class MapAndScanNode(Node):
    def __init__(self) -> None:
        super().__init__('pointlio_map_and_scan_node')

        self.declare_parameter('laser_map_topic', '/Laser_map')
        self.declare_parameter('lidar_points_topic', '/baal/lidar_points')
        self.declare_parameter('map_topic', '/map')
        self.declare_parameter('scan_topic', '/scan')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('scan_frame', 'base_link')
        self.declare_parameter('resolution', 0.05)
        self.declare_parameter('map_z_min', 0.4)
        self.declare_parameter('map_z_max', 1.2)
        self.declare_parameter('scan_z_min', 0.4)
        self.declare_parameter('scan_z_max', 1.2)
        self.declare_parameter('map_padding_m', 5.0)
        self.declare_parameter('map_publish_period_sec', 5.0)
        self.declare_parameter('scan_publish_period_sec', 0.1)
        self.declare_parameter('angle_min', -math.pi)
        self.declare_parameter('angle_max', math.pi)
        self.declare_parameter('angle_increment', math.radians(0.5))
        self.declare_parameter('range_min', 0.2)
        self.declare_parameter('range_max', 100.0)
        self.declare_parameter('use_inf', True)
        self.declare_parameter('track_unknown_space', False)
        self.declare_parameter('occupied_value', 100)
        self.declare_parameter('free_value', 0)
        self.declare_parameter('unknown_value', -1)

        self.laser_map_topic = self.get_parameter('laser_map_topic').value
        self.lidar_points_topic = self.get_parameter('lidar_points_topic').value
        self.map_topic = self.get_parameter('map_topic').value
        self.scan_topic = self.get_parameter('scan_topic').value
        self.map_frame = self.get_parameter('map_frame').value
        self.scan_frame = self.get_parameter('scan_frame').value
        self.resolution = float(self.get_parameter('resolution').value)
        self.map_z_min = float(self.get_parameter('map_z_min').value)
        self.map_z_max = float(self.get_parameter('map_z_max').value)
        self.scan_z_min = float(self.get_parameter('scan_z_min').value)
        self.scan_z_max = float(self.get_parameter('scan_z_max').value)
        self.map_padding_m = float(self.get_parameter('map_padding_m').value)
        self.angle_min = float(self.get_parameter('angle_min').value)
        self.angle_max = float(self.get_parameter('angle_max').value)
        self.angle_increment = float(self.get_parameter('angle_increment').value)
        self.range_min = float(self.get_parameter('range_min').value)
        self.range_max = float(self.get_parameter('range_max').value)
        self.use_inf = bool(self.get_parameter('use_inf').value)
        self.track_unknown_space = bool(self.get_parameter('track_unknown_space').value)
        self.occupied_value = int(self.get_parameter('occupied_value').value)
        self.free_value = int(self.get_parameter('free_value').value)
        self.unknown_value = int(self.get_parameter('unknown_value').value)

        map_period = float(self.get_parameter('map_publish_period_sec').value)
        scan_period = float(self.get_parameter('scan_publish_period_sec').value)

        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self.map_pub = self.create_publisher(OccupancyGrid, self.map_topic, 1)
        self.scan_pub = self.create_publisher(LaserScan, self.scan_topic, 10)

        self.map_sub = self.create_subscription(PointCloud2, self.laser_map_topic, self._on_laser_map, qos)
        self.scan_sub = self.create_subscription(PointCloud2, self.lidar_points_topic, self._on_lidar_points, qos)

        self._latest_map_cloud: Optional[PointCloud2] = None
        self._latest_scan_cloud: Optional[PointCloud2] = None

        self.map_timer = self.create_timer(map_period, self._publish_map)
        self.scan_timer = self.create_timer(scan_period, self._publish_scan)

        self.get_logger().info(
            f'Listening on {self.laser_map_topic} for global cloud -> {self.map_topic}, '
            f'and {self.lidar_points_topic} for live cloud -> {self.scan_topic}'
        )

    def _on_laser_map(self, msg: PointCloud2) -> None:
        self._latest_map_cloud = msg
        print(f"xxx get a /Laser_map msg", flush=True)

    def _on_lidar_points(self, msg: PointCloud2) -> None:
        self._latest_scan_cloud = msg
        self._publish_scan(msg)

    def _publish_map(self) -> None:
        if self._latest_map_cloud is None:
            return
        self._publish_map_from_cloud(self._latest_map_cloud)

    def _publish_scan(self, msg: Optional[PointCloud2] = None) -> None:
        cloud = msg if msg is not None else self._latest_scan_cloud
        if cloud is None:
            return

        angle_count = int(math.floor((self.angle_max - self.angle_min) / self.angle_increment)) + 1
        ranges = [math.inf if self.use_inf else (self.range_max + 1.0)] * angle_count
        intensities = [0.0] * angle_count
        have_intensity = 'intensity' in _field_names(cloud)
        print(f"xxx  self.scan_z_min { self.scan_z_min}")
        for pt in _cloud_points(cloud, want_intensity=have_intensity):
            if have_intensity:
                x, y, z, intensity = pt
            else:
                x, y, z = pt
                intensity = 0.0
            if z < self.scan_z_min or z > self.scan_z_max:
                continue
            #print(f"xxx  z {z}")
            r = math.hypot(x, y)
            if r < self.range_min or r > self.range_max:
                continue
            a = math.atan2(y, x)
            if a < self.angle_min or a > self.angle_max:
                continue
            idx = int((a - self.angle_min) / self.angle_increment)
            if 0 <= idx < angle_count and r < ranges[idx]:
                ranges[idx] = r
                intensities[idx] = float(intensity)

        scan = LaserScan()
        scan.header.stamp = cloud.header.stamp
        scan.header.frame_id = self.scan_frame
        scan.angle_min = self.angle_min
        scan.angle_max = self.angle_max
        scan.angle_increment = self.angle_increment
        scan.time_increment = 0.0
        scan.scan_time = 0.0
        scan.range_min = self.range_min
        scan.range_max = self.range_max
        scan.ranges = ranges
        scan.intensities = intensities
        self.scan_pub.publish(scan)

    def _publish_map_from_cloud(self, cloud: PointCloud2) -> None:
        print(f"xxx publish /map", flush=True)
        pts_xy: List[Tuple[float, float]] = []
        for x, y, z in _cloud_points(cloud, want_intensity=False):
            if z < self.map_z_min or z > self.map_z_max:
                continue
            pts_xy.append((float(x), float(y)))

        if not pts_xy:
            self.get_logger().warn('No map points left after Z filtering; /map not updated', throttle_duration_sec=5.0)
            return

        pts = np.array(pts_xy, dtype=np.float32)
        min_xy = pts.min(axis=0) - self.map_padding_m
        max_xy = pts.max(axis=0) + self.map_padding_m
        width = int(math.ceil((max_xy[0] - min_xy[0]) / self.resolution)) + 1
        height = int(math.ceil((max_xy[1] - min_xy[1]) / self.resolution)) + 1

        fill = self.unknown_value if self.track_unknown_space else self.free_value
        grid = np.full((height, width), fill, dtype=np.int8)

        gx = np.floor((pts[:, 0] - min_xy[0]) / self.resolution).astype(np.int32)
        gy = np.floor((pts[:, 1] - min_xy[1]) / self.resolution).astype(np.int32)

        valid = (gx >= 0) & (gx < width) & (gy >= 0) & (gy < height)
        gx = gx[valid]
        gy = gy[valid]
        grid[gy, gx] = self.occupied_value

        msg = OccupancyGrid()
        msg.header.stamp = cloud.header.stamp
        msg.header.frame_id = self.map_frame

        info = MapMetaData()
        info.map_load_time = self._copy_time(cloud.header.stamp)
        info.resolution = float(self.resolution)
        info.width = int(width)
        info.height = int(height)
        info.origin.position.x = float(min_xy[0])
        info.origin.position.y = float(min_xy[1])
        info.origin.position.z = 0.0
        info.origin.orientation.w = 1.0
        msg.info = info
        msg.data = grid.reshape(-1).tolist()
        self.map_pub.publish(msg)

    @staticmethod
    def _copy_time(t: Time) -> Time:
        copied = Time()
        copied.sec = t.sec
        copied.nanosec = t.nanosec
        return copied


def main() -> None:
    rclpy.init()
    node = MapAndScanNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
