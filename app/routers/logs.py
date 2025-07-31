from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schema

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schema.LogOut)
def create_log(log: schema.LogCreate, db: Session = Depends(get_db)):
    db_log = models.Log(type=log.type, speed=log.speed)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
