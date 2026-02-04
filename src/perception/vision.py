import cv2
import os
from ultralytics import YOLO
from ..schema import PerceptionState, Entity
from datetime import datetime
import threading
import time

class VisionEngine:
    def __init__(self):
        # Load YOLOv8 model (lightweight nano version)
        print("[VISION] Loading YOLOv8n model...")
        self.model = YOLO('yolov8n.pt') 
        print("[VISION] Model loaded. Opening webcam (DirectShow)...")
        # Use CAP_DSHOW for better performance/stability on Windows
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
        if not self.cap.isOpened():
            # Fallback to default index if DirectShow fails
            self.cap = cv2.VideoCapture(0)
            
        if not self.cap.isOpened():
            print("[ERROR] Could not open webcam. Ensure no other apps are using it.")
        else:
            print("[VISION] Webcam opened successfully.")
        self.latest_frame = None
        self.running = False
        self.detections = []
        self.lock = threading.Lock()
        self.snapshot_dir = "snapshots"
        self.last_snapshot_path = None
        os.makedirs(self.snapshot_dir, exist_ok=True)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.1)
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
        finally:
            self.cap.release()
            print("[VISION] Webcam released.")

    def get_perception_state(self, sensor_data: dict) -> PerceptionState:
        with self.lock:
            entities = self.detections.copy()
            frame = self.latest_frame.copy() if self.latest_frame is not None else None
            
        # Detect anomaly: Person or unknown dense object in frame
        anomaly = any(e.label in ['person', 'cell phone', 'scissors'] for e in entities)
        
        return PerceptionState(
            timestamp=datetime.now(),
            entities=entities,
            sensor_data=sensor_data,
            anomalies_detected=anomaly
        )

    def capture_snapshot(self) -> str:
        with self.lock:
            if self.latest_frame is None:
                return ""
            frame = self.latest_frame.copy()
        
        filename = f"snapshot_{int(time.time())}.jpg"
        filepath = os.path.join(self.snapshot_dir, filename)
        cv2.imwrite(filepath, frame)
        self.last_snapshot_path = filepath
        print(f"[VISION] Snapshot saved: {filepath}")
        return filepath

    def stop(self):
        self.running = False
        self.cap.release()
