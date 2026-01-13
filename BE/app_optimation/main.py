import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as aioredis

# Import modul internal kamu
from app_optimation.database.session import Base, engine
from app_optimation.core.config import settings
from app_optimation.services.yolo_service import VideoStreamService
from app_optimation.api.endpoints.vehicle_endpoint import router as vehicle_router

# 1. Create Database Tables
Base.metadata.create_all(bind=engine)

# 2. DEFINISI APP (Hanya boleh SATU kali, gabungkan Title dan Servers disini)
app = FastAPI(
    title="Traffic Monitoring API",
    servers=[
        {"url": "http://76.13.18.72", "description": "VPS Server (Nginx)"},
        {"url": "http://127.0.0.1:8000", "description": "Localhost (Direct)"}
    ]
)
# 4. Inisialisasi Service Video
video_service = VideoStreamService()
app.state.video_service = video_service

# 5. Startup Event (Redis & Threading)
@app.on_event("startup")
async def startup_event():
    # Inisialisasi Redis Cache
    redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=False
    )
    backend = RedisBackend(redis)
    FastAPICache.init(backend, prefix="traffic-cache")

    # Jalankan YOLO di Thread terpisah
    thread = threading.Thread(target=app.state.video_service.run_detection, daemon=True)
    thread.start()
    print("🚀 YOLO Detection Thread Started & Service Ready")

# 6. Daftarkan Router
app.include_router(vehicle_router)
