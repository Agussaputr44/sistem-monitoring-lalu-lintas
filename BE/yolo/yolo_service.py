import cv2
import threading
import time
import requests
import os
import random
import yt_dlp
import numpy as np
from datetime import datetime
from collections import defaultdict
from queue import Queue
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from ultralytics import YOLO

# ==========================================
# 1. CONFIGURATION
# ==========================================
class Config:
    MODEL_NAME = "yolov8s.pt"
    
    # Sumber Video (YouTube / RTSP / File)
    VIDEO_SOURCE = "https://youtu.be/r537Vt_U3_0" 
    
    # Url API
    API_BASE_URL = "http://127.0.0.1:8000/api" 
    
    TARGET_HEIGHT = 480
    
    # Konfigurasi per kendaraan 
    VEHICLE_CLASSES = {
        'car': {'name': 'Mobil', 'min_conf': 0.40, 'min_area': 800, 'color': (255, 100, 0)},
        'motorcycle': {'name': 'Motor', 'min_conf': 0.35, 'min_area': 300, 'color': (0, 255, 255)},
        'bus': {'name': 'Bus', 'min_conf': 0.45, 'min_area': 2500, 'color': (0, 0, 255)},
        'truck': {'name': 'Truk', 'min_conf': 0.45, 'min_area': 1800, 'color': (0, 0, 150)},
        'pickup': {'name': 'Pickup', 'min_conf': 0.40, 'min_area': 1000, 'color': (0, 165, 255)},
    }

# ==========================================
# 2. UTILITY & LOGIC CLASSES
# ==========================================
class VideoSourceManager:
    @staticmethod
    def get_url(source):
        if "youtube.com" in source or "youtu.be" in source:
            ydl_opts = {'format': 'best[ext=mp4]/best', 'quiet': True, 'no_warnings': True}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(source, download=False)
                    return info['url']
            except Exception as e:
                print(f"YouTube Error: {e}")
                return None
        return source

class VehicleDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.track_history = defaultdict(int)
        self.counted_ids = set()

    def classify_type(self, label, w, h):
        area = w * h
        aspect_ratio = w / h if h > 0 else 0
        
        if label == 'truck':
            if area < 25000: 
                return 'pickup'
            return 'truck'
        
        if label == 'car':
            if aspect_ratio > 1.8 and area > 15000:
                return 'pickup'
            return 'car'
            
        return label

    def estimate_speed(self, area, y_pos, frame_h):
        perspective = (frame_h - y_pos) / frame_h
        base = 30 if area > 20000 else 45
        speed = base * (1 + perspective * 0.4) + random.uniform(-3, 3)
        return max(10, min(100, speed))

# ==========================================
# 3. FASTAPI SETUP
# ==========================================
app = FastAPI(title="Bengkalis Traffic Intelligence")
api_queue = Queue()
stream_queue = Queue(maxsize=10)
running_flag = {"is_active": True}

class APIManager:
    def __init__(self, base_url):
        self.session = requests.Session()
        self.url = f"{base_url}/vehicle-detections"

    def send(self, data):
        try:
            res = self.session.post(self.url, json=data, timeout=3)
            if res.status_code == 422:
                print(f"Validation Error (422): {res.json()}")
            return res.status_code in [200, 201]
        except Exception as e:
            print(f"API Error: {e}")
            return False

api_manager = APIManager(Config.API_BASE_URL)

def draw_styled_bbox(img, x1, y1, x2, y2, label, conf, speed, color):
    """Menggambar Bounding Box yang rapi dengan label background."""
    # Main BBox
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    
    # Label Text
    text = f"{label} {speed:.1f} km/h"
    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 0.6
    thickness = 1
    
    (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Draw Background Box for Text
    cv2.rectangle(img, (x1, y1 - th - 10), (x1 + tw + 10, y1), color, -1)
    
    # Draw Text
    cv2.putText(img, text, (x1 + 5, y1 - 7), font, font_scale, (255, 255, 255), thickness)

# ==========================================
# 4. BACKGROUND LOOPS
# ==========================================
def detection_loop():
    while running_flag["is_active"]:
        source_url = VideoSourceManager.get_url(Config.VIDEO_SOURCE)
        if not source_url:
            time.sleep(5); continue

        cap = cv2.VideoCapture(source_url)
        detector = VehicleDetector(Config.MODEL_NAME)

        while running_flag["is_active"]:
            ret, frame = cap.read()
            if not ret: break

            h, w = frame.shape[:2]
            frame_resized = cv2.resize(frame, (int(w * Config.TARGET_HEIGHT / h), Config.TARGET_HEIGHT))
            
            # Run YOLO
            results = detector.model.track(frame_resized, persist=True, conf=0.3, verbose=False)[0]

            if results.boxes is not None:
                for box in results.boxes:
                    if box.id is None: continue
                    
                    tid = int(box.id[0])
                    cls_name = detector.model.names[int(box.cls[0])]
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Klasifikasi Ulang (Pickup vs Truk)
                    v_type = detector.classify_type(cls_name, x2-x1, y2-y1)
                    
                    if v_type not in Config.VEHICLE_CLASSES: continue
                    cfg = Config.VEHICLE_CLASSES[v_type]

                    # Filter noise
                    if conf < cfg['min_conf']: continue

                    # Scaling Koordinat ke Frame Asli
                    scale_x, scale_y = w / frame_resized.shape[1], h / frame_resized.shape[0]
                    orig_x1, orig_y1 = int(x1 * scale_x), int(y1 * scale_y)
                    orig_x2, orig_y2 = int(x2 * scale_x), int(y2 * scale_y)

                    speed = detector.estimate_speed((x2-x1)*(y2-y1), (y1+y2)//2, Config.TARGET_HEIGHT)

                    # Tampilkan BBox di Stream
                    draw_styled_bbox(frame, orig_x1, orig_y1, orig_x2, orig_y2, 
                                     cfg['name'], conf, speed, cfg['color'])

                    # Counter & Kirim API
                    detector.track_history[tid] += 1
                    if tid not in detector.counted_ids and detector.track_history[tid] >= 4:
                        detector.counted_ids.add(tid)
                        api_queue.put({
                            "vehicle_type": cfg['name'],
                            "speed_kmph": round(speed, 1),
                            "confidence": round(conf, 2),
                            "track_id": tid,
                            "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "location": "Bengkalis Main Road"
                        })

            # MJPEG Stream
            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if stream_queue.full(): stream_queue.get()
            stream_queue.put(jpeg.tobytes())

        cap.release()
        time.sleep(2)

def api_worker_loop():
    while running_flag["is_active"]:
        if not api_queue.empty():
            data = api_queue.get()
            api_manager.send(data)
            api_queue.task_done()
        time.sleep(0.1)

# ==========================================
# 5. ROUTES
# ==========================================
@app.on_event("startup")
def startup():
    threading.Thread(target=detection_loop, daemon=True).start()
    threading.Thread(target=api_worker_loop, daemon=True).start()

@app.get("/video_feed")
def video_feed():
    def gen():
        while True:
            if not stream_queue.empty():
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + stream_queue.get() + b'\r\n')
            else:
                time.sleep(0.01)
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/")
def index():
    return {"status": "running", "counted": len(api_queue.queue)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)