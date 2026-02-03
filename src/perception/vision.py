import cv2
from ultralytics import YOLO
from ..schema import PerceptionState, Entity
from datetime import datetime
import threading
import time

class VisionEngine:
    def __init__(self):
        # Load YOLOv8 model (lightweight nano version)
        self.model = YOLO('yolov8n.pt') 
        self.cap = cv2.VideoCapture(0) # Open default webcam
        self.latest_frame = None
        self.running = False
        self.detections = []
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Run YOLO detection
            results = self.model(frame, verbose=False)
            
            new_detections = []
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    label = self.model.names[cls]
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()
                    
                    new_detections.append(Entity(
                        id=f"{label}_{time.time()}",
                        label=label,
                        confidence=conf,
                        bbox=xyxy
                    ))
            
            with self.lock:
                self.latest_frame = frame
                self.detections = new_detections

    def get_perception_state(self, sensor_data: dict) -> PerceptionState:
        with self.lock:
            entities = self.detections.copy()
            
        # Detect anomaly: Person or unknown dense object in frame
        anomaly = any(e.label in ['person', 'cell phone', 'scissors'] for e in entities)
        
        return PerceptionState(
            timestamp=datetime.now(),
            entities=entities,
            sensor_data=sensor_data,
            anomalies_detected=anomaly
        )

    def stop(self):
        self.running = False
        self.cap.release()
