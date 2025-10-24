import asyncio
from fastapi.encoders import jsonable_encoder
from fastapi_cache import FastAPICache
from app_optimation.models.vehicle_model import VehicleDetection
from datetime import datetime, date
from sqlalchemy import func
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session
import pytz

# ============================================================
# === SIMPAN DATA HASIL DETEKSI YOLO KE DATABASE ============
# ============================================================

def save_detection(db: Session, vehicle_type, speed_kmph, confidence=0.0, track_id=0, location="Camera Bengkalis"):
    wib = pytz.timezone("Asia/Jakarta")
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

    # Bersihkan cache async-safe
    async def clear_cache_safe():
        try:
            await FastAPICache.clear()
            print("🧹 Cache dihapus: data terbaru akan dimuat ulang dari DB.")
        except Exception as e:
            print(f"⚠️ Gagal membersihkan cache: {e}")

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(clear_cache_safe())
    except RuntimeError:
        asyncio.run(clear_cache_safe())

    return {
        "status": "success",
        "message": f"Data {vehicle_type} disimpan dan cache diperbarui",
        "data": {
            "id": detection.id,
            "vehicle_type": detection.vehicle_type,
            "speed_kmph": detection.speed_kmph,
            "confidence": detection.confidence,
            "track_id": detection.track_id,
            "location": detection.location,
            "detected_at": detection.detected_at
        }
    }

# ============================================================
# === AMBIL SEMUA DATA KLASIFIKASI ==========================
# ============================================================
@cache(expire=120) 
async def get_all_classification(db: Session):
    result = (
        db.query(
            VehicleDetection.vehicle_type,
            func.count(VehicleDetection.id).label("count")
        )
        .group_by(VehicleDetection.vehicle_type)
        .all()
    )
    return [{"vehicle_type": r.vehicle_type, "count": r.count} for r in result]

# ============================================================
# === AMBIL HISTORY DETEKSI =================================
# ============================================================
@cache(expire=60)
async def get_history(db: Session):
    result = db.query(VehicleDetection).order_by(VehicleDetection.detected_at.desc()).all()
    return [
        {
            "id": r.id,
            "vehicle_type": r.vehicle_type,
            "speed_kmph": r.speed_kmph,
            "confidence": r.confidence,
            "track_id": r.track_id,
            "location": r.location,
            "detected_at": r.detected_at
        }
        for r in result
    ]
@cache(expire=60)
async def get_history_by_id(db: Session, history_id: int):
    record = db.query(VehicleDetection).filter(VehicleDetection.id == history_id).first()
    if not record:
        return {"status": "error", "message": "Data tidak ditemukan"}

    # Pastikan bisa di-cache dan di-decode JSON
    data = {
        "id": record.id,
        "vehicle_type": record.vehicle_type,
        "speed_kmph": record.speed_kmph,
        "confidence": record.confidence,
        "track_id": record.track_id,
        "location": record.location,
        "detected_at": record.detected_at,
    }

    return jsonable_encoder(data)
# ============================================================
# === RATA-RATA KECEPATAN ===================================
# ============================================================
@cache(expire=30)
async def get_average_speed(db: Session):
    result = db.query(func.avg(VehicleDetection.speed_kmph).label("average_speed")).scalar()
    return {
        "average_speed": round(result, 2) if result else 0.0,
        "unit": "km/h"
    }
