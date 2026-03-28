#!/usr/bin/env python3

import math
from typing import List

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


class CeilingFilterNode(Node):
    def __init__(self) -> None:
        super().__init__("ceiling_filter")

        self.declare_parameter("input_topic", "/unilidar/cloud_raw")
        self.declare_parameter("output_topic", "/unilidar/cloud")
        self.declare_parameter("ceiling_z", 1.8)
        self.declare_parameter("floor_z", 0.2)
        self.declare_parameter("keep_organized", False)

        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value

        self.sub = self.create_subscription(
            PointCloud2,
            input_topic,
            self.cloud_callback,
            10,
        )

        self.pub = self.create_publisher(PointCloud2, output_topic, 10)

        self.get_logger().info(
            f"Ceiling filter started. input={input_topic}, output={output_topic}"
        )

    def cloud_callback(self, msg: PointCloud2) -> None:
        ceiling_z = self.get_parameter("ceiling_z").get_parameter_value().double_value
        floor_z = self.get_parameter("floor_z").get_parameter_value().double_value
        keep_organized = (
            self.get_parameter("keep_organized").get_parameter_value().bool_value
        )

        field_names = [f.name for f in msg.fields]

        if "z" not in field_names:
            self.get_logger().error("Incoming PointCloud2 does not contain a 'z' field")
            return

        z_index = field_names.index("z")

        filtered_points: List[tuple] = []

        # read_points returns each point as a tuple matching msg.fields order
        for pt in point_cloud2.read_points(
            msg,
            field_names=field_names,
            skip_nans=False,
        ):
            z = pt[z_index]

            # Keep NaN points unchanged if organized output is desired
            if isinstance(z, float) and math.isnan(z):
                if keep_organized:
                    filtered_points.append(pt)
                continue

            if floor_z <= z <= ceiling_z:
                filtered_points.append(pt)
            elif keep_organized:
                # Replace removed point with NaNs to preserve organization
                new_pt = list(pt)
                for i, value in enumerate(new_pt):
                    if isinstance(value, float):
                        new_pt[i] = float("nan")
                filtered_points.append(tuple(new_pt))

        if keep_organized:
            out_msg = point_cloud2.create_cloud(
                msg.header,
                msg.fields,
                filtered_points,
            )
            out_msg.height = msg.height
            out_msg.width = msg.width
            out_msg.is_dense = False
        else:
            out_msg = point_cloud2.create_cloud(
                msg.header,
                msg.fields,
                filtered_points,
            )
            out_msg.height = 1
            out_msg.width = len(filtered_points)
            out_msg.is_dense = False

        self.pub.publish(out_msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CeilingFilterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
