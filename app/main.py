from fastapi import FastAPI
from app.routers import logs
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
