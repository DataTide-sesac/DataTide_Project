# api/router.py (수정 후)

from fastapi import APIRouter
from api.endpoints import (
    ground_weather_routers,
    item_routers,
    sample_router,
    rag_router,
    analysis_router,
    location_routers,
    sea_weather_routers,
    item_retail_routers,
)

api_router = APIRouter()

api_router.include_router(ground_weather_routers.router)
api_router.include_router(item_routers.router)
api_router.include_router(sample_router.router, prefix="/sample")
api_router.include_router(location_routers.router)
api_router.include_router(sea_weather_routers.router)
api_router.include_router(item_retail_routers.router)
api_router.include_router(rag_router.router)
api_router.include_router(analysis_router.router)