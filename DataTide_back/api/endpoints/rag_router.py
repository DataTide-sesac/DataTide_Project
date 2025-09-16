# api/endpoints/rag_router.py

from fastapi import APIRouter
# --- 아래 두 줄에서 'DataTide_back.' 부분을 삭제했습니다 ---
from schemas.rag import RagQueryRequest
from services import rag_service

router = APIRouter()

@router.post("/chatbot")
def get_rag_query_response(request: RagQueryRequest):
    """
    Receives a query and returns a RAG model's response.
    """
    response = rag_service.get_rag_response(query=request.message)
    return {"reply": response["answer"]}