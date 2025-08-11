from sqlalchemy.orm import Session
from app.models.vehicle_model import VehicleDetection
from sqlalchemy import func
from datetime import date, datetime
from fastapi import HTTPException

def save_detection(db: Session, vehicle_type: str, speed_kmph: float):
    detection = VehicleDetection(vehicle_type=vehicle_type, speed_kmph=speed_kmph)
    db.add(detection)
    db.commit()
    db.refresh(detection)
    return detection

def get_daily_statistics(db: Session):
    raw_results = db.query(
        VehicleDetection.vehicle_type,
        func.count(VehicleDetection.id).label("count")
    ).filter(
        func.date(VehicleDetection.detected_at) == date.today()
    ).group_by(VehicleDetection.vehicle_type).all()

    return [{"vehicle_type": r[0], "count": r[1]} for r in raw_results]

def get_vehicle_by_type(db: Session, vehicle_type: str):
    return db.query(VehicleDetection
    ).filter(VehicleDetection.vehicle_type == vehicle_type).all()
    
def get_history(db: Session):
    return db.query(VehicleDetection
    ).order_by(VehicleDetection.detected_at.desc()
    ).all()
    
def get_history_by_date(db: Session, date_str: str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format tanggal harus YYYY-MM-DD")

    results = db.query(VehicleDetection).filter(
        func.date(VehicleDetection.detected_at) == date_obj
    ).order_by(VehicleDetection.detected_at.desc()).all()

    return results
