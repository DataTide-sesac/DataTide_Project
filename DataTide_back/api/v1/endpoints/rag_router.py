from fastapi import APIRouter
from DataTide_back.schemas.rag import RagQueryRequest
from DataTide_back.services import rag_service

router = APIRouter()

@router.post("/chatbot")
def get_rag_query_response(request: RagQueryRequest):
    """
    Receives a query and returns a RAG model's response.
    """
    response = rag_service.get_rag_response(query=request.message)
    return {"reply": response["answer"]}
