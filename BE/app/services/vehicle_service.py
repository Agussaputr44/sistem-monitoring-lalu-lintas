from app.models.vehicle_model import VehicleDetection
from datetime import datetime, date
from sqlalchemy import func

# ============================================================
# === SIMPAN DATA HASIL DETEKSI YOLO KE DATABASE ============
# ============================================================

def save_detection(db, vehicle_type, speed_kmph, confidence=0.0, track_id=0, location="Camera Bengkalis"):
    """
    Simpan hasil deteksi kendaraan dari YOLO ke tabel vehicle_detections
    """
    detection = VehicleDetection(
        vehicle_type=vehicle_type,
        speed_kmph=speed_kmph,
        confidence=confidence,
        track_id=track_id,
        location=location,
        detected_at=datetime.utcnow()
    )
    db.add(detection)
    db.commit()
    db.refresh(detection)
    return {
        "status": "success",
        "message": f"Data {vehicle_type} disimpan",
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
# === AMBIL SEMUA DATA KLASIFIKASI (setara statistic) ========
# ============================================================

def get_all_classification(db):
    """
    Ambil jumlah kendaraan berdasarkan jenis
    """
    result = db.query(
        VehicleDetection.vehicle_type,
        func.count(VehicleDetection.id).label("count")
    ).group_by(VehicleDetection.vehicle_type).all()

    return [{"vehicle_type": r.vehicle_type, "count": r.count} for r in result]


# ============================================================
# === AMBIL HISTORY DETEKSI ==================================
# ============================================================

def get_history(db):
    """
    Ambil semua riwayat deteksi kendaraan
    """
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


def get_history_by_id(db, history_id: int):
    """
    Ambil data history berdasarkan ID
    """
    record = db.query(VehicleDetection).filter(VehicleDetection.id == history_id).first()
    if not record:
        return {"status": "error", "message": "Data tidak ditemukan"}
    
    return {
        "id": record.id,
        "vehicle_type": record.vehicle_type,
        "speed_kmph": record.speed_kmph,
        "confidence": record.confidence,
        "track_id": record.track_id,
        "location": record.location,
        "detected_at": record.detected_at
    }


# ============================================================
# === AMBIL HISTORY BERDASARKAN TANGGAL ======================
# ============================================================

# def get_history_by_date(db, selected_date: str):
#     """
#     Ambil semua data berdasarkan tanggal (YYYY-MM-DD)
#     """
#     try:
#         parsed_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
#     except ValueError:
#         return {"status": "error", "message": "Format tanggal salah, gunakan YYYY-MM-DD"}

#     result = db.query(VehicleDetection).filter(
#         func.date(VehicleDetection.detected_at) == parsed_date
#     ).order_by(VehicleDetection.detected_at.desc()).all()

#     return [
#         {
#             "id": r.id,
#             "vehicle_type": r.vehicle_type,
#             "speed_kmph": r.speed_kmph,
#             "confidence": r.confidence,
#             "track_id": r.track_id,
#             "location": r.location,
#             "detected_at": r.detected_at
#         }
#         for r in result
#     ]


# ============================================================
# === RATA-RATA KECEPATAN ===================================
# ============================================================

def get_average_speed(db):
    """
    Hitung rata-rata kecepatan semua kendaraan
    """
    result = db.query(
        func.avg(VehicleDetection.speed_kmph).label("average_speed")
    ).scalar()

    return {
        "average_speed": round(result, 2) if result else 0.0,
        "unit": "km/h"
    }


# ============================================================
# === STATISTIK HARIAN (KOMPATIBILITAS LAMA) ================
# ============================================================

def get_daily_statistics(db):
    """
    Statistik jumlah kendaraan per jenis untuk hari ini
    """
    today = date.today()

    result = db.query(
        VehicleDetection.vehicle_type,
        func.count(VehicleDetection.id).label("count")
    ).filter(
        func.date(VehicleDetection.detected_at) == today
    ).group_by(VehicleDetection.vehicle_type).all()

    return [{"vehicle_type": r.vehicle_type, "count": r.count} for r in result]


# ============================================================
# === FILTER BERDASARKAN JENIS KENDARAAN ====================
# ============================================================

def get_vehicle_by_type(db, vehicle_type: str):
    """
    Ambil semua data berdasarkan jenis kendaraan (car, motorcycle, bus, dll)
    """
    result = db.query(VehicleDetection).filter(
        VehicleDetection.vehicle_type == vehicle_type
    ).order_by(VehicleDetection.detected_at.desc()).all()

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
