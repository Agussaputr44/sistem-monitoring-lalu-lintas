CREATE DATABASE traffic_monitoring;
USE traffic_monitoring;

CREATE TABLE vehicle_detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_type VARCHAR(50),
    speed_kmph FLOAT,
    confidence FLOAT,
    track_id INT,
    location VARCHAR(100),
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
