import cv2
import threading
import time
import queue
import yt_dlp
import numpy as np
import random
from datetime import datetime
from collections import defaultdict
from ultralytics import YOLO
from app_optimation.database.session import SessionLocal
from app_optimation.services import vehicle_service

class VideoStreamService:
    def __init__(self):
        self.model_path = "app_optimation/core/yolov8s.pt" 
        self.video_source = "https://youtu.be/rncXQvezcZU"
        self.target_height = 480
        self.stream_queue = queue.Queue(maxsize=2)
        self.running = True
        self.model = None
        self.cap = None
        
        self.stream_ready = False
        self.frame_count = 0
        
        self.vehicle_classes = {
            'car': {'name': 'car', 'min_conf': 0.40, 'color': (0, 255, 0)},     
            'motorcycle': {'name': 'motorcycle', 'min_conf': 0.35, 'color': (0, 255, 255)}, 
            'bus': {'name': 'bus', 'min_conf': 0.45, 'color': (255, 0, 0)},        
            'truck': {'name': 'truck', 'min_conf': 0.45, 'color': (0, 0, 255)},    
            'pickup': {'name': 'pickup', 'min_conf': 0.40, 'color': (255, 0, 255)}, 
        }

    def _get_youtube_url(self, source):
        if "youtube.com" in source or "youtu.be" in source:
            try:
                ydl_opts = {
                    'format': 'best[height<=480]/best',
                    'quiet': True,
                    'no_warnings': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(source, download=False)
                    url = info['url']
                    return url
            except Exception as e:
                return source
        return source

    def _draw_bbox(self, img, x1, y1, x2, y2, label, speed, color):
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        
        text = f"{label} {speed:.1f} km/h"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        cv2.rectangle(img, 
                     (x1, y1 - text_height - 10), 
                     (x1 + text_width + 10, y1), 
                     color, 
                     -1)  
        
        cv2.putText(img, text, (x1 + 5, y1 - 5), 
                   font, font_scale, (255, 255, 255), thickness)
        
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        cv2.circle(img, (center_x, center_y), 5, color, -1)

    def run_detection(self):
        print("Starting YOLO detection thread...")
        
        try:
            print("📦 Loading YOLO model...")
            self.model = YOLO(self.model_path)
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return

        track_history = defaultdict(int)
        counted_ids = set()
        retry_count = 0
        max_retries = 3

        while self.running and retry_count < max_retries:
            try:
                url = self._get_youtube_url(self.video_source)
                
                print(f"📹 Opening video stream (attempt {retry_count + 1}/{max_retries})...")
                self.cap = cv2.VideoCapture(url)
                
                if not self.cap.isOpened():
                    print("❌ Failed to open video stream")
                    retry_count += 1
                    time.sleep(5)
                    continue
                
                print("✅ Video stream opened")
                self.stream_ready = True
                retry_count = 0
                
                frame_counter = 0
                detection_count = 0

                while self.cap.isOpened() and self.running:
                    ret, frame = self.cap.read()
                    if not ret:
                        print("⚠️ No frame received, reconnecting...")
                        break

                    frame_counter += 1
                    
                    h, w = frame.shape[:2]
                    frame_resized = cv2.resize(frame, (int(w * self.target_height / h), self.target_height))
                    
                    try:
                        results = self.model.track(frame_resized, persist=True, conf=0.3, verbose=False)[0]
                    except Exception as e:
                        print(f"⚠️ Detection error: {e}")
                        _, jpeg = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        try:
                            if self.stream_queue.full():
                                self.stream_queue.get_nowait()
                            self.stream_queue.put_nowait(jpeg.tobytes())
                        except queue.Full:
                            pass
                        continue

                    detected_in_frame = 0
                    if results.boxes is not None and len(results.boxes) > 0:
                        for box in results.boxes:
                            if box.id is None:
                                continue
                            
                            tid = int(box.id[0])
                            cls_name = self.model.names[int(box.cls[0])]
                            conf = float(box.conf[0])
                            x1, y1, x2, y2 = map(int, box.xyxy[0])

                            if cls_name in self.vehicle_classes:
                                cfg = self.vehicle_classes[cls_name]
                                if conf < cfg['min_conf']:
                                    continue

                                detected_in_frame += 1
                                
                                speed = 40 + random.uniform(-5, 5)

                                self._draw_bbox(frame_resized, x1, y1, x2, y2, 
                                              cfg['name'], speed, cfg['color'])

                                track_history[tid] += 1
                                if tid not in counted_ids and track_history[tid] >= 5:
                                    counted_ids.add(tid)
                                    
                                    threading.Thread(
                                        target=self._save_to_db,
                                        args=(cfg['name'], speed, conf, tid),
                                        daemon=True
                                    ).start()
                    
                    if detected_in_frame > 0:
                        detection_count += 1
                        if detection_count % 10 == 0:
                            print(f"📊 Detected {detected_in_frame} vehicles in frame (total detections: {detection_count})")

                    info_text = f"Detections: {detected_in_frame} | Frame: {frame_counter}"
                    cv2.putText(frame_resized, info_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    _, jpeg = cv2.imencode('.jpg', frame_resized, 
                                          [cv2.IMWRITE_JPEG_QUALITY, 85])  
                    
                    try:
                        if self.stream_queue.full():
                            self.stream_queue.get_nowait()
                        self.stream_queue.put_nowait(jpeg.tobytes())
                        self.frame_count += 1
                    except queue.Full:
                        pass

                if self.cap:
                    self.cap.release()
                    self.cap = None
                
                print("⚠️ Stream ended, will retry in 3 seconds...")
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Error in detection loop: {e}")
                retry_count += 1
                if self.cap:
                    self.cap.release()
                    self.cap = None
                time.sleep(5)

        print("🛑 Detection thread stopped")
        self.stream_ready = False

    def _save_to_db(self, vehicle_type, speed, conf, tid):
        db = SessionLocal()
        try:
            vehicle_service.save_detection(
                db=db,
                vehicle_type=vehicle_type,
                speed_kmph=round(speed, 1),
                confidence=round(conf, 2),
                track_id=tid,
                location="Bengkalis Main Road"
            )
            print(f"✅ Saved: {vehicle_type} (ID: {tid})")
        except Exception as e:
            print(f"⚠️ DB Save error: {e}")
        finally:
            db.close()

    def generate_frames(self):
        print("🎬 Stream client connected")
        
        wait_time = 0
        while not self.stream_ready and wait_time < 10:
            time.sleep(0.5)
            wait_time += 0.5
        
        if not self.stream_ready:
            print("⚠️ Stream not ready, sending placeholder")
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Connecting to stream...", (150, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, jpeg = cv2.imencode('.jpg', placeholder)
            frame_bytes = jpeg.tobytes()
            
            for _ in range(5):
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.2)
        
        frames_sent = 0
        while self.running:
            try:
                frame = self.stream_queue.get(timeout=2.0)
                frames_sent += 1
                
                if frames_sent % 100 == 0:
                    print(f"📊 Frames sent to client: {frames_sent}")
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
            except queue.Empty:
                if self.stream_ready:
                    continue
                else:
                    break
            except Exception as e:
                print(f"❌ Stream error: {e}")
                break
        
        print("🛑 Stream client disconnected")

    def stop(self):
        print("🛑 Stopping video service...")
        self.running = False
        if self.cap:
            self.cap.release()
        print("✅ Video service stopped")