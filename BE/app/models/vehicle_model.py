from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database.session import Base

class VehicleDetection(Base):
    __tablename__ = "vehicle_detections"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String(20), nullable=False)
    speed_kmph = Column(Float)
    detected_at = Column(DateTime, default=datetime.utcnow)
