from fastapi.encoders import jsonable_encoder
from fastapi_cache.decorator import cache
from app_optimation.models.vehicle_model import VehicleDetection
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
import pytz

# Setup Timezone
wib = pytz.timezone("Asia/Jakarta")

def save_detection(db: Session, vehicle_type, speed_kmph, confidence=0.0, track_id=0, location="Camera Bengkalis"):
    """
    Menyimpan data deteksi baru.
    """
    detection = VehicleDetection(
        vehicle_type=vehicle_type,
        speed_kmph=speed_kmph,
        confidence=confidence,
        track_id=track_id,
        location=location,
        detected_at=datetime.now(wib)
    )
    db.add(detection)
    db.commit()
    db.refresh(detection)
    
    return {
        "status": "success",
        "data": {
            "id": detection.id,
            "vehicle_type": detection.vehicle_type,
            "detected_at": detection.detected_at
        }
    }

@cache(expire=60)  
def get_all_classification(db: Session):
    """
    Menghitung total kendaraan per jenis.
    OPTIMASI: Pastikan kolom 'vehicle_type' di-index di database.
    Cache dinaikkan ke 60s karena data agregat tidak berubah drastis tiap detik.
    """
    result = (
        db.query(
            VehicleDetection.vehicle_type,
            func.count(VehicleDetection.id).label("count")
        )
        .group_by(VehicleDetection.vehicle_type)
        .all()
    )
    return [{"vehicle_type": r.vehicle_type, "count": r.count} for r in result]

@cache(expire=10) 
def get_history(db: Session, limit: int = 100):
    """
    Mengambil 100 data terakhir.
    OPTIMASI: Menggunakan .desc() eksplisit.
    WAJIB: Index kolom 'detected_at' di database agar sorting instan.
    """
    results = (
        db.query(
            VehicleDetection.id,
            VehicleDetection.vehicle_type,
            VehicleDetection.speed_kmph,
            VehicleDetection.confidence,
            VehicleDetection.location,
            VehicleDetection.detected_at
        )
        .order_by(desc(VehicleDetection.detected_at)) # Menggunakan desc() dari sqlalchemy
        .limit(limit) 
        .all()
    )
    
    return [
        {
            "id": r.id,
            "vehicle_type": r.vehicle_type,
            "speed_kmph": r.speed_kmph,
            "confidence": r.confidence,
            "location": r.location,
            "detected_at": r.detected_at.isoformat() if r.detected_at else None
        }
        for r in results
    ]

@cache(expire=60)
def get_history_by_id(db: Session, history_id: int):
    """
    Mengambil detail satu data. Cepat karena pakai ID (Primary Key).
    """
    record = db.query(VehicleDetection).filter(VehicleDetection.id == history_id).first()
    
    if not record:
        return None 
    
    return {
        "id": record.id,
        "vehicle_type": record.vehicle_type,
        "speed_kmph": record.speed_kmph,
        "confidence": record.confidence,
        "location": record.location,
        "detected_at": record.detected_at
    }

@cache(expire=60)
def get_average_speed(db: Session):
    """
    Menghitung rata-rata kecepatan.
    OPTIMASI BESAR: Hanya menghitung data 24 jam terakhir.
    Alasan: Menghitung rata-rata 2 juta baris (semua data) bikin server timeout.
    """
    # Ambil waktu 24 jam yang lalu dari sekarang
    last_24h = datetime.now(wib) - timedelta(hours=24)
    
    # Query rata-rata hanya untuk data >= last_24h
    result = db.query(func.avg(VehicleDetection.speed_kmph))\
        .filter(VehicleDetection.detected_at >= last_24h)\
        .scalar()
        
    return {
        "average_speed": round(result, 2) if result else 0.0,
        "unit": "km/h",
        "period": "Last 24 Hours" 
    }