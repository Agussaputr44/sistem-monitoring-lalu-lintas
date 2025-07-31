from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50))
    speed = Column(Float)
