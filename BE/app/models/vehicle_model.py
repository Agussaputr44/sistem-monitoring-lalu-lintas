from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database.session import Base

class VehicleDetection(Base):
    __tablename__ = "vehicle_detections"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String(50))
    speed_kmph = Column(Float)
    confidence = Column(Float)
    track_id = Column(Integer)
    location = Column(String(100))
    detected_at = Column(DateTime, default=datetime.utcnow)
