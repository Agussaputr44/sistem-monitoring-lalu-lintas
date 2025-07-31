from pydantic import BaseModel

class LogCreate(BaseModel):
    type: str
    speed: float

class LogOut(LogCreate):
    id: int

    class Config:
        from_artibutes = True
