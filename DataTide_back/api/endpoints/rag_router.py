from fastapi import APIRouter
from DataTide_back.schemas.rag import RagQueryRequest, LLMResponse
from DataTide_back.services import rag_service

router = APIRouter()

@router.post("/chatbot", response_model=LLMResponse)
def get_rag_query_response(request: RagQueryRequest):
    """
    Receives a query and returns a RAG model's response.
    """
    response = rag_service.get_llm_response(query=request.message)
    print(response)
    return {"answer": response["answer"]}
