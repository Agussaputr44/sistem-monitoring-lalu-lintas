import cv2
import numpy as np
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime
import pandas as pd
from ultralytics import YOLO
import time
from collections import defaultdict, deque
import requests
import json

model_yolo = YOLO("yolov8n.pt")

# Definisi kelas atau label kendaraan dengan confidence atau kemungkinan yang ada (Bawaan YOLO)
vehicle_classes = {
    'bicycle': {'name': 'Sepeda', 'min_conf': 0.6},
    'car': {'name': 'Mobil', 'min_conf': 0.5}, 
    'motorcycle': {'name': 'Motor', 'min_conf': 0.5},
    'truck': {'name': 'Truk', 'min_conf': 0.5},
    'bus': {'name': 'Bus', 'min_conf': 0.5}
}

class APIManager:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def send_vehicle_data(self, vehicle_type, speed, timestamp, additional_data=None):
        """Send vehicle detection data to Laravel API"""
        try:
            data = {
                'vehicle_type': vehicle_type,
                'speed': speed,
                'detected_at': timestamp,
                'location': 'Bengkalis Traffic Cam',  # You can make this configurable
                'confidence': additional_data.get('confidence', 0) if additional_data else 0,
                'track_id': additional_data.get('track_id', 0) if additional_data else 0
            }
            
            response = requests.post(f"{self.base_url}/vehicle-detections", 
                                   json=data, 
                                   headers=self.headers,
                                   timeout=5)
            
            if response.status_code in [200, 201]:
                return True, "Data berhasil dikirim ke server"
            else:
                return False, f"Server error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def send_batch_data(self, vehicle_data_list):
        """Send multiple vehicle detections in one request"""
        try:
            batch_data = []
            for data in vehicle_data_list:
                batch_data.append({
                    'vehicle_type': data[0],
                    'speed': data[1],
                    'detected_at': data[2],
                    'location': 'Bengkalis Traffic Cam',
                    'confidence': data[3] if len(data) > 3 else 0,
                    'track_id': data[4] if len(data) > 4 else 0
                })
            
            response = requests.post(f"{self.base_url}/vehicle-detections/batch", 
                                   json={'detections': batch_data}, 
                                   headers=self.headers,
                                   timeout=10)
            
            if response.status_code in [200, 201]:
                return True, f"Batch data ({len(batch_data)} records) berhasil dikirim"
            else:
                return False, f"Server error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def get_statistics(self):
        """Get vehicle detection statistics from API"""
        try:
            response = requests.get(f"{self.base_url}/vehicle-statistics", 
                                  headers=self.headers,
                                  timeout=5)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, "Failed to get statistics"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

def calculate_speed_smoothed(positions, timestamps, scale_factor):
    """Calculate smoothed speed using multiple position points."""
    if len(positions) < 2:
        return 0
    
    speeds = []
    for i in range(1, len(positions)):
        y1, y2 = positions[i-1], positions[i]
        t1, t2 = timestamps[i-1], timestamps[i]
        
        dt = t2 - t1
        if dt > 0:
            pixel_distance = abs(y2 - y1)
            distance_meters = pixel_distance / scale_factor
            speed_ms = distance_meters / dt
            speed_kmh = speed_ms * 3.6
            speeds.append(speed_kmh)
    
    # Return average speed untuk smoothing
    return round(np.mean(speeds) if speeds else 0, 1)

def is_crossing_line(y1, y2, line_y, tolerance=10):
    """Check if vehicle crosses the counting line."""
    return (y1 <= line_y + tolerance and y2 >= line_y - tolerance) or \
           (y1 >= line_y - tolerance and y2 <= line_y + tolerance)

def run_detection(app):
    """Run vehicle detection and tracking using YOLO."""
    try:
        cap = cv2.VideoCapture("rtsp://admin:Bengkalis12@192.168.1.64:554")
        if not cap.isOpened():
            app.append_log("Gagal membuka kamera: Stream tidak tersedia.")
            return
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        
        app.append_log(f"Resolusi video: {width}x{height}, FPS: {fps}")
    except Exception as e:
        app.append_log(f"Gagal membuka video: {e}")
        return

    # Tracking variables
    track_history = defaultdict(lambda: {'positions': deque(maxlen=10), 
                                       'timestamps': deque(maxlen=10),
                                       'class_votes': defaultdict(int),
                                       'counted': False,
                                       'last_seen': 0})
    
    vehicle_counter = {v: 0 for v in vehicle_classes.keys()}
    data_records = []
    
    # Improved scale factor (adjust based on your video perspective)
    scale_factor = float(app.scale_var.get()) if app.scale_var.get().replace('.','').isdigit() else 100
    
    # Counting line (horizontal line across the frame)
    target_width, target_height = 640, 480
    counting_line_y = target_height // 2  # Middle of the frame
    
    cv2.namedWindow("Deteksi Kendaraan", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Deteksi Kendaraan", target_width, target_height)
    
    app.append_log("Mulai deteksi kendaraan...")
    app.append_log(f"Scale factor: {scale_factor} pixels/meter")
    app.append_log(f"Counting line at y={counting_line_y}")

    frame_count = 0
    while app.running:
        ret, frame = cap.read()
        if not ret:
            app.append_log("Video selesai atau gagal membaca frame.")
            break

        frame_count += 1
        current_time = time.time()
        
        # Resize frame
        frame = cv2.resize(frame, (target_width, target_height))

        # YOLO detection with tracking
        results = model_yolo.track(frame, persist=True, 
                                 conf=0.4,  # Lower initial threshold
                                 iou=0.5,
                                 tracker="bytetrack.yaml")
        
        if results[0].boxes is not None:
            for box in results[0].boxes:
                if box.id is None:
                    continue
                    
                track_id = int(box.id[0])
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model_yolo.names[cls_id]
                
                # Filter hanya kendaraan dengan confidence yang sesuai
                if class_name not in vehicle_classes:
                    continue
                    
                min_confidence = vehicle_classes[class_name]['min_conf']
                if conf < min_confidence:
                    continue

                # Get bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                # Update tracking history
                track_info = track_history[track_id]
                track_info['positions'].append(cy)
                track_info['timestamps'].append(current_time)
                track_info['class_votes'][class_name] += 1
                track_info['last_seen'] = frame_count
                
                # Determine most voted class untuk stabilitas klasifikasi
                most_voted_class = max(track_info['class_votes'], 
                                     key=track_info['class_votes'].get)
                display_name = vehicle_classes[most_voted_class]['name']
                
                # Calculate smoothed speed
                speed = 0
                if len(track_info['positions']) >= 3:
                    speed = calculate_speed_smoothed(
                        list(track_info['positions']), 
                        list(track_info['timestamps']), 
                        scale_factor
                    )
                    
                if not track_info['counted']:
                    track_info['counted'] = True
                    vehicle_counter[most_voted_class] += 1
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Store data with additional info for API
                    record = [display_name, speed, timestamp, conf, track_id]
                    data_records.append(record)
                    
                    # Send to API immediately if enabled
                    if app.api_enabled.get():
                        success, message = app.api_manager.send_vehicle_data(
                            display_name, speed, timestamp, 
                            {'confidence': conf, 'track_id': track_id}
                        )
                        if success:
                            app.append_log(f"✅ API: {message}")
                        else:
                            app.append_log(f"❌ API Error: {message}")
                    
                    app.append_log(f"{display_name} melewati garis dengan kecepatan {speed:.1f} km/h "
                                 f"(confidence: {conf:.2f}, ID: {track_id})")
                    app.update_vehicle_count(vehicle_counter)

                # Draw bounding box dan info
                color = (0, 255, 0) if track_info['counted'] else (255, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Label dengan informasi lengkap
                label = f"ID:{track_id} {display_name}"
                if speed > 0:
                    label += f" {speed:.1f}km/h"
                label += f" ({conf:.2f})"
                
                cv2.putText(frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Cleanup old tracks (hapus track yang sudah lama tidak terlihat)
        tracks_to_remove = []
        for track_id, track_info in track_history.items():
            if frame_count - track_info['last_seen'] > 30:  # 30 frames tanpa deteksi
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del track_history[track_id]

        # Draw counting line
        cv2.line(frame, (0, counting_line_y), (target_width, counting_line_y), (255, 0, 0), 2)

        # Display info
        info_text = f"Frame: {frame_count} | Tracks: {len(track_history)} | "
        info_text += f"Total: {sum(vehicle_counter.values())}"
        cv2.putText(frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Deteksi Kendaraan", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            app.stop_detection()
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    app.vehicle_data = data_records
    app.append_log(f"Deteksi selesai. Total kendaraan: {sum(vehicle_counter.values())}")

class VehicleDetectionApp:
    def __init__(self, root):
        """Initialize the Tkinter GUI application."""
        self.root = root
        self.root.title("Deteksi & Klasifikasi Kendaraan (YOLO) - API Integration")
        self.root.geometry("900x800")
        self.root.configure(bg="#f0f0f0")

        self.running = False
        self.thread = None
        self.vehicle_data = []
        self.vehicle_counter = {v: 0 for v in vehicle_classes.keys()}
        
        # Initialize API Manager
        self.api_manager = APIManager()

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        self.title_label = ttk.Label(self.main_frame, 
                                   text="Vehicle Detection System with API Integration",
                                   font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        # API Configuration Frame
        self.api_frame = ttk.LabelFrame(self.main_frame, text="Konfigurasi API", padding="10")
        self.api_frame.pack(fill=tk.X, pady=5)

        # API URL setting
        ttk.Label(self.api_frame, text="API URL:").grid(row=0, column=0, sticky=tk.W)
        self.api_url_var = tk.StringVar(value="http://localhost:8000/api")
        self.api_url_entry = ttk.Entry(self.api_frame, textvariable=self.api_url_var, width=40)
        self.api_url_entry.grid(row=0, column=1, padx=5, sticky=tk.W)

        # API Enable checkbox
        self.api_enabled = tk.BooleanVar(value=True)
        self.api_check = ttk.Checkbutton(self.api_frame, text="Kirim data ke API secara real-time", 
                                       variable=self.api_enabled)
        self.api_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        # API Test button
        self.btn_test_api = ttk.Button(self.api_frame, text="🔗 Test Koneksi API", 
                                     command=self.test_api_connection)
        self.btn_test_api.grid(row=2, column=0, pady=5, sticky=tk.W)

        # Status frame
        self.status_frame = ttk.LabelFrame(self.main_frame, text="Status Deteksi", padding="10")
        self.status_frame.pack(fill=tk.X, pady=5)

        # Vehicle count display
        self.count_label = ttk.Label(self.status_frame, text="Jumlah Kendaraan: -",
                                   font=("Helvetica", 11))
        self.count_label.pack(anchor=tk.W)

        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        # Create GUI buttons
        self.btn_start = ttk.Button(self.button_frame, text="🚀 Start Deteksi",
                                  command=self.start_detection)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_stop = ttk.Button(self.button_frame, text="⏹ Stop Deteksi",
                                 command=self.stop_detection, state='disabled')
        self.btn_stop.grid(row=0, column=1, padx=5)

        self.btn_save = ttk.Button(self.button_frame, text="💾 Simpan Data CSV",
                                 command=self.save_data)
        self.btn_save.grid(row=0, column=2, padx=5)

        self.btn_send_batch = ttk.Button(self.button_frame, text="📤 Kirim Batch ke API",
                                       command=self.send_batch_to_api)
        self.btn_send_batch.grid(row=0, column=3, padx=5)

        # Settings frame
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Pengaturan", padding="5")
        self.settings_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.settings_frame, text="Scale Factor (pixels/meter):").pack(side=tk.LEFT)
        self.scale_var = tk.StringVar(value="100")
        self.scale_entry = ttk.Entry(self.settings_frame, textvariable=self.scale_var, width=10)
        self.scale_entry.pack(side=tk.LEFT, padx=5)

        # Create log display
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Log Deteksi", padding="5")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.txt_log = scrolledtext.ScrolledText(self.log_frame, width=100, height=20,
                                               font=("Courier", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def test_api_connection(self):
        """Test API connection"""
        self.api_manager.base_url = self.api_url_var.get()
        success, result = self.api_manager.get_statistics()
        
        if success:
            self.append_log("✅ Koneksi API berhasil!")
            messagebox.showinfo("API Test", "Koneksi API berhasil!")
        else:
            self.append_log(f"❌ Koneksi API gagal: {result}")
            messagebox.showerror("API Test", f"Koneksi API gagal:\n{result}")

    def send_batch_to_api(self):
        """Send all collected data to API in batch"""
        if not self.vehicle_data:
            messagebox.showwarning("Peringatan", "Belum ada data untuk dikirim.")
            return
        
        self.api_manager.base_url = self.api_url_var.get()
        success, message = self.api_manager.send_batch_data(self.vehicle_data)
        
        if success:
            self.append_log(f"✅ Batch API: {message}")
            messagebox.showinfo("Batch Upload", message)
        else:
            self.append_log(f"❌ Batch API Error: {message}")
            messagebox.showerror("Batch Upload Error", message)

    def append_log(self, message):
        """Append message to the log display in a thread-safe way."""
        def update_log():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.txt_log.insert(tk.END, f"[{timestamp}] {message}\n")
            self.txt_log.see(tk.END)
        self.root.after(0, update_log)

    def update_vehicle_count(self, counter):
        """Update the vehicle count display in the GUI."""
        count_text = "Jumlah Kendaraan Terdeteksi:\n"
        total = 0
        for class_key, count in counter.items():
            if count > 0:
                display_name = vehicle_classes[class_key]['name']
                count_text += f"• {display_name}: {count}\n"
                total += count
        count_text += f"📊 Total: {total} kendaraan"
        
        def update_count():
            self.count_label.config(text=count_text)
        self.root.after(0, update_count)

    def start_detection(self):
        """Start the vehicle detection process in a separate thread."""
        if self.running:
            messagebox.showinfo("Info", "Deteksi sedang berjalan.")
            return
        
        # Update API manager base URL
        self.api_manager.base_url = self.api_url_var.get()
            
        self.running = True
        self.btn_start.config(state='disabled')
        self.btn_stop.config(state='normal')
        self.txt_log.delete('1.0', tk.END)
        self.vehicle_counter = {v: 0 for v in vehicle_classes.keys()}
        self.update_vehicle_count(self.vehicle_counter)
        
        self.append_log("Memulai sistem deteksi kendaraan...")
        if self.api_enabled.get():
            self.append_log(f"API Integration aktif: {self.api_url_var.get()}")
        else:
            self.append_log("API Integration nonaktif - data hanya disimpan lokal")
            
        self.thread = threading.Thread(target=run_detection, args=(self,))
        self.thread.daemon = True
        self.thread.start()

    def stop_detection(self):
        """Stop the vehicle detection process."""
        if not self.running:
            return
        self.running = False
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.append_log("Menghentikan deteksi...")

    def save_data(self):
        """Save vehicle detection data to a CSV file."""
        if not self.vehicle_data:
            messagebox.showwarning("Peringatan", "Belum ada data kendaraan untuk disimpan.")
            return
            
        try:
            df = pd.DataFrame(self.vehicle_data, 
                            columns=["Jenis Kendaraan", "Kecepatan (km/h)", "Waktu", "Confidence", "Track ID"])
            filename = f"data_kendaraan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            
            # Buat summary
            summary = df.groupby('Jenis Kendaraan').agg({
                'Kecepatan (km/h)': ['count', 'mean', 'max', 'min'],
                'Confidence': 'mean'
            }).round(2)
            
            messagebox.showinfo("Sukses", 
                              f"Data berhasil disimpan ke {filename}\n"
                              f"Total kendaraan: {len(df)} unit")
            self.append_log(f"Data disimpan ke {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDetectionApp(root)
    root.mainloop()