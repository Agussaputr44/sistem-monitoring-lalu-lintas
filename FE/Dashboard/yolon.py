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
    global latest_frame, stream_active
    with frame_lock:
        latest_frame = frame.copy()
        stream_active = True

def generate_frames():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.01)
                continue
            ret, buffer = cv2.imencode('.jpg', latest_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.03)

@app_stream.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app_stream.route('/stream_status')
def stream_status():
    global stream_active, latest_frame
    return jsonify({
        'status': 'active' if stream_active else 'inactive',
        'resolution': latest_frame.shape[:2] if latest_frame is not None else None
    })

def start_stream_server(port=5001):
    app_stream.run(host='0.0.0.0', port=port, threaded=True, debug=False, use_reloader=False)

# ===== YOLO MODEL =====
model_yolo = YOLO("yolov8s.pt")  # Lebih akurat dari nano

# ===== VEHICLE CONFIG =====
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
                json=data, timeout=2
            )
            return response.status_code in [200, 201], response.text
        except Exception as e:
            return False, str(e)

# ===== API WORKER =====
def api_worker(app):
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
    except:
        return False

# ===== HELPER FUNCTIONS =====
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
    import random
    variation = random.uniform(-5,5)
    speed = base_speed * (1 + perspective_factor*0.3) + variation
    return max(15, min(80, speed))

# ===== MAIN DETECTION =====
def run_instant_detection(app):
    # ===== RTSP THREAD + FRAME QUEUE =====
    RTSP_URL = "rtsp://admin:Bengkalis12@192.168.1.64:554/stream1"
    frame_queue = Queue(maxsize=5)
    stop_event = threading.Event()

    def rtsp_reader(url):
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.5)
                continue
            if frame_queue.full():
                try: frame_queue.get_nowait()
                except: pass
            frame_queue.put(frame)
        cap.release()

    threading.Thread(target=rtsp_reader, args=(RTSP_URL,), daemon=True).start()
    app.append_log("✅ RTSP reader started")

    # ===== Streaming =====
    threading.Thread(target=start_stream_server, args=(5001,), daemon=True).start()
    app.append_log("🎥 Stream server aktif: http://localhost:5001/video_feed")

    # ===== API WORKERS =====
    for i in range(3):
        threading.Thread(target=api_worker, args=(app,), daemon=True).start()

    track_frame_count = defaultdict(int)
    counted_ids = set()
    vehicle_counter = {v:0 for v in vehicle_classes}
    data_records = []
    frame_count = 0

    while app.running:
        if frame_queue.empty():
            time.sleep(0.01)
            continue
        frame = frame_queue.get()
        frame_count +=1
        h, w = frame.shape[:2]
        # Resize untuk inference saja
        target_h_inf = 480
        target_w_inf = int(w * target_h_inf / h)
        frame_inf = cv2.resize(frame, (target_w_inf, target_h_inf))

        # YOLOv8s track (half precision untuk GPU)
        results = model_yolo.track(
    frame_inf,
    persist=True,
    conf=0.25,
    iou=0.4,
    tracker="bytetrack.yaml",
    verbose=False,
    device='cpu',  # <--- pakai CPU
    half=False      # CPU tidak bisa half precision
    )[0]


        detected_count = 0
        current_ids = set()

        if results.boxes is not None:
            for box in results.boxes:
                track_id = int(box.id[0]) if box.id is not None else None
                if track_id is None: continue
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model_yolo.names[cls_id]

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Scale ke frame asli
                x1 = int(x1 * w / target_w_inf)
                y1 = int(y1 * h / target_h_inf)
                x2 = int(x2 * w / target_w_inf)
                y2 = int(y2 * h / target_h_inf)
                bw, bh = x2-x1, y2-y1
                area = bw*bh

                if class_name=='truck':
                    class_name = classify_truck_or_pickup(bw,bh,area)
                if class_name not in vehicle_classes:
                    continue
                if area < vehicle_classes[class_name]['min_area'] or conf < vehicle_classes[class_name]['min_conf']:
                    continue

                detected_count +=1
                current_ids.add(track_id)
                track_frame_count[track_id] +=1

                if track_id not in counted_ids and track_frame_count[track_id]>=3:
                    counted_ids.add(track_id)
                    vehicle_counter[class_name] +=1
                    y_center = (y1+y2)//2
                    speed = estimate_speed_simple(area, y_center, h)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    data_records.append([vehicle_classes[class_name]['name'], round(speed,1), timestamp, round(conf,2), track_id])
                    app.append_log(f"COUNTED #{len(data_records)}: {vehicle_classes[class_name]['name']} @ {speed:.1f} km/h (ID:{track_id})")
                    app.update_vehicle_count(vehicle_counter)
                    if api_queue.qsize()<200:
                        api_queue.put_nowait({"vehicle_type":vehicle_classes[class_name]['name'],
                                              "speed":speed,"timestamp":timestamp,
                                              "track_id":track_id,"confidence":conf})

                # Draw bbox
                if track_id in counted_ids: color=(0,255,0); status="COUNTED"
                elif track_frame_count[track_id]>=2: color=(0,165,255); status=f"READY ({track_frame_count[track_id]}/3)"
                else: color=(255,255,0); status=f"NEW ({track_frame_count[track_id]}/3)"
                cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)
                cv2.putText(frame,f"ID:{track_id} {vehicle_classes[class_name]['name']} - {status}",(x1,y1-25),cv2.FONT_HERSHEY_SIMPLEX,0.5,color,2)
                cv2.putText(frame,f"Conf:{conf:.2f}",(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.4,color,1)

        # Cleanup
        for tid in list(track_frame_count.keys()):
            if tid not in current_ids and tid not in counted_ids:
                if track_frame_count[tid]<3: del track_frame_count[tid]

        # Overlay info
        info_text = f"Frame:{frame_count} | Active:{detected_count} | COUNTED:{len(counted_ids)}"
        cv2.putText(frame,info_text,(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
        counter_text = f"Mobil:{vehicle_counter.get('car',0)} Motor:{vehicle_counter.get('motorcycle',0)} Pickup:{vehicle_counter.get('pickup',0)} Bus:{vehicle_counter.get('bus',0)}"
        cv2.putText(frame,counter_text,(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,0),2)

        # Update ke stream
        update_frame_for_stream(frame)
        cv2.imshow("Vehicle Detection", frame)
        if cv2.waitKey(1)&0xFF==27:
            app.stop_detection()
            break

    stop_event.set()
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
        self.vehicle_counter = {v:0 for v in vehicle_classes}
        self.api_manager = APIManager()
        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        title = ttk.Label(main_frame,text="Vehicle Detection System + Live Stream",font=("Helvetica",18,"bold"))
        title.pack(pady=10)
        subtitle = ttk.Label(main_frame,text="Stream: http://localhost:5001/video_feed", font=("Helvetica",10), foreground="blue")
        subtitle.pack()
        self.count_label = ttk.Label(main_frame,text="Belum ada kendaraan terdeteksi",font=("Helvetica",12,"bold"))
        self.count_label.pack(pady=15)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame,text="▶ Start",command=self.start_detection,width=15).pack(side=tk.LEFT,padx=5)
        ttk.Button(btn_frame,text="⏹ Stop",command=self.stop_detection,width=15).pack(side=tk.LEFT,padx=5)
        ttk.Button(btn_frame,text="💾 Save",command=self.save_data,width=15).pack(side=tk.LEFT,padx=5)
        ttk.Button(btn_frame,text="🗑 Clear Log",command=self.clear_log,width=15).pack(side=tk.LEFT,padx=5)
        log_frame = ttk.LabelFrame(main_frame,text="Log Deteksi",padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.txt_log = scrolledtext.ScrolledText(log_frame,width=90,height=20,font=("Consolas",9))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def start_detection(self):
        if self.running: messagebox.showinfo("Info","Detection sudah berjalan"); return
        self.running=True; self.txt_log.delete("1.0",tk.END); self.vehicle_counter={v:0 for v in vehicle_classes}; self.vehicle_data=[]
        self.update_vehicle_count(self.vehicle_counter)
        threading.Thread(target=run_instant_detection,args=(self,),daemon=True).start()
        self.append_log("=== DETECTION STARTED ==="); self.append_log("🎥 Video stream: http://localhost:5001/video_feed"); self.append_log("🌐 Buka di browser untuk melihat live stream!")

    def stop_detection(self):
        if not self.running: messagebox.showinfo("Info","Detection tidak berjalan"); return
        self.running=False; self.append_log("Stopping detection...")

    def clear_log(self): self.txt_log.delete("1.0",tk.END)
    def append_log(self,message): self.txt_log.insert(tk.END,f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"); self.txt_log.see(tk.END)
    def update_vehicle_count(self,counter):
        text="Kendaraan Terdeteksi:\n"; total=0
        for k,v in counter.items():
            if v>0: text+=f"{vehicle_classes[k]['name']}: {v}  "; total+=v
        text+=f"\n\nTOTAL: {total} kendaraan"; self.count_label.config(text=text)
    def save_data(self):
        if not self.vehicle_data: messagebox.showwarning("Warning","Tidak ada data"); return
        try:
            df=pd.DataFrame(self.vehicle_data,columns=["Vehicle","Speed","Time","Confidence","ID"])
            filename=f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename,index=False)
            messagebox.showinfo("Success",f"Data disimpan: {filename}")
            self.append_log(f"💾 Data saved: {filename}")
        except Exception as e: messagebox.showerror("Error",str(e))

# ===== MAIN =====
if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDetectionApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.running=False
        print("App terminated")
