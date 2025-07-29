import cv2
import numpy as np
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime
import pandas as pd
from ultralytics import YOLO
import time
from queue import Queue

# Load YOLOv8 model
model_yolo = YOLO("yolov8n.pt")

vehicle_classes = ["car", "motorcycle", "bus", "truck", "bicycle", "person"]
frame_queue = Queue(maxsize=5)

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
        time.sleep(0.01)  # small delay to stabilize

# -----------------------------
# Detection and Display Thread
# -----------------------------
def run_detection(app):
    cap = cv2.VideoCapture("rtsp://admin:Bengkalis12@192.168.1.64:554")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Optional: flush RTSP buffer
    if not cap.isOpened():
        app.append_log("❌ Gagal membuka kamera RTSP.")
        return

    app.append_log("✅ Kamera berhasil dibuka.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    scale_factor = 10  # pixels per meter (ubah sesuai CCTV)
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

                if track_id not in counted_ids:
                    counted_ids.add(track_id)
                    vehicle_counter[class_name] += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    data_records.append([class_name, round(speed, 1), timestamp])
                    app.append_log(f"🚗 {class_name} lewat @ {speed:.1f} km/h")
                    app.update_vehicle_count(vehicle_counter)

        cv2.imshow("Deteksi Kendaraan", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            app.stop_detection()
            break

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
        self.root.title("Deteksi Kendaraan - YOLOv8")
        self.root.geometry("700x600")
        self.running = False
        self.vehicle_data = []

        self.vehicle_counter = {v: 0 for v in vehicle_classes}

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = ttk.Label(self.main_frame, text="🚦 Sistem Deteksi Kendaraan",
                                     font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

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

        self.txt_log = scrolledtext.ScrolledText(self.main_frame, width=80, height=20,
                                                 font=("Courier", 10))
        self.txt_log.pack(pady=10)

    def append_log(self, message):
        def update_log():
            self.txt_log.insert(tk.END, message + "\n")
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
        threading.Thread(target=run_detection, args=(self,), daemon=True).start()

    def stop_detection(self):
        self.running = False
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')

    def save_data(self):
        if not self.vehicle_data:
            messagebox.showwarning("⚠️ Tidak Ada Data", "Belum ada data kendaraan untuk disimpan.")
            return
        df = pd.DataFrame(self.vehicle_data, columns=["Jenis", "Kecepatan (km/h)", "Waktu"])
        df.to_csv("data_kendaraan.csv", index=False)
        messagebox.showinfo("✅ Berhasil", "Data berhasil disimpan ke data_kendaraan.csv")

# -----------------------------
# Run the GUI
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDetectionApp(root)
    root.mainloop()
