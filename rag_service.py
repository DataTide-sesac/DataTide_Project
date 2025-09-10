# DataTide_back/services/rag_service.py

import httpx

# RAG AI 서버의 API 주소
# uvicorn 실행 시 포트를 8001로 지정했으므로 주소도 일치시켜야 합니다.
RAG_API_URL = "http://127.0.0.1:8001/rag-query"

async def get_answer_from_rag(question: str) -> str:
    """
    HTTP 클라이언트를 사용해 RAG AI 서버에 질문을 보내고 답변을 받아오는 함수
    """
    # 비동기 HTTP 요청을 위해 AsyncClient를 사용합니다.
    async with httpx.AsyncClient() as client:
        try:
            # POST 요청으로 RAG AI 서버에 question을 JSON 형식으로 보냅니다.
            response = await client.post(RAG_API_URL, json={"question": question}, timeout=30.0)
            
            # 응답 상태 코드가 200번대가 아니면 예외를 발생시킵니다.
            response.raise_for_status()
            
            data = response.json()
            return data.get("answer", "답변을 가져오는 데 실패했습니다.")

        except httpx.RequestError as e:
            # 네트워크 연결 오류 등 요청 관련 문제가 발생했을 때 처리
            print(f"RAG API 요청 중 오류 발생: {e}")
            return "AI 서버에 연결할 수 없거나 응답이 없습니다."