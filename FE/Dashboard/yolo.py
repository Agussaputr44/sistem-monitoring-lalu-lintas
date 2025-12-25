import cv2
import numpy as np
import tkinter as tk
import threading
import requests
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime
import pandas as pd
from ultralytics import YOLO
import time
from queue import Queue
from collections import defaultdict
from flask import Flask, Response, jsonify
from flask_cors import CORS

# ===== FLASK STREAMING SETUP =====
app_stream = Flask(__name__)
CORS(app_stream)

latest_frame = None
frame_lock = threading.Lock()
stream_active = False

def update_frame_for_stream(frame):
    """Update frame untuk streaming"""
    global latest_frame, stream_active
    with frame_lock:
        latest_frame = frame.copy()
        stream_active = True

def generate_frames():
    """Generator untuk streaming video"""
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.1)
                continue
            
            ret, buffer = cv2.imencode('.jpg', latest_frame, 
                                      [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.03)  # ~30 FPS

@app_stream.route('/video_feed')
def video_feed():
    """Endpoint streaming video"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app_stream.route('/stream_status')
def stream_status():
    """Check status streaming"""
    global stream_active, latest_frame
    return jsonify({
        'status': 'active' if stream_active else 'inactive',
        'resolution': latest_frame.shape[:2] if latest_frame is not None else None
    })

def start_stream_server(port=5001):
    """Start Flask streaming server"""
    app_stream.run(host='0.0.0.0', port=port, threaded=True, debug=False, use_reloader=False)

# ===== MODEL YOLO =====
model_yolo = YOLO("yolov8s.pt")

# ===== KONFIGURASI KENDARAAN =====
vehicle_classes = {
    'car': {'name': 'Mobil', 'min_conf': 0.25, 'min_area': 600}, 
    'motorcycle': {'name': 'Motor', 'min_conf': 0.25, 'min_area': 250},
    'bicycle': {'name': 'Sepeda', 'min_conf': 0.30, 'min_area': 150},
    'bus': {'name': 'Bus', 'min_conf': 0.25, 'min_area': 1500},
    'truck': {'name': 'Truk', 'min_conf': 0.25, 'min_area': 1000},
    'pickup': {'name': 'Pickup', 'min_conf': 0.25, 'min_area': 700},
}

api_queue = Queue()

# ===== API MANAGER =====
class APIManager:
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

# ===== API WORKER =====
def api_worker(app):
    """Batch processing API"""
    batch = []
    batch_size = 50
    last_send_time = time.time()
    retry_batch = []
    
    while app.running or not api_queue.empty():
        try:
            try:
                data = api_queue.get(timeout=0.3)
                batch.append(data)
                api_queue.task_done()
            except:
                pass
            
            current_time = time.time()
            should_send = (len(batch) >= batch_size or 
                          (len(batch) > 0 and current_time - last_send_time > 1.0))
            
            if should_send and batch:
                success = send_batch_to_api(app, batch)
                
                if success:
                    app.append_log(f"✅ API Batch: {len(batch)} data terkirim")
                    batch = []
                else:
                    retry_batch.extend(batch[:20])
                    app.append_log(f"⚠ API Failed, {len(retry_batch)} di retry queue")
                    batch = []
                
                last_send_time = current_time
                time.sleep(0.05)
            
            if len(retry_batch) > 0 and current_time - last_send_time > 3.0:
                if send_batch_to_api(app, retry_batch):
                    app.append_log(f"♻ Retry Success: {len(retry_batch)} data")
                    retry_batch = []
                
        except Exception as e:
            app.append_log(f"⚠ API Worker Error: {str(e)}")
            continue
    
    if batch:
        send_batch_to_api(app, batch)
    if retry_batch:
        send_batch_to_api(app, retry_batch)

def send_batch_to_api(app, batch):
    """Kirim data batch ke API"""
    if not batch:
        return True
        
    try:
        batch_data = [{
            'vehicle_type': item['vehicle_type'],
            'speed': round(item['speed'], 1),
            'detected_at': item['timestamp'],
            'location': 'Bengkalis Traffic Cam',
            'confidence': round(item['confidence'], 2),
            'track_id': item['track_id']
        } for item in batch]
        
        response = app.api_manager.session.post(
            f"{app.api_manager.base_url}/vehicle-detections/batch",
            json={'detections': batch_data},
            timeout=5
        )
        
        return response.status_code in [200, 201]
        
    except requests.exceptions.Timeout:
        app.append_log("⏱ API Timeout - server lambat")
        return False
    except requests.exceptions.ConnectionError:
        app.append_log("🔌 Koneksi API terputus")
        return False
    except Exception as e:
        app.append_log(f"❌ Send Batch Error: {str(e)}")
        return False

# ===== HELPER FUNCTIONS =====
def classify_truck_or_pickup(bbox_width, bbox_height, bbox_area):
    """Bedakan Pickup vs Truck berdasarkan ukuran"""
    aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0
    
    if bbox_area < 15000:
        return 'pickup'
    
    if bbox_area < 20000 and aspect_ratio > 1.2:
        return 'pickup'
    
    if bbox_area >= 20000:
        return 'truck'
    
    return 'pickup'

def estimate_speed_simple(bbox_area, y_position, frame_height):
    """Estimasi kecepatan sederhana"""
    perspective_factor = (frame_height - y_position) / frame_height
    
    if bbox_area > 20000:
        base_speed = 25
    elif bbox_area > 10000:
        base_speed = 35
    elif bbox_area > 5000:
        base_speed = 45
    else:
        base_speed = 55
    
    estimated_speed = base_speed * (1 + perspective_factor * 0.3)
    
    import random
    variation = random.uniform(-5, 5)
    
    return max(15, min(80, estimated_speed + variation))

from queue import Queue
def run_instant_detection(app):
    """Realtime vehicle detection + live streaming (YOLOv8s 720p optimal)"""
    import os
    import threading
    import time
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
        "rtsp_transport;tcp|max_delay;500000|stimeout;5000000|loglevel;error"
    )

    # ==================== RTSP Reader Thread ====================
    RTSP_URL = "rtsp://admin:Bengkalis12@192.168.1.64:554/stream2"
    frame_queue = Queue(maxsize=5)
    stop_rtsp = threading.Event()

    def rtsp_reader(url):
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        reconnect_attempts = 0
        while not stop_rtsp.is_set():
            ret, frame = cap.read()
            if not ret:
                reconnect_attempts += 1
                time.sleep(2)
                cap.release()
                cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                if reconnect_attempts > 5:
                    app.append_log("❌ RTSP gagal reconnect, keluar.")
                    stop_rtsp.set()
                continue
            reconnect_attempts = 0
            if frame_queue.full():
                try:
                    frame_queue.get_nowait()
                except:
                    pass
            frame_queue.put(frame)
        cap.release()

    threading.Thread(target=rtsp_reader, args=(RTSP_URL,), daemon=True).start()
    app.append_log("✅ RTSP reader thread started")

    # ==================== Streaming Server ====================
    stream_thread = threading.Thread(target=start_stream_server, args=(5001,), daemon=True)
    stream_thread.start()
    app.append_log("🎥 Stream server aktif: http://localhost:5001/video_feed")

    # ==================== API Workers ====================
    num_api_workers = 3
    for i in range(num_api_workers):
        threading.Thread(target=api_worker, args=(app,), daemon=True).start()
    app.append_log(f"🚀 {num_api_workers} API worker dijalankan")

    # ==================== Setup ====================
    track_frame_count = defaultdict(int)
    counted_ids = set()
    vehicle_counter = {v: 0 for v in vehicle_classes}
    data_records = []
    frame_count = 0

    # YOLOv8s model full
    model = YOLO("yolov8s.pt")

    # Bytetrack config optimal
    tracker_config = "bytetrack.yaml"
    # pastikan track_buffer di yaml minimal 60, match_thresh 0.7

    while app.running and not stop_rtsp.is_set():
        if frame_queue.empty():
            time.sleep(0.01)
            continue
        frame = frame_queue.get()
        frame_count += 1

        # Resize untuk inference 720p (lebih akurat)
        frame_height, frame_width = frame.shape[:2]
        target_height_inf = min(720, frame_height)
        target_width_inf = int(frame_width * target_height_inf / frame_height)
        frame_inf = cv2.resize(frame, (target_width_inf, target_height_inf))

        # YOLOv8s tracking
        results = model.track(
            frame_inf,
            persist=True,
            conf=0.20,   # turunkan sedikit supaya lebih sensitif
            iou=0.4,
            tracker=tracker_config,
            verbose=False,
        )[0]

        detected_count = 0
        current_frame_ids = set()

        if results.boxes is not None:
            for box in results.boxes:
                track_id = int(box.id[0]) if box.id is not None else None
                if track_id is None:
                    continue

                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls_id]

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Scale bbox ke frame asli
                scale_x = frame_width / target_width_inf
                scale_y = frame_height / target_height_inf
                x1 = int(x1 * scale_x)
                y1 = int(y1 * scale_y)
                x2 = int(x2 * scale_x)
                y2 = int(y2 * scale_y)

                bbox_width = x2 - x1
                bbox_height = y2 - y1
                bbox_area = bbox_width * bbox_height

                # Bedakan truck/pickup
                if class_name == "truck":
                    class_name = classify_truck_or_pickup(bbox_width, bbox_height, bbox_area)

                if class_name not in vehicle_classes:
                    continue

                # Turunkan min_area supaya lebih sensitif
                min_area = vehicle_classes[class_name]["min_area"] // 2
                min_conf = vehicle_classes[class_name]["min_conf"]

                if bbox_area < min_area or conf < min_conf:
                    continue

                detected_count += 1
                current_frame_ids.add(track_id)
                track_frame_count[track_id] += 1

                # Hitung kendaraan baru
                if track_id not in counted_ids and track_frame_count[track_id] >= 2:
                    counted_ids.add(track_id)
                    vehicle_counter[class_name] += 1

                    y_center = (y1 + y2) // 2
                    speed = estimate_speed_simple(bbox_area, y_center, frame_height)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    data_records.append([
                        vehicle_classes[class_name]["name"],
                        round(speed, 1),
                        timestamp,
                        round(conf, 2),
                        track_id,
                    ])

                    app.append_log(
                        f"COUNTED #{len(data_records)}: "
                        f"{vehicle_classes[class_name]['name']} @ {speed:.1f} km/h (ID:{track_id})"
                    )
                    app.update_vehicle_count(vehicle_counter)

                    if api_queue.qsize() < 200:
                        api_queue.put_nowait({
                            "vehicle_type": vehicle_classes[class_name]["name"],
                            "speed": speed,
                            "timestamp": timestamp,
                            "track_id": track_id,
                            "confidence": conf,
                        })

                # Draw box & label
                if track_id in counted_ids:
                    color = (0, 255, 0)
                    status = "COUNTED"
                elif track_frame_count[track_id] >= 2:
                    color = (0, 165, 255)
                    status = f"READY ({track_frame_count[track_id]}/2)"
                else:
                    color = (255, 255, 0)
                    status = f"NEW ({track_frame_count[track_id]}/2)"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame,
                            f"ID:{track_id} {vehicle_classes[class_name]['name']} - {status}",
                            (x1, y1-25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(frame,
                            f"Conf:{conf:.2f}",
                            (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # Cleanup tracks
        for tid in list(track_frame_count.keys()):
            if tid not in current_frame_ids and tid not in counted_ids:
                if track_frame_count[tid] < 2:
                    del track_frame_count[tid]

        # Overlay info
        info_text = f"Frame: {frame_count} | Active: {detected_count} | COUNTED: {len(counted_ids)}"
        cv2.putText(frame, info_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        counter_text = (f"Mobil:{vehicle_counter.get('car',0)} "
                        f"Motor:{vehicle_counter.get('motorcycle',0)} "
                        f"Pickup:{vehicle_counter.get('pickup',0)} "
                        f"Bus:{vehicle_counter.get('bus',0)}")
        cv2.putText(frame, counter_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Update frame ke stream
        update_frame_for_stream(frame)

        # Show lokal
        cv2.imshow("Vehicle Detection", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            app.stop_detection()
            break

    stop_rtsp.set()
    api_queue.join()
    cv2.destroyAllWindows()
    app.vehicle_data = data_records
    app.append_log(f"✅ Detection selesai! Total: {len(counted_ids)} kendaraan")

# ===== GUI =====
class VehicleDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Detection - Live Stream")
        self.root.geometry("800x600")
        self.running = False
        self.vehicle_data = []
        self.vehicle_counter = {v: 0 for v in vehicle_classes}
        self.api_manager = APIManager()
        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(main_frame, 
                         text="Vehicle Detection System + Live Stream", 
                         font=("Helvetica", 18, "bold"))
        title.pack(pady=10)
        
        subtitle = ttk.Label(main_frame,
                            text="Stream: http://localhost:5001/video_feed", 
                            font=("Helvetica", 10),
                            foreground="blue")
        subtitle.pack()
        
        self.count_label = ttk.Label(main_frame, 
                                    text="Belum ada kendaraan terdeteksi", 
                                    font=("Helvetica", 12, "bold"))
        self.count_label.pack(pady=15)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="▶ Start", 
                  command=self.start_detection, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⏹ Stop", 
                  command=self.stop_detection, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Save", 
                  command=self.save_data, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Clear Log", 
                  command=self.clear_log, width=15).pack(side=tk.LEFT, padx=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="Log Deteksi", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.txt_log = scrolledtext.ScrolledText(log_frame, width=90, height=20,
                                                 font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def start_detection(self):
        if self.running:
            messagebox.showinfo("Info", "Detection sudah berjalan")
            return
        
        self.running = True
        self.txt_log.delete("1.0", tk.END)
        self.vehicle_counter = {v: 0 for v in vehicle_classes}
        self.vehicle_data = []
        self.update_vehicle_count(self.vehicle_counter)
        
        threading.Thread(target=run_instant_detection, args=(self,), daemon=True).start()
        self.append_log("=== DETECTION STARTED ===")
        self.append_log("🎥 Video stream: http://localhost:5001/video_feed")
        self.append_log("🌐 Buka di browser untuk melihat live stream!")

    def stop_detection(self):
        if not self.running:
            messagebox.showinfo("Info", "Detection tidak berjalan")
            return
        self.running = False
        self.append_log("Stopping detection...")

    def clear_log(self):
        self.txt_log.delete("1.0", tk.END)

    def append_log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.txt_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.txt_log.see(tk.END)

    def update_vehicle_count(self, counter):
        text = "Kendaraan Terdeteksi:\n"
        total = 0
        for k, v in counter.items():
            if v > 0:
                text += f"{vehicle_classes[k]['name']}: {v}  "
                total += v
        text += f"\n\nTOTAL: {total} kendaraan"
        self.count_label.config(text=text)

    def save_data(self):
        if not self.vehicle_data:
            messagebox.showwarning("Warning", "Tidak ada data")
            return
        
        try:
            df = pd.DataFrame(self.vehicle_data, 
                            columns=["Vehicle", "Speed", "Time", "Confidence", "ID"])
            filename = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            
            messagebox.showinfo("Success", f"Data disimpan: {filename}")
            self.append_log(f"💾 Data saved: {filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ===== MAIN =====
if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDetectionApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.running = False
        print("App terminated")
