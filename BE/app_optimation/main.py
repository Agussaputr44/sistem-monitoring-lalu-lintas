from fastapi import FastAPI
from app_optimation.database.session import Base, engine
from app_optimation.core.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as aioredis
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Traffic Monitoring API")
app.add_middleware(
    CORSMiddleware,
   allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=False  
    )
    backend = RedisBackend(redis)
    FastAPICache.init(backend, prefix="traffic-cache")
    print("✅ Redis cache connected and initialized")

from app_optimation.api.endpoints.vehicle_endpoint import router as vehicle_router
app.include_router(vehicle_router)
