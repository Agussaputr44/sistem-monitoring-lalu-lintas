import threading
from fastapi import FastAPI
from app_optimation.database.session import Base, engine
from app_optimation.core.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as aioredis
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app_optimation.services.yolo_service import VideoStreamService
from app_optimation.api.endpoints.vehicle_endpoint import router as vehicle_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Traffic Monitoring API")

class NgrokBypassMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['ngrok-skip-browser-warning'] = 'true'
        return response

app.add_middleware(NgrokBypassMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

video_service = VideoStreamService()

app.state.video_service = video_service

@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=False  
    )
    backend = RedisBackend(redis)
    FastAPICache.init(backend, prefix="traffic-cache")
    
    thread = threading.Thread(target=app.state.video_service.run_detection, daemon=True)
    thread.start()
    print("🚀 YOLO Detection Thread Started & Service Ready")

app.include_router(vehicle_router)