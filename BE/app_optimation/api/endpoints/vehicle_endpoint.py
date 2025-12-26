from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app_optimation.database.session import SessionLocal
from app_optimation.services import vehicle_service
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

# HAPUS: from app_optimation.main import video_service_instance 
# Baris di atas adalah penyebab error Circular Import

router = APIRouter(prefix="/api", tags=["Traffic Monitoring"])

# Dependency untuk koneksi database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schema input untuk data hasil deteksi YOLO
class VehicleIn(BaseModel):
    vehicle_type: str
    speed_kmph: float
    confidence: float = 0
    track_id: int = 0
    location: str = "Camera Bengkalis"

@router.get("/video_feed")
async def video_feed(request: Request):
    video_service = request.app.state.video_service
    
    return StreamingResponse(
        video_service.generate_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )

# ===============================
# === Endpoint untuk YOLO save ===
# ===============================
@router.post("/vehicle-detections")
async def create_vehicle(data: VehicleIn, db: Session = Depends(get_db)):
    return vehicle_service.save_detection(
        db=db,
        vehicle_type=data.vehicle_type,
        speed_kmph=data.speed_kmph,
        confidence=data.confidence,
        track_id=data.track_id,
        location=data.location
    )

# ========================================
# === Endpoint utama sesuai rancangan ===
# ========================================

@router.get("/traffic-classification")
async def get_traffic_classification(db: Session = Depends(get_db)):
    return await vehicle_service.get_all_classification(db)

@router.get("/traffic-history")
async def get_traffic_history(db: Session = Depends(get_db)):
    return await vehicle_service.get_history(db)

@router.get("/traffic-history/{history_id}")
async def get_traffic_history_by_id(history_id: int, db: Session = Depends(get_db)):
    return await vehicle_service.get_history_by_id(db, history_id)

@router.get("/average-speed")
async def get_average_speed(db: Session = Depends(get_db)):
    return await vehicle_service.get_average_speed(db)