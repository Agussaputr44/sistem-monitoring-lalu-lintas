from app.models.vehicle_model import VehicleDetection
from datetime import datetime
from sqlalchemy import func

def save_detection(db, vehicle_type, speed_kmph, confidence=0.0, track_id=0, location="Camera Bengkalis"):
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
    return detection

def get_daily_statistics(db):
    return db.query(
        VehicleDetection.vehicle_type,
        func.count(VehicleDetection.id).label("count")
    ).group_by(VehicleDetection.vehicle_type).all()

def get_vehicle_by_type(db, vehicle_type):
    return db.query(VehicleDetection).filter(VehicleDetection.vehicle_type == vehicle_type).all()

def get_history(db):
    return db.query(VehicleDetection).order_by(VehicleDetection.detected_at.desc()).all()

def get_history_by_date(db, date):
    return db.query(VehicleDetection).filter(
        func.date(VehicleDetection.detected_at) == date
    ).order_by(VehicleDetection.detected_at.desc()).all()
