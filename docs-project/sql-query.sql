create database monitoring_kendaraan;
use monitoring_kendaraan;
CREATE TABLE vehicle_detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_type VARCHAR(20) NOT NULL,
    speed_kmph FLOAT,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

select * from vehicle_detections;