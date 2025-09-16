from fastapi import APIRouter
from schemas.rag import RagQueryRequest, RagQueryResponse
from services import rag_service

router = APIRouter()

@router.post("/query", response_model=RagQueryResponse)
def get_rag_query_response(request: RagQueryRequest):
    """
    Receives a query and returns a RAG model's response.
    """
    response = rag_service.get_rag_response(query=request.query)
    return response
