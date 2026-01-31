DELIMITER $$

CREATE PROCEDURE GenerateTrafficData()
BEGIN
    DECLARE i INT DEFAULT 0;
    
    -- Matikan autocommit biar proses INSERT ngebut (tidak commit per baris)
    SET autocommit = 0;

    WHILE i < 1000000 DO
        INSERT INTO vehicle_detections (vehicle_type, speed_kmph, confidence, track_id, location, detected_at)
        VALUES (
            -- Random Vehicle Type (Car, Bus, Truck, Motorcycle)
            ELT(FLOOR(1 + RAND() * 4), 'Car', 'Truck', 'Bus', 'Motorcycle'),
            
            -- Random Speed (Antara 20.00 sampai 120.00 kmph)
            ROUND(20 + (RAND() * 100), 2),
            
            -- Random Confidence (Antara 0.70 sampai 0.99)
            ROUND(0.70 + (RAND() * 0.29), 2),
            
            -- Random Track ID (1 - 5000)
            FLOOR(1 + RAND() * 5000),
            
            -- Random Location (Camera_1 sampai Camera_5)
            CONCAT('Camera_', FLOOR(1 + RAND() * 5)),
            
            -- Random Time (Dalam 30 hari terakhir)
            NOW() - INTERVAL FLOOR(RAND() * 30) DAY - INTERVAL FLOOR(RAND() * 86400) SECOND
        );

        SET i = i + 1;

        -- Commit setiap 10.000 data agar RAM tidak jebol
        IF i % 10000 = 0 THEN
            COMMIT;
        END IF;
    END WHILE;

    COMMIT;
    SET autocommit = 1;
END$$

DELIMITER ;

-- Panggil prosedur untuk generate data
CALL GenerateTrafficData();

-- Hapus prosedur setelah selesai
DROP PROCEDURE GenerateTrafficData;

-- hitung
SELECT COUNT(*) FROM vehicle_detections;

