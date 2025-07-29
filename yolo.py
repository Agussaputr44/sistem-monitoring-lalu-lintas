import cv2
import numpy as np
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime
import pandas as pd
from ultralytics import YOLO
import time

# Load the YOLOv8 model
model_yolo = YOLO("yolov8n.pt")

# Define vehicle classes to detect
vehicle_classes = ["car", "motorcycle", "bus", "truck", "bicycle", "person"]

def estimate_speed(y1, y2, fps, scale_factor):
    """Estimate vehicle speed based on pixel distance and frame rate."""
    pixel_distance = abs(y2 - y1)
    speed = (pixel_distance / scale_factor) * fps * 0.06  # Convert to km/h
    return round(speed, 2)

def run_detection(app):
    """Run vehicle detection and tracking using YOLO with improved display."""
    try:
        cap = cv2.VideoCapture("rtsp://admin:Bengkalis12@192.168.1.64:554")
        if not cap.isOpened():
            app.append_log("Gagal membuka kamera: Stream tidak tersedia.")
            return
        # Get original resolution
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        app.append_log(f"Resolusi kamera asli: {width}x{height}")
    except Exception as e:
        app.append_log(f"Gagal membuka kamera: {e}")
        return

    track_history = {}  # track_id: (cy, time.time())
    vehicle_counter = {v: 0 for v in vehicle_classes}  # Initialize vehicle counter
    data_records = []

    app.append_log("Mulai deteksi kendaraan...")

    # Get FPS from video capture or default to 30
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    scale_factor = 10  # Assumption: 10 pixels = 1 meter (adjust based on CCTV)

    counted_ids = set()  # Track IDs of counted vehicles

    # Set OpenCV window properties with aspect ratio preservation
    target_width, target_height = 640, 480  # Target resolution
    cv2.namedWindow("Deteksi Kendaraan", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Deteksi Kendaraan", target_width, target_height)

    while app.running:
        ret, frame = cap.read()
        if not ret:
            app.append_log("Gagal membaca frame dari kamera.")
            break

        # Preserve aspect ratio and resize
        frame = cv2.resize(frame, (target_width, target_height),
                          interpolation=cv2.INTER_LINEAR)  # Use INTER_LINEAR for better quality

        # Perform YOLO tracking
        results = model_yolo.track(frame, persist=True)[0]
        for box in results.boxes:
            track_id = int(box.id[0]) if box.id is not None else None

            # Get bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = model_yolo.names[cls_id]

            if class_name in vehicle_classes:
                # Calculate center of bounding box
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                # Initialize tracking for new track_id
                if track_id not in track_history:
                    track_history[track_id] = (cy, time.time())
                    continue

                # Calculate speed
                prev_cy, prev_time = track_history[track_id]
                curr_time = time.time()
                dt = curr_time - prev_time  # Time difference in seconds

                if dt == 0:
                    speed = 0
                else:
                    dy = abs(cy - prev_cy)
                    distance_meters = dy / scale_factor  # Pixels to meters
                    speed = (distance_meters / dt) * 3.6  # Convert m/s to km/h

                # Update tracking history
                track_history[track_id] = (cy, curr_time)

                # Draw bounding box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{class_name} | {speed:.2f} km/h"
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Count vehicle if not already counted
                if track_id and track_id not in counted_ids:
                    vehicle_counter[class_name] += 1
                    counted_ids.add(track_id)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    data_records.append([class_name, speed, timestamp])
                    app.append_log(f"{class_name} lewat dengan kecepatan {speed:.2f} km/h")
                    app.update_vehicle_count(vehicle_counter)

        # Display the frame
        cv2.imshow("Deteksi Kendaraan", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # Exit on ESC key
            app.stop_detection()
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

    app.vehicle_data = data_records
    app.append_log("Deteksi kendaraan selesai.")

class VehicleDetectionApp:
    def __init__(self, root):
        """Initialize the Tkinter GUI application."""
        self.root = root
        self.root.title("Deteksi & Klasifikasi Kendaraan (YOLO)")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f0f0")

        self.running = False
        self.thread = None
        self.vehicle_data = []
        self.vehicle_counter = {v: 0 for v in vehicle_classes}

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        self.title_label = ttk.Label(self.main_frame, text="Vehicle Detection System",
                                     font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        # Vehicle count display
        self.count_label = ttk.Label(self.main_frame, text="Jumlah Kendaraan: -",
                                     font=("Helvetica", 12))
        self.count_label.pack(pady=5)

        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        # Create GUI buttons
        self.btn_start = ttk.Button(self.button_frame, text="Start Deteksi",
                                    command=self.start_detection)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_stop = ttk.Button(self.button_frame, text="Stop Deteksi",
                                   command=self.stop_detection, state='disabled')
        self.btn_stop.grid(row=0, column=1, padx=5)

        self.btn_save = ttk.Button(self.button_frame, text="Simpan Data",
                                   command=self.save_data)
        self.btn_save.grid(row=0, column=2, padx=5)

        # Create log display
        self.txt_log = scrolledtext.ScrolledText(self.main_frame, width=80, height=20,
                                                 font=("Courier", 10))
        self.txt_log.pack(pady=10)

    def append_log(self, message):
        """Append message to the log display in a thread-safe way."""
        def update_log():
            self.txt_log.insert(tk.END, message + '\n')
            self.txt_log.see(tk.END)
        self.txt_log.after(0, update_log)

    def update_vehicle_count(self, counter):
        """Update the vehicle count display in the GUI."""
        count_text = "Jumlah Kendaraan:\n" + "\n".join(
            f"{k}: {v}" for k, v in counter.items() if v > 0)
        def update_count():
            self.count_label.config(text=count_text)
        self.count_label.after(0, update_count)

    def start_detection(self):
        """Start the vehicle detection process in a separate thread."""
        if self.running:
            messagebox.showinfo("Info", "Deteksi sedang berjalan.")
            return
        self.running = True
        self.btn_start.config(state='disabled')
        self.btn_stop.config(state='normal')
        self.txt_log.delete('1.0', tk.END)
        self.vehicle_counter = {v: 0 for v in vehicle_classes}
        self.update_vehicle_count(self.vehicle_counter)
        self.thread = threading.Thread(target=run_detection, args=(self,))
        self.thread.start()

    def stop_detection(self):
        """Stop the vehicle detection process."""
        if not self.running:
            return
        self.running = False
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')

    def save_data(self):
        """Save vehicle detection data to a CSV file."""
        if not self.vehicle_data:
            messagebox.showwarning("Peringatan", "Belum ada data kendaraan.")
            return
        df = pd.DataFrame(self.vehicle_data, columns=["Jenis Kendaraan", "Kecepatan (km/h)", "Waktu"])
        df.to_csv("data_kendaraan.csv", index=False)
        messagebox.showinfo("Sukses", "Data kendaraan berhasil disimpan.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDetectionApp(root)
    root.mainloop()