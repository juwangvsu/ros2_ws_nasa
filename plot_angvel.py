import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import matplotlib.pyplot as plt
from collections import deque

class ImuPlotter(Node):
    def __init__(self):
        super().__init__('imu_plotter')
        # Update '/imu/data' to your specific topic name if different
        self.subscription = self.create_subscription(
            Imu, '/unilidar/imu', self.listener_callback, 10)

        # Data buffers
        self.maxlen = 100
        self.x_vals, self.y_vals, self.z_vals, self.time_vals = [deque(maxlen=self.maxlen) for _ in range(4)]
        self.start_time = self.get_clock().now().nanoseconds / 1e9

        # Matplotlib setup
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.line_x, = self.ax.plot([], [], label='X-axis', color='r')
        self.line_y, = self.ax.plot([], [], label='Y-axis', color='g')
        self.line_z, = self.ax.plot([], [], label='Z-axis', color='b')
        self.ax.legend(loc='upper right')
        self.ax.set_ylabel('Angular Velocity (rad/s)')
        self.ax.set_xlabel('Time (s)')

    def listener_callback(self, msg):
        now = (self.get_clock().now().nanoseconds / 1e9) - self.start_time
        
        self.time_vals.append(now)
        self.x_vals.append(msg.angular_velocity.x)
        self.y_vals.append(msg.angular_velocity.y)
        self.z_vals.append(msg.angular_velocity.z)

        # Update lines
        self.line_x.set_data(self.time_vals, self.x_vals)
        self.line_y.set_data(self.time_vals, self.y_vals)
        self.line_z.set_data(self.time_vals, self.z_vals)

        # Adjust view
        self.ax.relim()
        self.ax.autoscale_view()
        plt.pause(0.001)

def main():
    rclpy.init()
    node = ImuPlotter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
