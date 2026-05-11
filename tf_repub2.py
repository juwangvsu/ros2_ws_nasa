import rclpy
from rclpy.node import Node
from tf2_ros import TransformException, Buffer, TransformListener, TransformBroadcaster
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TransformStamped

class MultiTFRepublisher(Node):
    def __init__(self):
        super().__init__('multi_tf_republisher_node')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = TransformBroadcaster(self)

        # Configuration
        self.source_frame = 'camera_rgb_optical_frame'
        self.tag_mapping = {
            'tag_0': 'tag_0_map',
            'tag_1': 'tag_1_map',
            'tag_2': 'tag_2_map'
        }

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        
        self.get_logger().info("Node started. Republishing tags 0, 1, and 2 with /scan timestamps.")

    def scan_callback(self, msg):
        # Current timestamp from the LIDAR scan
        scan_time = msg.header.stamp

        for original_tag, new_name in self.tag_mapping.items():
            try:
                # Lookup latest available transform for this specific tag
                t = self.tf_buffer.lookup_transform(
                    self.source_frame,
                    original_tag,
                    rclpy.time.Time())

                # Prepare the synchronized message
                new_tf = TransformStamped()
                new_tf.header.stamp = scan_time
                new_tf.header.frame_id = self.source_frame
                new_tf.child_frame_id = new_name
                
                # Copy translation and rotation
                new_tf.transform = t.transform

                # Broadcast self.tf_broadcaster.sendTransform
                self.tf_broadcaster.sendTransform(new_tf)

            except TransformException:
                # Silently skip if a specific tag isn't in view/buffer
                continue

def main(args=None):
    rclpy.init(args=args)
    node = MultiTFRepublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
