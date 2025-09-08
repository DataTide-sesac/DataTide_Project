# services/rag_service.py

def get_rag_response(query: str) -> dict:
    """
    주어진 쿼리에 대해 RAG 모델을 호출하고 응답을 반환하는 서비스 함수입니다.
    실제 구현에서는 이곳에 LangChain, LlamaIndex 또는 직접 구현한 RAG 파이프라인 코드가 들어갑니다.
    """
    print(f"RAG 모델 호출: '{query}'")

    # --- 할일:여기에 실제 RAG 파이프라인 로직 구현 ---
    # 1. 쿼리 전처리 Query Pre-processing
    # 2. Vector DB / Retriever에서 관련 문서 검색
    # 3. LLM에 검색된 문서와 쿼리를 함께 전달하여 답변 생성
    # -----------------------------------------

    # 아래는 예시 응답입니다.
    example_response = {
        "query": query,
        "answer": f"'{query}'에 대한 답변입니다.",
        "source_documents": [
            {"source": "doc_1.pdf", "content": "관련 문서 1의 내용..."},
            {"source": "doc_2.txt", "content": "관련 문서 2의 내용..."},
        ]
    }

    print("RAG 모델 응답 수신")
    return example_response