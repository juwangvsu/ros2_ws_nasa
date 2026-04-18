import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class GoPublisher(Node):
    def __init__(self):
        super().__init__('go_publisher')
        self.pub = self.create_publisher(String, '/usercmd', 10)
        self.timer = self.create_timer(0.5, self.tick)
        self.sent = 0

    def tick(self):
        msg = String()
        msg.data = 'go'
        self.pub.publish(msg)
        self.sent += 1
        self.get_logger().info(f'Published /usercmd: go ({self.sent})')
        if self.sent >= 3:
            rclpy.shutdown()


def main():
    rclpy.init()
    node = GoPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
