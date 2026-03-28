#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion


def quat_multiply(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return (
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
    )


def quat_normalize(q):
    x, y, z, w = q
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n < 1e-12:
        return (0.0, 0.0, 0.0, 1.0)
    return (x / n, y / n, z / n, w / n)


def quat_from_angular_velocity(wx, wy, wz, dt):
    angle = math.sqrt(wx * wx + wy * wy + wz * wz) * dt
    if angle < 1e-12:
        return (0.0, 0.0, 0.0, 1.0)

    norm = math.sqrt(wx * wx + wy * wy + wz * wz)
    ax = wx / norm
    ay = wy / norm
    az = wz / norm

    half = 0.5 * angle
    s = math.sin(half)
    c = math.cos(half)
    return (ax * s, ay * s, az * s, c)


def rotate_vector_by_quat(v, q):
    vx, vy, vz = v
    qx, qy, qz, qw = q

    ix =  qw * vx + qy * vz - qz * vy
    iy =  qw * vy + qz * vx - qx * vz
    iz =  qw * vz + qx * vy - qy * vx
    iw = -qx * vx - qy * vy - qz * vz

    rx = ix * qw + iw * -qx + iy * -qz - iz * -qy
    ry = iy * qw + iw * -qy + iz * -qx - ix * -qz
    rz = iz * qw + iw * -qz + ix * -qy - iy * -qx
    return (rx, ry, rz)


def quat_from_two_vectors(v1, v2):
    """
    Returns quaternion rotating v1 to v2.
    v1, v2 should be normalized.
    """
    x1, y1, z1 = v1
    x2, y2, z2 = v2

    dot = x1 * x2 + y1 * y2 + z1 * z2

    if dot < -0.999999:
        # 180 degree rotation
        # choose arbitrary orthogonal axis
        if abs(x1) < abs(y1):
            axis = (0.0, -z1, y1)
        else:
            axis = (-z1, 0.0, x1)
        ax, ay, az = axis
        n = math.sqrt(ax * ax + ay * ay + az * az)
        if n < 1e-12:
            return (0.0, 0.0, 0.0, 1.0)
        ax /= n
        ay /= n
        az /= n
        return (ax, ay, az, 0.0)

    cx = y1 * z2 - z1 * y2
    cy = z1 * x2 - x1 * z2
    cz = x1 * y2 - y1 * x2
    w = 1.0 + dot

    return quat_normalize((cx, cy, cz, w))


def vec_norm(v):
    x, y, z = v
    return math.sqrt(x * x + y * y + z * z)


def vec_normalize(v):
    n = vec_norm(v)
    if n < 1e-12:
        return (0.0, 0.0, 0.0)
    return (v[0] / n, v[1] / n, v[2] / n)


class ImuToOdomCalibrated(Node):
    def __init__(self):
        super().__init__('imu_to_odom_calibrated')

        self.declare_parameter('imu_topic', '/unilidar/imu')
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('calibration_duration', 3.0)
        self.declare_parameter('use_imu_orientation', False)

        imu_topic = self.get_parameter('imu_topic').value
        odom_topic = self.get_parameter('odom_topic').value

        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        self.calibration_duration = float(self.get_parameter('calibration_duration').value)
        self.use_imu_orientation = bool(self.get_parameter('use_imu_orientation').value)

        self.sub = self.create_subscription(Imu, imu_topic, self.imu_callback, 200)
        self.pub = self.create_publisher(Odometry, odom_topic, 50)

        self.last_time = None
        self.calib_start_time = None
        self.calibrated = False

        # calibration accumulators
        self.calib_count = 0
        self.sum_gx = 0.0
        self.sum_gy = 0.0
        self.sum_gz = 0.0
        self.sum_ax = 0.0
        self.sum_ay = 0.0
        self.sum_az = 0.0

        # estimated biases
        self.gyro_bias = (0.0, 0.0, 0.0)
        self.accel_bias = (0.0, 0.0, 0.0)

        # world-from-body orientation
        self.q = (0.0, 0.0, 0.0, 1.0)

        # odom state
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0

        self.get_logger().info(f'Subscribing to {imu_topic}, publishing {odom_topic}')
        self.get_logger().info(
            f'Calibrating for first {self.calibration_duration:.1f} seconds. '
            'Assume robot stays still during this time.'
        )

    def finish_calibration(self):
        if self.calib_count == 0:
            self.get_logger().warn('No IMU samples received during calibration.')
            self.calibrated = True
            return

        avg_gx = self.sum_gx / self.calib_count
        avg_gy = self.sum_gy / self.calib_count
        avg_gz = self.sum_gz / self.calib_count

        avg_ax = self.sum_ax / self.calib_count
        avg_ay = self.sum_ay / self.calib_count
        avg_az = self.sum_az / self.calib_count

        self.gyro_bias = (avg_gx, avg_gy, avg_gz)

        # mean accelerometer during still period includes gravity
        # use it to initialize orientation so measured gravity aligns with world +Z
        g_body = vec_normalize((avg_ax, avg_ay, avg_az))
        g_world = (0.0, 0.0, 1.0)
        self.q = quat_from_two_vectors(g_body, g_world)

        # after orientation is initialized, expected stationary accel in body frame is gravity
        # accel_bias = measured_mean - expected_gravity_in_body
        self.accel_bias = (0.0, 0.0, 0.0)

        self.calibrated = True

        self.get_logger().info(
            'Calibration done:\n'
            f'  samples: {self.calib_count}\n'
            f'  gyro bias: [{self.gyro_bias[0]:.6f}, {self.gyro_bias[1]:.6f}, {self.gyro_bias[2]:.6f}] rad/s\n'
            f'  mean accel: [{avg_ax:.6f}, {avg_ay:.6f}, {avg_az:.6f}] m/s^2\n'
            f'  init quat: [{self.q[0]:.6f}, {self.q[1]:.6f}, {self.q[2]:.6f}, {self.q[3]:.6f}]'
        )

    def publish_odom(self, stamp, angular_velocity):
        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame

        odom.pose.pose.position.x = self.px
        odom.pose.pose.position.y = self.py
        odom.pose.pose.position.z = self.pz

        odom.pose.pose.orientation = Quaternion(
            x=self.q[0],
            y=self.q[1],
            z=self.q[2],
            w=self.q[3],
        )

        odom.twist.twist.linear.x = self.vx
        odom.twist.twist.linear.y = self.vy
        odom.twist.twist.linear.z = self.vz

        odom.twist.twist.angular.x = angular_velocity[0]
        odom.twist.twist.angular.y = angular_velocity[1]
        odom.twist.twist.angular.z = angular_velocity[2]

        odom.pose.covariance[0] = 0.5
        odom.pose.covariance[7] = 0.5
        odom.pose.covariance[14] = 0.5
        odom.pose.covariance[21] = 0.2
        odom.pose.covariance[28] = 0.2
        odom.pose.covariance[35] = 0.2

        odom.twist.covariance[0] = 0.5
        odom.twist.covariance[7] = 0.5
        odom.twist.covariance[14] = 0.5
        odom.twist.covariance[21] = 0.2
        odom.twist.covariance[28] = 0.2
        odom.twist.covariance[35] = 0.2

        self.pub.publish(odom)

    def imu_callback(self, msg: Imu):
        now = rclpy.time.Time.from_msg(msg.header.stamp)

        if self.calib_start_time is None:
            self.calib_start_time = now
            self.last_time = now

        # calibration stage
        if not self.calibrated:
            elapsed = (now - self.calib_start_time).nanoseconds * 1e-9

            self.sum_gx += msg.angular_velocity.x
            self.sum_gy += msg.angular_velocity.y
            self.sum_gz += msg.angular_velocity.z

            self.sum_ax += msg.linear_acceleration.x
            self.sum_ay += msg.linear_acceleration.y
            self.sum_az += msg.linear_acceleration.z

            self.calib_count += 1
            self.last_time = now

            if elapsed >= self.calibration_duration:
                self.finish_calibration()

            return

        dt = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now

        if dt <= 0.0 or dt > 1.0:
            return

        # bias-corrected gyro
        wx = msg.angular_velocity.x - self.gyro_bias[0]
        wy = msg.angular_velocity.y - self.gyro_bias[1]
        wz = msg.angular_velocity.z - self.gyro_bias[2]

        # orientation update
        if self.use_imu_orientation:
            self.q = quat_normalize((
                msg.orientation.x,
                msg.orientation.y,
                msg.orientation.z,
                msg.orientation.w,
            ))
        else:
            dq = quat_from_angular_velocity(wx, wy, wz, dt)
            self.q = quat_normalize(quat_multiply(self.q, dq))

        # bias-corrected accel in body frame
        ax_b = msg.linear_acceleration.x - self.accel_bias[0]
        ay_b = msg.linear_acceleration.y - self.accel_bias[1]
        az_b = msg.linear_acceleration.z - self.accel_bias[2]

        # rotate to world frame
        ax_w, ay_w, az_w = rotate_vector_by_quat((ax_b, ay_b, az_b), self.q)

        # remove gravity in world frame
        az_w -= 9.81

        # integrate
        self.vx += ax_w * dt
        self.vy += ay_w * dt
        self.vz += az_w * dt

        self.px += self.vx * dt
        self.py += self.vy * dt
        self.pz += self.vz * dt

        self.publish_odom(msg.header.stamp, (wx, wy, wz))


def main(args=None):
    rclpy.init(args=args)
    node = ImuToOdomCalibrated()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
