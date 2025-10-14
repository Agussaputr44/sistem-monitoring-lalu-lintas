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

# Model YOLO
model_yolo = YOLO("yolov8s.pt")

# Konfigurasi kendaraan - TAMBAH PICKUP
vehicle_classes = {
    'car': {'name': 'Mobil', 'min_conf': 0.25, 'min_area': 600}, 
    'motorcycle': {'name': 'Motor', 'min_conf': 0.25, 'min_area': 250},
    'bicycle': {'name': 'Sepeda', 'min_conf': 0.30, 'min_area': 150},
    'bus': {'name': 'Bus', 'min_conf': 0.25, 'min_area': 1500},
    'truck': {'name': 'Truk', 'min_conf': 0.25, 'min_area': 1000},
    'pickup': {'name': 'Pickup', 'min_conf': 0.25, 'min_area': 700}, 
}

api_queue = Queue()

# API Manager
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

def api_worker(app):
    """Worker thread untuk kirim data ke API - batch processing"""
    batch = []
    batch_size = 10
    last_send_time = time.time()
    
    while app.running or not api_queue.empty():
        try:
            try:
                data = api_queue.get(timeout=0.5)
                batch.append(data)
                api_queue.task_done()
            except:
                pass
            
            current_time = time.time()
            should_send = (len(batch) >= batch_size or 
                          (len(batch) > 0 and current_time - last_send_time > 2))
            
            if should_send and batch:
                success_count = 0
                for data in batch:
                    try:
                        success, _ = app.api_manager.send_vehicle_data(
                            data["vehicle_type"], data["speed"], data["timestamp"],
                            data["track_id"], data["confidence"]
                        )
                        if success:
                            success_count += 1
                    except:
                        pass
                
                if success_count > 0:
                    app.append_log(f"API: {success_count}/{len(batch)} data terkirim")
                
                batch = []
                last_send_time = current_time
                time.sleep(0.1)
                
        except Exception as e:
            app.append_log(f"API Worker Error: {str(e)}")
            continue
    
    if batch:
        for data in batch:
            try:
                app.api_manager.send_vehicle_data(
                    data["vehicle_type"], data["speed"], data["timestamp"],
                    data["track_id"], data["confidence"]
                )
            except:
                pass

def classify_truck_or_pickup(bbox_width, bbox_height, bbox_area):
    """
    Bedain Pickup vs Truck berdasarkan UKURAN
    Logic: Truck kecil-menengah = PICKUP (L300, Carry, dll)
           Truck besar = TRUCK (Container, Box Truck)
    """
    aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0
    
    # MAIN RULE: Ukuran menentukan!
    # Pickup (L300, Carry, dll): Area kecil-menengah
    # Truck besar (Container): Area sangat besar
    
    # Rule 1: Area kecil-menengah = PICKUP
    if bbox_area < 15000:
        return 'pickup'  # L300, Carry, pickup kecil
    
    # Rule 2: Area menengah + tidak terlalu tinggi = PICKUP
    if bbox_area < 20000 and aspect_ratio > 1.2:
        return 'pickup'  # Pickup sedang
    
    # Rule 3: Sangat besar = TRUCK beneran
    if bbox_area >= 20000:
        return 'truck'  # Container truck, box truck besar
    
    # Default: Cenderung pickup (karena di Indonesia banyak L300/Carry)
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

# SIMPLE TRACKING - Permanent Counting
def run_instant_detection(app):
    cap = cv2.VideoCapture("lalulintaskota.mp4")
    
    if not cap.isOpened():
        app.append_log("Gagal membuka video")
        return

    app.append_log("Video dibuka - PERMANENT COUNT MODE")
    
    num_api_workers = 3
    for i in range(num_api_workers):
        threading.Thread(target=api_worker, args=(app,), daemon=True, name=f"API-Worker-{i+1}").start()
    app.append_log(f"Started {num_api_workers} API worker threads")
    
    track_frame_count = defaultdict(int)
    counted_ids = set()
    
    vehicle_counter = {v: 0 for v in vehicle_classes}
    data_records = []
    frame_count = 0

    while app.running:
        ret, frame = cap.read()
        if not ret:
            app.append_log("Video selesai")
            break
            
        frame_count += 1
        
        frame_height, frame_width = frame.shape[:2]
        target_height = 720
        target_width = int(frame_width * target_height / frame_height)
        frame = cv2.resize(frame, (target_width, target_height))
        
        results = model_yolo.track(
            frame, 
            persist=True,
            conf=0.20,
            iou=0.4,
            tracker="bytetrack.yaml",
            verbose=False
        )[0]
        
        if results.boxes is None:
            cv2.imshow("Vehicle Detection", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            continue
        
        detected_count = 0
        current_frame_ids = set()
        
        for box in results.boxes:
            track_id = int(box.id[0]) if box.id is not None else None
            if track_id is None:
                continue
                
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = model_yolo.names[cls_id]
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            bbox_width = x2 - x1
            bbox_height = y2 - y1
            bbox_area = bbox_width * bbox_height
            
            # LOGIC PICKUP: Jika detect truck, cek apakah itu pickup atau truck beneran
            if class_name == 'truck':
                class_name = classify_truck_or_pickup(bbox_width, bbox_height, bbox_area)
            
            if class_name not in vehicle_classes:
                continue
            
            min_area = vehicle_classes[class_name]['min_area']
            min_conf = vehicle_classes[class_name]['min_conf']
            
            if bbox_area < min_area or conf < min_conf:
                continue
            
            detected_count += 1
            current_frame_ids.add(track_id)
            
            track_frame_count[track_id] += 1
            
            if track_id not in counted_ids and track_frame_count[track_id] >= 3:
                counted_ids.add(track_id)
                vehicle_counter[class_name] += 1
                
                y_center = (y1 + y2) // 2
                speed = estimate_speed_simple(bbox_area, y_center, target_height)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                data_records.append([
                    vehicle_classes[class_name]['name'],
                    round(speed, 1),
                    timestamp,
                    round(conf, 2),
                    track_id
                ])
                
                app.append_log(
                    f"COUNTED #{len(data_records)}: {vehicle_classes[class_name]['name']} "
                    f"@ {speed:.1f} km/h (ID:{track_id}, Conf:{conf:.2f}, Frames:{track_frame_count[track_id]})"
                )
                
                app.update_vehicle_count(vehicle_counter)
                
                if api_queue.qsize() < 100:
                    try:
                        api_queue.put_nowait({
                            "vehicle_type": vehicle_classes[class_name]['name'],
                            "speed": speed,
                            "timestamp": timestamp,
                            "track_id": track_id,
                            "confidence": conf
                        })
                    except:
                        pass
                else:
                    app.append_log("⚠ API Queue penuh, skip data")
            
            if track_id in counted_ids:
                color = (0, 255, 0)
                status = f"COUNTED #{list(counted_ids).index(track_id) + 1}"
            elif track_frame_count[track_id] >= 2:
                color = (0, 165, 255)
                status = f"READY ({track_frame_count[track_id]}/3)"
            else:
                color = (255, 255, 0)
                status = f"NEW ({track_frame_count[track_id]}/3)"
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label1 = f"ID:{track_id} {vehicle_classes[class_name]['name']} - {status}"
            label2 = f"Conf:{conf:.2f}"
            
            cv2.putText(frame, label1, (x1, y1-25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(frame, label2, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        all_track_ids = list(track_frame_count.keys())
        for tid in all_track_ids:
            if tid not in current_frame_ids and tid not in counted_ids:
                if track_frame_count[tid] < 3:
                    del track_frame_count[tid]
        
        info_text = f"Frame: {frame_count} | Active: {detected_count} | COUNTED: {len(counted_ids)}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # UPDATE: Tampilkan counter semua kendaraan termasuk Pickup
        counter_text = f"Mobil:{vehicle_counter.get('car',0)} Motor:{vehicle_counter.get('motorcycle',0)} Pickup:{vehicle_counter.get('pickup',0)} Bus:{vehicle_counter.get('bus',0)}"
        cv2.putText(frame, counter_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Vehicle Detection", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            app.stop_detection()
            break

    api_queue.join()
    cap.release()
    cv2.destroyAllWindows()
    app.vehicle_data = data_records
    app.append_log(f"Detection selesai! Total: {len(counted_ids)} kendaraan")

# GUI
class VehicleDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Detection - with Pickup")
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
                         text="Vehicle Detection System", 
                         font=("Helvetica", 18, "bold"))
        title.pack(pady=10)
        
        subtitle = ttk.Label(main_frame,
                            text="Deteksi: Mobil, Motor, Sepeda, Bus, Truk, Pickup", 
                            font=("Helvetica", 11))
        subtitle.pack()
        
        self.count_label = ttk.Label(main_frame, 
                                    text="Belum ada kendaraan terdeteksi", 
                                    font=("Helvetica", 12, "bold"))
        self.count_label.pack(pady=15)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Start", 
                  command=self.start_detection, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Stop", 
                  command=self.stop_detection, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save", 
                  command=self.save_data, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Log", 
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
        self.append_log("Sistem: Permanent counting - hitung sekali per ID")
        self.append_log("Kendaraan: Mobil, Motor, Sepeda, Bus, Truk, Pickup")
        self.append_log("Syarat: Track harus muncul minimal 3 frame")

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
            self.append_log(f"Data saved: {filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDetectionApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.running = False
        print("App terminated")
