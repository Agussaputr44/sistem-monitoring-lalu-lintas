from fastapi.encoders import jsonable_encoder
from fastapi_cache.decorator import cache
from app_optimation.models.vehicle_model import VehicleDetection
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
import pytz

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
    
    return {
        "status": "success",
        "data": {
            "id": detection.id,
            "vehicle_type": detection.vehicle_type,
            "detected_at": detection.detected_at
        }
    }

@cache(expire=30)  
def get_all_classification(db: Session):
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
    
    
    results = (
        db.query(
            VehicleDetection.id,
            VehicleDetection.vehicle_type,
            VehicleDetection.speed_kmph,
            VehicleDetection.confidence,
            VehicleDetection.location,
            VehicleDetection.detected_at
        )
        .order_by(VehicleDetection.detected_at.desc())
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

@cache(expire=30)
def get_average_speed(db: Session):
    result = db.query(func.avg(VehicleDetection.speed_kmph)).scalar()
    return {
        "average_speed": round(result, 2) if result else 0.0,
        "unit": "km/h"
    }