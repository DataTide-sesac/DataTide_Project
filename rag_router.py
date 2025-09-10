# DataTide_back/routers/rag_router.py

from fastapi import APIRouter
from services.rag_service import get_answer_from_rag
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QueryRequest):
    answer = await get_answer_from_rag(request.question)
    return {"question": request.question, "answer": answer}