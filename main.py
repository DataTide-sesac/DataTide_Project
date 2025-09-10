# DataTide_ai/RAG_AI/main.py

from fastapi import FastAPI
from pydantic import BaseModel
# rag_model.py에서 우리가 만든 함수들을 가져옵니다.
from rag_model import setup_rag_chain, get_rag_response

app = FastAPI()

# Pydantic 모델 정의
class QueryRequest(BaseModel):
    question: str

# 서버가 시작될 때 RAG 체인을 미리 한 번만 생성합니다.
# 이렇게 하면 매번 요청이 올 때마다 모델을 로드하는 것을 방지할 수 있습니다.
try:
    rag_chain = setup_rag_chain()
    print("✅ RAG 체인이 성공적으로 로드되었습니다.")
except Exception as e:
    print(f"🚨 RAG 체인 로딩 중 오류 발생: {e}")
    rag_chain = None

@app.post("/rag-query")
async def query_rag(request: QueryRequest):
    """
    사용자의 질문을 받아 RAG 모델의 답변을 반환합니다.
    """
    if rag_chain is None:
        return {"error": "RAG 모델이 로드되지 않았습니다. 서버 로그를 확인해주세요."}
    
    question = request.question
    
    # 미리 생성된 체인을 사용하여 실제 RAG 답변을 가져옵니다.
    answer = get_rag_response(rag_chain, question)

    return {"answer": answer}