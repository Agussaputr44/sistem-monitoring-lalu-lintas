INSERT INTO vehicle_detections (vehicle_type, speed_kmph, confidence, track_id, location, detected_at)
SELECT
  ELT(FLOOR(RAND() * 5) + 1, 'car', 'bus', 'truck', 'motorcycle', 'bicycle') AS vehicle_type,
  ROUND(RAND() * 100 + 20, 2) AS speed_kmph,
  ROUND(RAND() * 0.3 + 0.7, 2) AS confidence,
  FLOOR(RAND() * 5000) + 1 AS track_id,
  ELT(FLOOR(RAND() * 4) + 1, 'Camera 1', 'Camera 2', 'Camera 3', 'Camera 4') AS location,
  DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 1440) MINUTE) AS detected_at
FROM information_schema.columns t1
LIMIT 10000;
