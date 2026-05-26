import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
from rclpy.qos import qos_profile_sensor_data

import json
import asyncio
import websockets
import base64
import threading


class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')

        self.bridge = CvBridge()

        self.latest_frame = None   # 🔥 store only latest frame
        self.ws = None

        # Async loop
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_loop, daemon=True).start()

        asyncio.run_coroutine_threadsafe(self.connect(), self.loop)

        self.subscription = self.create_subscription(
            Image,
            '/camera',
            self.listener_callback,
            qos_profile_sensor_data
        )

        self.pub = self.create_publisher(String, '/detections', 10)

        # 🔥 controlled sending rate (~5 FPS)
        self.timer = self.create_timer(0.2, self.process_and_send)

        self.frame_count = 0

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def connect(self):
        try:
            self.ws = await websockets.connect("ws://host.docker.internal:8000/ws")
            self.get_logger().info("Connected to server")
            asyncio.create_task(self.receive())
        except Exception as e:
            self.get_logger().error(f"Connection failed: {e}")

    # 🔥 FAST callback (no heavy work)
    def listener_callback(self, msg):
        self.latest_frame = msg

    # 🔥 controlled processing loop
    def process_and_send(self):
        if self.latest_frame is None or self.ws is None:
            return

        frame = self.bridge.imgmsg_to_cv2(self.latest_frame, desired_encoding='bgr8')

        # resize → huge speed gain
        frame = cv2.resize(frame, (320, 240))

        # compress
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        # send async (non-blocking)
        asyncio.run_coroutine_threadsafe(
            self.ws.send(jpg_as_text),
            self.loop
        )

        self.frame_count += 1

        # 🔥 minimal logging
        if self.frame_count % 20 == 0:
            self.get_logger().info(f"Frames sent: {self.frame_count}")

    async def receive(self):
        while True:
            result = await self.ws.recv()

            # 🔥 no heavy logging
            msg = String()
            msg.data = result
            self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()