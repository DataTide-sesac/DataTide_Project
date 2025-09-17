from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..schemas import item, item_retail, ground_weather, sea_weather, location, rag
from ..services import item_crud, item_retail_crud, ground_weather_crud, sea_weather_crud, location_crud
from ..services.rag_service import get_llm_response

from .endpoints import (
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

@api_router.post("/rag", response_model=rag.LLMResponse)
async def get_rag_answer(query: rag.RagQueryRequest):
    """
    RAG 모델을 사용하여 질문에 대한 답변을 생성합니다.
    """
    response = get_llm_response(query.message)
    if "error" in response:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response["error"])
    return rag.LLMResponse(answer=response["answer"])