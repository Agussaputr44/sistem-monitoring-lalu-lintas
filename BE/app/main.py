from fastapi import FastAPI
from app.database.session import Base, engine
from app.api.endpoints.vehicle_endpoint import router as vehicle_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Traffic Monitoring API")

app.include_router(vehicle_router)

@app.get("/")
def root():
    return {"message": "Traffic Monitoring API is running!"}