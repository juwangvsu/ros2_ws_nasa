import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2

class PointCloudFrameRemapper(Node):
    def __init__(self):
        super().__init__('pointcloud_frame_remapper')
        
        # Subscriber to the remapped bag topic
        self.sub = self.create_subscription(
            PointCloud2, 
            '/unilidar/cloud_raw', 
            self.callback, 
            10)
        
        # Publisher to the target topic name
        self.pub = self.create_publisher(
            PointCloud2, 
            '/unilidar/cloud', 
            10)
        
        self.get_logger().info('Cloud Remapper started. Changing frame to: baal/base')

    def callback(self, msg):
        # Update the frame_id in the header
        msg.header.frame_id = 'baal/base'
        
        # Republish the modified message
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = PointCloudFrameRemapper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
