from fastapi import FastAPI, WebSocket
import base64
import cv2
import numpy as np
from ultralytics import YOLO

app = FastAPI()

#load model 
model = YOLO("yolov8n.pt")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        print("data received on server")

        img_bytes = base64.b64decode(data)
        np_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        print("frame_shape = ",frame.shape)

        results = model(frame)
        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls_id] 

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append({
                    "label": label,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]
                })
                
                print(detections)

        await websocket.send_json({"objects": detections})
        print("data sent from websocker server")

        annotated = results[0].plot()
        cv2.imshow("YOLO", annotated)
        cv2.waitKey(1)