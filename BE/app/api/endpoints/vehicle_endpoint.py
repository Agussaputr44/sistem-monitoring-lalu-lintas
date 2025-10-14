from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.services import vehicle_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/vehicle-detections", tags=["Vehicle Detections"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class VehicleIn(BaseModel):
    vehicle_type: str
    speed_kmph: float
    confidence: float = 0
    track_id: int = 0
    location: str = "Camera Bengkalis"

@router.post("/")
def create_vehicle(data: VehicleIn, db: Session = Depends(get_db)):
    return vehicle_service.save_detection(
        db, data.vehicle_type, data.speed_kmph, data.confidence, data.track_id, data.location
    )

@router.get("/statistic")
def get_stats(db: Session = Depends(get_db)):
    return vehicle_service.get_daily_statistics(db)

@router.get("/statistic/{vehicle_type}")
def get_vehicle_by_type(vehicle_type: str, db: Session = Depends(get_db)):
    return vehicle_service.get_vehicle_by_type(db, vehicle_type)

@router.get("/history")
def get_history(db: Session = Depends(get_db)): 
    return vehicle_service.get_history(db)

@router.get("/history/{date}")
def get_history_by_date(date: str, db: Session = Depends(get_db)):
    return vehicle_service.get_history_by_date(db, date)
