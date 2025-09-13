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
from collections import deque, defaultdict

# -----------------------------
# Model YOLO dan kelas kendaraan
# -----------------------------
model_yolo = YOLO("yolov8n.pt")
vehicle_classes = {
    'bicycle': {'name': 'Sepeda', 'min_conf': 0.6},
    'car': {'name': 'Mobil', 'min_conf': 0.5}, 
    'motorcycle': {'name': 'Motor', 'min_conf': 0.5},
    'truck': {'name': 'Truk', 'min_conf': 0.5},
    'bus': {'name': 'Bus', 'min_conf': 0.5}
}

frame_queue = Queue(maxsize=5)
api_queue = Queue()

# -----------------------------
# API Manager
# -----------------------------
class APIManager:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def send_vehicle_data(self, vehicle_type, speed, timestamp, additional_data=None):
        try:
            data = {
                'vehicle_type': vehicle_type,
                'speed': speed,
                'detected_at': timestamp,
                'location': 'Bengkalis Traffic Cam',
                'confidence': additional_data.get('confidence', 0) if additional_data else 0,
                'track_id': additional_data.get('track_id', 0) if additional_data else 0
            }
            response = requests.post(f"{self.base_url}/vehicle-detections",
                                     json=data, headers=self.headers, timeout=5)
            return response.status_code in [200, 201], response.text
        except requests.exceptions.RequestException as e:
            return False, str(e)

def api_worker(app):
    """Thread terpisah untuk mengirim data ke API"""
    while app.running or not api_queue.empty():
        try:
            data = api_queue.get(timeout=1)
            success, message = app.api_manager.send_vehicle_data(
                data["vehicle_type"], data["speed"], data["detected_at"],
                {'confidence': data.get('confidence',0), 'track_id': data.get('track_id',0)}
            )
            if success:
                app.append_log(f"✅ API: Data {data['vehicle_type']} terkirim")
            else:
                app.append_log(f"❌ API Error: {message}")
            api_queue.task_done()
        except:
            continue

def queue_api_data(vehicle_type, speed, track_id=None, confidence=0):
    """Tambahkan data ke queue API"""
    data = {
        "vehicle_type": vehicle_type,
        "speed": speed,
        "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "track_id": track_id,
        "confidence": confidence
    }
    try:
        api_queue.put_nowait(data)
    except:
        print("⚠️ API Queue penuh, data diabaikan")

# -----------------------------
# Frame Capturing Thread
# -----------------------------
def capture_frames(app, cap):
    while app.running and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        if not frame_queue.full():
            frame_queue.put(frame)
        time.sleep(0.01)

# -----------------------------
# Detection Thread
# -----------------------------
def run_detection(app):
    cap = cv2.VideoCapture("rtsp://admin:Bengkalis12@192.168.1.64:554")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        app.append_log("❌ Gagal membuka kamera RTSP.")
        return

    app.append_log("✅ Kamera berhasil dibuka.")
    threading.Thread(target=api_worker, args=(app,), daemon=True).start()
    threading.Thread(target=capture_frames, args=(app, cap), daemon=True).start()
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    scale_factor = float(app.scale_var.get()) if app.scale_var.get().replace('.','').isdigit() else 100
    track_history = defaultdict(lambda: {'positions': deque(maxlen=10), 'timestamps': deque(maxlen=10)})
    counted_ids = set()
    vehicle_counter = {v: 0 for v in vehicle_classes}
    data_records = []

    while app.running:
        if frame_queue.empty():
            time.sleep(0.01)
            continue

        frame = frame_queue.get()
        frame = cv2.resize(frame, (640, 480))

        results = model_yolo.track(frame, persist=True)[0]
        for box in results.boxes:
            if box.id is None: continue
            track_id = int(box.id[0])
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = model_yolo.names[cls_id]
            if class_name not in vehicle_classes: continue
            min_conf = vehicle_classes[class_name]['min_conf']
            if conf < min_conf: continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = (x1+x2)//2, (y1+y2)//2

            # Update history
            hist = track_history[track_id]
            hist['positions'].append(cy)
            hist['timestamps'].append(time.time())

            # Hitung kecepatan sederhana
            speed = 0
            if len(hist['positions'])>=2:
                dy = abs(hist['positions'][-1]-hist['positions'][-2])
                dt = hist['timestamps'][-1]-hist['timestamps'][-2]
                if dt>0: speed = (dy/scale_factor)/dt*3.6

            # Hitung hanya sekali
            if track_id not in counted_ids:
                counted_ids.add(track_id)
                vehicle_counter[class_name] +=1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data_records.append([vehicle_classes[class_name]['name'], round(speed,1), timestamp, conf, track_id])
                app.append_log(f"🚗 {vehicle_classes[class_name]['name']} @ {speed:.1f} km/h")
                app.update_vehicle_count(vehicle_counter)

                # Masukkan ke API queue
                queue_api_data(vehicle_classes[class_name]['name'], speed, track_id, conf)

            color = (0,255,0) if track_id in counted_ids else (255,255,0)
            label = f"ID:{track_id} {vehicle_classes[class_name]['name']} {speed:.1f}km/h ({conf:.2f})"
            cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)
            cv2.putText(frame,label,(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,color,2)

        cv2.imshow("Deteksi Kendaraan", frame)
        if cv2.waitKey(1) & 0xFF==27:
            app.stop_detection()
            break

    api_queue.join()
    cap.release()
    cv2.destroyAllWindows()
    app.vehicle_data = data_records
    app.append_log("🛑 Deteksi selesai.")

# -----------------------------
# Tkinter GUI
# -----------------------------
class VehicleDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deteksi Kendaraan - YOLOv8 + API")
        self.root.geometry("700x650")
        self.running = False
        self.vehicle_data = []
        self.vehicle_counter = {v: 0 for v in vehicle_classes}
        self.api_manager = APIManager()

        # GUI setup
        self.main_frame = ttk.Frame(root,padding=10)
        self.main_frame.pack(fill=tk.BOTH,expand=True)
        ttk.Label(self.main_frame,text="🚦 Sistem Deteksi Kendaraan",font=("Helvetica",16,"bold")).pack(pady=10)

        self.count_label = ttk.Label(self.main_frame,text="Jumlah Kendaraan: -",font=("Helvetica",12))
        self.count_label.pack(pady=5)

        self.scale_var = tk.StringVar(value="100")
        scale_frame = ttk.Frame(self.main_frame)
        scale_frame.pack(pady=5)
        ttk.Label(scale_frame,text="Scale Factor (pixels/meter):").pack(side=tk.LEFT)
        ttk.Entry(scale_frame,textvariable=self.scale_var,width=10).pack(side=tk.LEFT, padx=5)

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame,text="▶ Start",command=self.start_detection).grid(row=0,column=0,padx=5)
        ttk.Button(button_frame,text="⏹ Stop",command=self.stop_detection).grid(row=0,column=1,padx=5)
        ttk.Button(button_frame,text="💾 Simpan Data",command=self.save_data).grid(row=0,column=2,padx=5)

        self.txt_log = scrolledtext.ScrolledText(self.main_frame,width=80,height=20,font=("Courier",10))
        self.txt_log.pack(pady=10)

    def append_log(self,message):
        self.txt_log.after(0,lambda: (self.txt_log.insert(tk.END,f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"), self.txt_log.see(tk.END)))

    def update_vehicle_count(self,counter):
        count_text = "Jumlah Kendaraan:\n" + "\n".join(f"{vehicle_classes[k]['name']}: {v}" for k,v in counter.items() if v>0)
        self.count_label.after(0,lambda: self.count_label.config(text=count_text))

    def start_detection(self):
        if self.running: return
        self.running = True
        self.txt_log.delete("1.0",tk.END)
        self.vehicle_counter = {v:0 for v in vehicle_classes}
        self.update_vehicle_count(self.vehicle_counter)
        threading.Thread(target=run_detection,args=(self,),daemon=True).start()
        self.append_log("🚀 Deteksi dimulai...")

    def stop_detection(self):
        self.running = False
        self.append_log("🛑 Menghentikan deteksi...")

    def save_data(self):
        if not self.vehicle_data:
            messagebox.showwarning("⚠️ Tidak Ada Data","Belum ada data kendaraan untuk disimpan.")
            return
        df = pd.DataFrame(self.vehicle_data,columns=["Jenis","Kecepatan (km/h)","Waktu","Confidence","Track ID"])
        filename = f"data_kendaraan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename,index=False)
        messagebox.showinfo("✅ Berhasil",f"Data berhasil disimpan ke {filename}")

# -----------------------------
# Run GUI
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDetectionApp(root)
    root.mainloop()
