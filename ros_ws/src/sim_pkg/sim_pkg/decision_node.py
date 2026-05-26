import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json

class DecisionNode(Node):
    def __init__(self):
        super().__init__('decision_node')

        self.sub = self.create_subscription(
            String,
            '/detections',
            self.callback,
            10
        )

    def callback(self, msg):
        data = json.loads(msg.data)

        for obj in data["objects"]:
            if obj["label"] == "person":
                self.get_logger().info("🚨 Person detected → STOP")

def main(args=None):
    rclpy.init(args=args)
    node = DecisionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()