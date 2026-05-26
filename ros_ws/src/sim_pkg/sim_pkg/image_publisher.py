import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import glob

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')

        self.bridge = CvBridge()

        # 👇 change if needed
        self.image_dir = '/ros_ws/src/sim_pkg/sim_pkg/images'

        self.image_paths = sorted(
            glob.glob(os.path.join(self.image_dir, '*.jpg')) +
            glob.glob(os.path.join(self.image_dir, '*.png'))
        )

        if not self.image_paths:
            self.get_logger().error(f"No images found in {self.image_dir}")
            return

        self.index = 0

        self.pub = self.create_publisher(Image, '/camera', 10)

        # ~5 FPS (adjust as needed)
        self.timer = self.create_timer(0.2, self.publish_image)

        # self.get_logger().info(f"Loaded {len(self.image_paths)} images")

    def publish_image(self):
        img_path = self.image_paths[self.index]
        frame = cv2.imread(img_path)

        if frame is None:
            self.get_logger().warning(f"Failed to read {img_path}")
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.pub.publish(msg)
        if self.index %10 ==0:
            self.get_logger().info(f"Publishing: {os.path.basename(img_path)}")

        # loop
        self.index = (self.index + 1) % len(self.image_paths)


def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()