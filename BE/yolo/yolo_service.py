import cv2
import threading
import time
from datetime import datetime
from collections import defaultdict
from queue import Queue
import requests
import os
import random
import numpy as np 

from ultralytics import YOLO
from fastapi import FastAPI
from fastapi.responses import StreamingResponse


# ===== QUEUE & API MANAGER =====
api_queue = Queue()

# Queue untuk menampung frame hasil deteksi yang akan di-stream
stream_queue = Queue(maxsize=5) 

class APIManager:
    """Mengelola pengiriman data deteksi ke API backend."""
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def send_vehicle_data(self, vehicle_type, speed, timestamp, track_id=0, confidence=0):
        try:
            data = {
                'vehicle_type': vehicle_type,
                'speed': round(speed, 1),
                'detected_at': timestamp,
                'location': 'Bengkalis Traffic Cam',
                'confidence': round(confidence, 2),
                'track_id': track_id
            }
            response = self.session.post(
                f"{self.base_url}/vehicle-detections",
                json=data,
                timeout=2
            )
            return response.status_code in [200, 201], response.text
        except Exception as e:
            return False, str(e)

# ===== FASTAPI APP =====
app = FastAPI(title="Vehicle Detection API Worker")

app.running = True
app.api_manager = APIManager(base_url="http://localhost:8000/api")
app.log_buffer = []

def append_log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    app.log_buffer.append(log_msg)
    if len(app.log_buffer) > 100:
        app.log_buffer.pop(0)
    print(log_msg)

app.append_log = append_log

# ===== YOLO MODEL & CLASSIFICATION LOGIC =====

def load_yolo_model():
    """Fungsi untuk memuat model YOLO dengan penanganan unduh otomatis."""
    model_name = "yolov8s.pt"
    try:
        append_log(f"Mencoba memuat model: {model_name}")
        model = YOLO(model_name)
        return model
    except RuntimeError as e:
        append_log(f"Gagal memuat model ({model_name}). Detail Error: {str(e)}")
        
        try:
            append_log(f"Mencoba mengunduh ulang model {model_name}...")
            if os.path.exists(model_name):
                os.remove(model_name)
                append_log(f"File {model_name} lama dihapus.")

            model = YOLO(model_name) 
            append_log(f"Model {model_name} berhasil diunduh dan dimuat.")
            return model
        except Exception as retry_e:
            append_log(f"Gagal total memuat dan mengunduh model {model_name}. Error: {str(retry_e)}")
            raise SystemExit(1)

model_yolo = load_yolo_model()

vehicle_classes = {
    'car': {'name': 'Mobil', 'min_conf': 0.25, 'min_area': 600}, 
    'motorcycle': {'name': 'Motor', 'min_conf': 0.25, 'min_area': 250},
    'bicycle': {'name': 'Sepeda', 'min_conf': 0.30, 'min_area': 150},
    'bus': {'name': 'Bus', 'min_conf': 0.25, 'min_area': 1500},
    'truck': {'name': 'Truk', 'min_conf': 0.25, 'min_area': 1000},
    'pickup': {'name': 'Pickup', 'min_conf': 0.25, 'min_area': 700},
}

def classify_truck_or_pickup(w, h, area):
    ar = w / h if h > 0 else 0
    if area < 15000 or (area < 20000 and ar > 1.2):
        return 'pickup'
    if area >= 20000:
        return 'truck'
    return 'pickup'

def estimate_speed_simple(area, y_pos, frame_h):
    perspective_factor = (frame_h - y_pos) / frame_h
    if area > 20000: base_speed = 25
    elif area > 10000: base_speed = 35
    elif area > 5000: base_speed = 45
    else: base_speed = 55
    variation = random.uniform(-5, 5)
    speed = base_speed * (1 + perspective_factor * 0.3) + variation
    return max(15, min(80, speed))

# ===== DETECTION THREAD =====
def run_detection(rtsp_url: str):
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        append_log(f"Gagal membuka RTSP: {rtsp_url}")
        return

    track_frame_count = defaultdict(int)
    counted_ids = set()
    last_speed = {}
    
    append_log("Deteksi RTSP dimulai...")

    while app.running:
        ret, frame = cap.read()
        if not ret:
            append_log("Frame gagal dibaca, mencoba ulang...")
            time.sleep(0.5)
            continue
        
        h, w = frame.shape[:2]
        target_h_inf = 480
        target_w_inf = int(w * target_h_inf / h)
        frame_inf = cv2.resize(frame, (target_w_inf, target_h_inf))
        
        results = model_yolo.track(
            frame_inf,
            persist=True,
            conf=0.25,
            iou=0.4,
            tracker="bytetrack.yaml",
            verbose=False,
            device='cpu',
            half=False
        )[0]

        current_ids = set()
        if results.boxes is not None:
            for box in results.boxes:
                track_id = int(box.id[0]) if box.id is not None else None
                if track_id is None:
                    continue
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model_yolo.names[cls_id]

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Scale kembali ke ukuran frame asli
                x1 = int(x1 * w / target_w_inf)
                y1 = int(y1 * h / target_h_inf)
                x2 = int(x2 * w / target_w_inf)
                y2 = int(y2 * h / target_h_inf)
                bw, bh = x2 - x1, y2 - y1
                area = bw * bh

                # Klasifikasi truck vs pickup
                if class_name == 'truck':
                    class_name = classify_truck_or_pickup(bw, bh, area)
                if class_name not in vehicle_classes:
                    continue
                if area < vehicle_classes[class_name]['min_area'] or conf < vehicle_classes[class_name]['min_conf']:
                    continue

                current_ids.add(track_id)
                track_frame_count[track_id] += 1
                
                # Hitung kecepatan setiap frame
                y_center_current = (y1 + y2) // 2
                current_speed = estimate_speed_simple(area, y_center_current, h)
                last_speed[track_id] = current_speed
                
                # Gambar anotasi
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{vehicle_classes[class_name]['name']} {current_speed:.1f} km/h (ID:{track_id})"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Logika pengiriman data ke API
                if track_id not in counted_ids and track_frame_count[track_id] >= 3:
                    counted_ids.add(track_id)
                    timestamp = datetime.now().isoformat()

                    data = {
                        "vehicle_type": vehicle_classes[class_name]['name'],
                        "speed": current_speed,
                        "timestamp": timestamp,
                        "track_id": track_id,
                        "confidence": conf
                    }
                    api_queue.put(data)

                    append_log(f"Deteksi: {data['vehicle_type']} | {current_speed:.1f} km/h | ID: {track_id}")

        # Cleanup tracker yang hilang
        for tid in list(track_frame_count.keys()):
            if tid not in current_ids and tid not in counted_ids:
                if track_frame_count[tid] < 3:
                    del track_frame_count[tid]
        
        # Masukkan Frame ke Stream Queue (untuk MJPEG)
        try:
            # Mengubah frame menjadi byte JPEG (kualitas 70)
            ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70]) 
            if ret:
                # Bersihkan queue jika penuh
                if stream_queue.full():
                    stream_queue.get_nowait()
                stream_queue.put(jpeg.tobytes())
        except Exception as e:
            append_log(f"Stream Queue Error: {str(e)}")

        time.sleep(0.01)

    cap.release()
    append_log("Deteksi RTSP dihentikan.")

# ===== API WORKER =====
def api_worker():
    """Worker thread untuk kirim data ke API - batch processing"""
    batch = []
    batch_size = 10
    last_send_time = time.time()
    
    append_log("API Worker dimulai...")

    while app.running or not api_queue.empty():
        try:
            # Ambil data dari queue
            try:
                data = api_queue.get(timeout=0.5)
                batch.append(data)
                api_queue.task_done()
            except:
                pass
            
            current_time = time.time()
            should_send = (
                len(batch) >= batch_size or 
                (len(batch) > 0 and current_time - last_send_time > 2)
            )
            
            if should_send and batch:
                success_count = 0
                failed_data = []

                for data in batch:
                    try:
                        success, resp = app.api_manager.send_vehicle_data(
                            data["vehicle_type"], data["speed"], data["timestamp"],
                            data["track_id"], data["confidence"]
                        )
                        if success:
                            success_count += 1
                        else:
                            failed_data.append(data)
                            append_log(f"API Gagal: {resp}")
                    except Exception as e:
                        failed_data.append(data)
                        append_log(f"API Error: {str(e)}")

                if success_count > 0:
                    append_log(f"API: {success_count}/{len(batch)} data terkirim")

                batch = failed_data
                last_send_time = current_time
                time.sleep(0.1)
                
        except Exception as e:
            append_log(f"API Worker Error: {str(e)}")
            time.sleep(1)

    # Kirim sisa data saat shutdown
    if batch:
        append_log(f"Mengirim {len(batch)} data tersisa saat shutdown...")
        for data in batch:
            try:
                app.api_manager.send_vehicle_data(
                    data["vehicle_type"], data["speed"], data["timestamp"],
                    data["track_id"], data["confidence"]
                )
            except:
                pass

    append_log("API Worker dihentikan.")

# ===== START DETECTION & WORKER =====
def start_background_tasks():
    RTSP_URL = "rtsp://admin:Bengkalis12@192.168.1.64:554/stream1"
    
    threading.Thread(target=run_detection, args=(RTSP_URL,), daemon=True).start()
    threading.Thread(target=api_worker, daemon=True).start()

# ===== FASTAPI LIFECYCLE & ENDPOINTS =====
@app.on_event("startup")
def startup_event():
    start_background_tasks()
    append_log("Aplikasi deteksi kendaraan dimulai.")

@app.on_event("shutdown")
def shutdown_event():
    app.running = False
    append_log("Menghentikan semua thread...")
    time.sleep(3)

# Endpoint untuk cek status
@app.get("/status")
def get_status():
    return {
        "status": "running",
        "queue_size": api_queue.qsize(),
        "log": app.log_buffer[-20:]
    }

@app.get("/")
def root():
    return {"message": "Vehicle Detection Worker API - Running in background"}

# ===== ENDPOINT VIDEO FEED MJPEG =====
def frame_generator():
    """Generator yang menghasilkan frame JPEG dari stream_queue."""
    while True:
        try:
            # Ambil frame dari queue
            frame_bytes = stream_queue.get(timeout=0.5) 
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )
        except Exception:
            # Lanjut ke loop berikutnya jika queue kosong
            continue

@app.get("/video_feed")
def video_feed():
    """Endpoint untuk menyajikan video feed MJPEG."""
    # Menghasilkan response streaming dengan Content-Type khusus MJPEG
    return StreamingResponse(
        frame_generator(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )