from fastapi import FastAPI
from app.api.endpoints import vehicle_endpoint 
from app.database.session import engine
from app.models import vehicle_model

vehicle_model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(vehicle_endpoint.router, prefix="/vehicles", tags=["Vehicles"])

@app.get("/")
def root():
    return {"message": "Monitoring kendaraan API aktif"}
