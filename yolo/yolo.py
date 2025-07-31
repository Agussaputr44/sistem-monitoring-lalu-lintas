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
import json

# Load YOLOv8 model
model_yolo = YOLO("yolo/yolov8n.pt")
vehicle_classes = ["car", "motorcycle", "bus", "truck", "bicycle", "person"]
frame_queue = Queue(maxsize=5)
api_queue = Queue()  # Queue untuk antrian API requests

# Konfigurasi API
API_CONFIG = {
    "url": "http://127.0.0.1:8000/api/logs",
    "timeout": 10,
    "max_retries": 3,
    "retry_delay": 2
}

# -----------------------------
# API Worker Thread
# -----------------------------
def api_worker(app):
    """Thread terpisah untuk menangani pengiriman data ke API"""
    while app.running or not api_queue.empty():
        try:
            # Ambil data dari queue dengan timeout
            data = api_queue.get(timeout=1)
            
            # Coba kirim ke API dengan retry mechanism
            success = send_to_api_with_retry(data, app)
            
            if success:
                app.append_log(f"✅ API: Data {data['type']} berhasil dikirim")
            else:
                app.append_log(f"❌ API: Gagal mengirim data {data['type']} setelah beberapa percobaan")
            
            api_queue.task_done()
            
        except:
            # Queue kosong atau timeout, lanjutkan
            continue

def send_to_api_with_retry(data, app):
    """Fungsi kirim ke API dengan retry mechanism"""
    for attempt in range(API_CONFIG["max_retries"]):
        try:
            payload = {
                "type": data["type"],
                "speed": round(data["speed"], 1),
                "timestamp": data["timestamp"],
                "track_id": data.get("track_id", None)
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                API_CONFIG["url"], 
                json=payload, 
                headers=headers, 
                timeout=API_CONFIG["timeout"]
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                app.append_log(f"⚠️ API Error ({response.status_code}): {response.text}")
                
        except requests.exceptions.Timeout:
            app.append_log(f"⏰ API Timeout (percobaan {attempt + 1}/{API_CONFIG['max_retries']})")
        except requests.exceptions.ConnectionError:
            app.append_log(f"🔌 API Connection Error (percobaan {attempt + 1}/{API_CONFIG['max_retries']})")
        except requests.exceptions.RequestException as e:
            app.append_log(f"❌ API Request Error: {e}")
        
        # Tunggu sebelum retry (kecuali percobaan terakhir)
        if attempt < API_CONFIG["max_retries"] - 1:
            time.sleep(API_CONFIG["retry_delay"])
    
    return False

# -----------------------------
# Fungsi untuk menambahkan data ke queue API
# -----------------------------
def queue_api_data(vehicle_type, speed, track_id=None):
    """Menambahkan data ke queue untuk dikirim ke API"""
    data = {
        "type": vehicle_type,
        "speed": speed,
        "timestamp": datetime.now().isoformat(),
        "track_id": track_id
    }
    
    try:
        api_queue.put_nowait(data)
    except:
        print("⚠️ API Queue penuh, data diabaikan")

# -----------------------------
# Frame Capturing Thread (RTSP)
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
# Detection and Display Thread
# -----------------------------
def run_detection(app):
    cap = cv2.VideoCapture("rtsp://admin:Bengkalis12@192.168.1.64:554")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        app.append_log("❌ Gagal membuka kamera RTSP.")
        return

    app.append_log("✅ Kamera berhasil dibuka.")
    
    # Start API worker thread
    api_thread = threading.Thread(target=api_worker, args=(app,), daemon=True)
    api_thread.start()
    app.append_log("🔄 API Worker thread dimulai.")
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    scale_factor = 10  # pixels per meter
    track_history = {}
    counted_ids = set()
    vehicle_counter = {v: 0 for v in vehicle_classes}
    data_records = []

    threading.Thread(target=capture_frames, args=(app, cap), daemon=True).start()

    while app.running:
        if frame_queue.empty():
            time.sleep(0.01)
            continue

        frame = frame_queue.get()
        frame = cv2.resize(frame, (640, 480))

        results = model_yolo.track(frame, persist=True)[0]
        for box in results.boxes:
            track_id = int(box.id[0]) if box.id is not None else None
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            class_name = model_yolo.names[cls_id]

            if class_name in vehicle_classes:
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                if track_id not in track_history:
                    track_history[track_id] = (cy, time.time())
                    continue

                prev_cy, prev_time = track_history[track_id]
                dt = time.time() - prev_time
                dy = abs(cy - prev_cy)
                distance = dy / scale_factor
                speed = (distance / dt) * 3.6 if dt > 0 else 0

                track_history[track_id] = (cy, time.time())

                label = f"{class_name} | {speed:.1f} km/h"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Hanya kirim data jika kendaraan belum pernah dihitung
                if track_id not in counted_ids:
                    counted_ids.add(track_id)
                    vehicle_counter[class_name] += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    data_records.append([class_name, round(speed, 1), timestamp])
                    
                    app.append_log(f"🚗 {class_name} lewat @ {speed:.1f} km/h")
                    app.update_vehicle_count(vehicle_counter)

                    # OTOMATIS KIRIM KE API - Masukkan ke queue
                    queue_api_data(class_name, speed, track_id)

        cv2.imshow("Deteksi Kendaraan", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            app.stop_detection()
            break

    # Tunggu semua API request selesai sebelum menutup
    app.append_log("⏳ Menunggu pengiriman API selesai...")
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
        self.root.title("Deteksi Kendaraan - YOLOv8 + Auto API")
        self.root.geometry("700x650")
        self.running = False
        self.vehicle_data = []

        self.vehicle_counter = {v: 0 for v in vehicle_classes}

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = ttk.Label(self.main_frame, text="🚦 Sistem Deteksi Kendaraan + Auto API",
                                     font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        # Frame untuk status API
        self.api_frame = ttk.LabelFrame(self.main_frame, text="Status API", padding="5")
        self.api_frame.pack(fill=tk.X, pady=5)

        self.api_status_label = ttk.Label(self.api_frame, text=f"🔗 API Endpoint: {API_CONFIG['url']}")
        self.api_status_label.pack()

        self.queue_status_label = ttk.Label(self.api_frame, text="📤 Queue: 0 pending")
        self.queue_status_label.pack()

        self.count_label = ttk.Label(self.main_frame, text="Jumlah Kendaraan: -",
                                     font=("Helvetica", 12))
        self.count_label.pack(pady=5)

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        self.btn_start = ttk.Button(self.button_frame, text="▶ Start", command=self.start_detection)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_stop = ttk.Button(self.button_frame, text="⏹ Stop", command=self.stop_detection, state='disabled')
        self.btn_stop.grid(row=0, column=1, padx=5)

        self.btn_save = ttk.Button(self.button_frame, text="💾 Simpan Data", command=self.save_data)
        self.btn_save.grid(row=0, column=2, padx=5)

        self.btn_test_api = ttk.Button(self.button_frame, text="🔧 Test API", command=self.test_api)
        self.btn_test_api.grid(row=0, column=3, padx=5)

        self.txt_log = scrolledtext.ScrolledText(self.main_frame, width=80, height=20,
                                                 font=("Courier", 10))
        self.txt_log.pack(pady=10)

        # Update queue status secara berkala
        self.update_queue_status()

    def update_queue_status(self):
        """Update status queue API secara berkala"""
        queue_size = api_queue.qsize()
        self.queue_status_label.config(text=f"📤 Queue: {queue_size} pending")
        self.root.after(1000, self.update_queue_status)  # Update setiap detik

    def test_api(self):
        """Test koneksi ke API"""
        self.append_log("🔧 Testing API connection...")
        test_data = {
            "type": "test",
            "speed": 0.0,
            "timestamp": datetime.now().isoformat(),
            "track_id": "test"
        }
        
        def test_thread():
            success = send_to_api_with_retry(test_data, self)
            if success:
                self.append_log("✅ API Test berhasil!")
            else:
                self.append_log("❌ API Test gagal!")
        
        threading.Thread(target=test_thread, daemon=True).start()

    def append_log(self, message):
        def update_log():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.txt_log.insert(tk.END, f"[{timestamp}] {message}\n")
            self.txt_log.see(tk.END)
        self.txt_log.after(0, update_log)

    def update_vehicle_count(self, counter):
        count_text = "Jumlah Kendaraan:\n" + "\n".join(f"{k}: {v}" for k, v in counter.items() if v > 0)
        def update_count():
            self.count_label.config(text=count_text)
        self.count_label.after(0, update_count)

    def start_detection(self):
        if self.running:
            messagebox.showinfo("Info", "Deteksi sedang berjalan.")
            return
        self.running = True
        self.btn_start.config(state='disabled')
        self.btn_stop.config(state='normal')
        self.txt_log.delete("1.0", tk.END)
        self.vehicle_counter = {v: 0 for v in vehicle_classes}
        self.update_vehicle_count(self.vehicle_counter)
        self.append_log("🚀 Memulai deteksi dengan auto API sync...")
        threading.Thread(target=run_detection, args=(self,), daemon=True).start()

    def stop_detection(self):
        self.running = False
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.append_log("🛑 Menghentikan deteksi...")

    def save_data(self):
        if not self.vehicle_data:
            messagebox.showwarning("⚠️ Tidak Ada Data", "Belum ada data kendaraan untuk disimpan.")
            return
        df = pd.DataFrame(self.vehicle_data, columns=["Jenis", "Kecepatan (km/h)", "Waktu"])
        filename = f"data_kendaraan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        messagebox.showinfo("✅ Berhasil", f"Data berhasil disimpan ke {filename}")

# -----------------------------
# Run the GUI
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDetectionApp(root)
    root.mainloop()