import math
from typing import Dict, List, Optional, Tuple

import rclpy
from geometry_msgs.msg import PoseStamped, TransformStamped
from rclpy.duration import Duration
from rclpy.node import Node
from std_msgs.msg import String
from tf2_ros import Buffer, TransformBroadcaster, TransformListener


def yaw_from_quat(q) -> float:
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def quat_from_yaw(yaw: float) -> Tuple[float, float, float, float]:
    h = 0.5 * yaw
    return (0.0, 0.0, math.sin(h), math.cos(h))


def wrap_to_pi(a: float) -> float:
    while a > math.pi:
        a -= 2.0 * math.pi
    while a < -math.pi:
        a += 2.0 * math.pi
    return a


class GlobalAnchorNode(Node):
    def __init__(self):
        super().__init__('global_anchor_node')
        self.declare_parameter('global_frame', 'global')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('base_frame', 'base_footprint')
        self.declare_parameter('camera_frame', 'camera_rgb_frame')
        self.declare_parameter('required_tag_count', 2)
        self.declare_parameter('required_tag_ids', [0, 1, 2])
        self.declare_parameter('tag_frames', ['tag_0', 'tag_1', 'tag_2'])
        self.declare_parameter('tag_positions_xy', [3.0, -1.0, 3.0, 0.0, 3.0, 1.0])
        self.declare_parameter('republish_period_sec', 0.5)
        self.declare_parameter('publish_debug_pose', True)

        self.global_frame = self.get_parameter('global_frame').value
        self.map_frame = self.get_parameter('map_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        self.camera_frame = self.get_parameter('camera_frame').value
        self.required_tag_count = int(self.get_parameter('required_tag_count').value)
        tag_ids = list(self.get_parameter('required_tag_ids').value)
        tag_frames = list(self.get_parameter('tag_frames').value)
        flat = list(self.get_parameter('tag_positions_xy').value)
        self.tag_global_xy: Dict[str, Tuple[float, float]] = {}
        for i, frame in enumerate(tag_frames):
            self.tag_global_xy[frame] = (float(flat[2 * i]), float(flat[2 * i + 1]))
        self.required_frames = list(self.tag_global_xy.keys())

        self.go_received = False
        self.anchor_locked = False
        self.anchor_tf: Optional[TransformStamped] = None

        self.tf_buffer = Buffer(cache_time=Duration(seconds=10.0))
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.debug_pub = self.create_publisher(PoseStamped, '/global_anchor/debug_base_pose', 10)
        self.usercmd_sub = self.create_subscription(String, '/usercmd', self.usercmd_cb, 10)
        self.timer = self.create_timer(0.2, self.tick)
        self.repub_timer = self.create_timer(float(self.get_parameter('republish_period_sec').value), self.republish)

        self.get_logger().info('Waiting for at least two visible AprilTags and /usercmd == go')

    def usercmd_cb(self, msg: String):
        if msg.data.strip().lower() == 'go':
            self.go_received = True
            self.get_logger().info('Received /usercmd = go')

    def visible_tags(self) -> List[Tuple[str, float, float]]:
        visible = []
        for frame in self.required_frames:
            try:
                tf = self.tf_buffer.lookup_transform(self.camera_frame, frame, rclpy.time.Time(), timeout=Duration(seconds=0.05))
                visible.append((frame, tf.transform.translation.x, tf.transform.translation.y))
            except Exception:
                continue
        return visible

    def tick(self):
        if self.anchor_locked:
            return

        vis = self.visible_tags()
        if len(vis) < self.required_tag_count:
            self.get_logger().info(f'Visible tags: {len(vis)} / {self.required_tag_count}', throttle_duration_sec=2.0)
            return
        if not self.go_received:
            self.get_logger().info('Tags visible. Waiting for /usercmd == go', throttle_duration_sec=2.0)
            return

        try:
            map_to_base = self.tf_buffer.lookup_transform(self.map_frame, self.base_frame, rclpy.time.Time(), timeout=Duration(seconds=0.2))
        except Exception as e:
            self.get_logger().warn(f'Cannot get {self.map_frame}->{self.base_frame} yet: {e}')
            return

        try:
            base_to_camera = self.tf_buffer.lookup_transform(self.base_frame, self.camera_frame, rclpy.time.Time(), timeout=Duration(seconds=0.2))
        except Exception as e:
            self.get_logger().warn(f'Cannot get {self.base_frame}->{self.camera_frame} yet: {e}')
            return

        estimate = self.solve_global_camera(vis)
        if estimate is None:
            self.get_logger().warn('Could not solve anchor from visible tags')
            return
        gcx, gcy, gyaw = estimate

        bcx = base_to_camera.transform.translation.x
        bcy = base_to_camera.transform.translation.y
        gx = gcx - (math.cos(gyaw) * bcx - math.sin(gyaw) * bcy)
        gy = gcy - (math.sin(gyaw) * bcx + math.cos(gyaw) * bcy)

        mx = map_to_base.transform.translation.x
        my = map_to_base.transform.translation.y
        myaw = yaw_from_quat(map_to_base.transform.rotation)

        c = math.cos(gyaw - myaw)
        s = math.sin(gyaw - myaw)
        gmx = gx - (c * mx - s * my)
        gmy = gy - (s * mx + c * my)
        gmyaw = wrap_to_pi(gyaw - myaw)

        tf = TransformStamped()
        tf.header.stamp = self.get_clock().now().to_msg()
        tf.header.frame_id = self.global_frame
        tf.child_frame_id = self.map_frame
        tf.transform.translation.x = gmx
        tf.transform.translation.y = gmy
        tf.transform.translation.z = 0.0
        q = quat_from_yaw(gmyaw)
        tf.transform.rotation.x = q[0]
        tf.transform.rotation.y = q[1]
        tf.transform.rotation.z = q[2]
        tf.transform.rotation.w = q[3]
        self.anchor_tf = tf
        self.anchor_locked = True
        self.tf_broadcaster.sendTransform(tf)
        self.get_logger().info(
            f'Latched initial anchor {self.global_frame}->{self.map_frame}: '
            f'x={gmx:.3f}, y={gmy:.3f}, yaw={gmyaw:.3f} rad'
        )

        if self.get_parameter('publish_debug_pose').value:
            dbg = PoseStamped()
            dbg.header.stamp = tf.header.stamp
            dbg.header.frame_id = self.global_frame
            dbg.pose.position.x = gx
            dbg.pose.position.y = gy
            dbg.pose.position.z = 0.0
            dbg.pose.orientation.x = 0.0
            dbg.pose.orientation.y = 0.0
            dbg.pose.orientation.z = q[2]
            dbg.pose.orientation.w = q[3]
            self.debug_pub.publish(dbg)

    def republish(self):
        if self.anchor_locked and self.anchor_tf is not None:
            self.anchor_tf.header.stamp = self.get_clock().now().to_msg()
            self.tf_broadcaster.sendTransform(self.anchor_tf)

    def solve_global_camera(self, visible: List[Tuple[str, float, float]]) -> Optional[Tuple[float, float, float]]:
        # Use pairs of tags to estimate yaw from the line joining tags, then average.
        if len(visible) < 2:
            return None

        tag_by_name = {name: (x, y) for name, x, y in visible}
        pair_yaws = []
        names = [name for name, _, _ in visible]
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                ni, nj = names[i], names[j]
                gi = self.tag_global_xy[ni]
                gj = self.tag_global_xy[nj]
                ci = tag_by_name[ni]
                cj = tag_by_name[nj]
                gtheta = math.atan2(gj[1] - gi[1], gj[0] - gi[0])
                ctheta = math.atan2(cj[1] - ci[1], cj[0] - ci[0])
                pair_yaws.append(wrap_to_pi(gtheta - ctheta))
        if not pair_yaws:
            return None
        gyaw = math.atan2(sum(math.sin(a) for a in pair_yaws), sum(math.cos(a) for a in pair_yaws))

        # With gyaw fixed, each tag gives a base position estimate.
        cos_y = math.cos(gyaw)
        sin_y = math.sin(gyaw)
        base_estimates = []
        for name, cx, cy in visible:
            gx_tag, gy_tag = self.tag_global_xy[name]
            # camera frame point rotated into global and translated by base.
            bx = gx_tag - (cos_y * cx - sin_y * cy)
            by = gy_tag - (sin_y * cx + cos_y * cy)
            base_estimates.append((bx, by))
        gx = sum(p[0] for p in base_estimates) / len(base_estimates)
        gy = sum(p[1] for p in base_estimates) / len(base_estimates)
        return gx, gy, gyaw


def main():
    rclpy.init()
    node = GlobalAnchorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
