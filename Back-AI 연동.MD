-----

# **백엔드-RAG AI 서버 연동 개발 가이드**

이 문서는 Python 기반의 백엔드(`DataTide_back`)와 RAG AI 모델 서버(`DataTide_ai`)를 분리하여 API로 연동하는 전체 과정을 설명합니다.

### **최종 아키텍처**

사용자의 요청은 백엔드 서버를 통해 AI 서버로 전달되며, AI 서버는 RAG 모델을 통해 생성된 답변을 다시 백엔드를 거쳐 사용자에게 반환합니다.

**흐름**: `사용자` ↔ `백엔드 서버 (포트 8000)` ↔ `AI 서버 (포트 8001)` ↔ `RAG 모델`

-----

## **1단계: RAG AI 서버 구축 (`DataTide_ai`)**

AI 모델의 추론을 전담하고, 이를 API로 노출하는 서버를 구축합니다.

### **1. 프로젝트 준비**

  - **폴더 구조**
    ```
    DataTide_ai/
    └── RAG_AI/
        ├── data/
        │   └── sample_document.txt
        ├── .env
        ├── main.py
        └── rag_model.py
    ```
  - **필요 라이브러리 설치**
    ```bash
    pip install fastapi "uvicorn[standard]" python-dotenv langchain langchain-openai langchain-community faiss-cpu sentence-transformers
    ```
  - **환경 변수 설정 (`.env` 파일)**
    `sk-...` 부분에 실제 OpenAI API 키를 입력합니다.
    ```
    OPENAI_API_KEY="sk-..."
    ```

### **2. RAG 모델 로직 작성 (`rag_model.py`)**

LangChain을 사용하여 RAG 파이프라인의 핵심 로직을 구현합니다.

```python
# DataTide_ai/RAG_AI/rag_model.py

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

def setup_rag_chain():
    """RAG 파이프라인을 설정하고 체인을 반환합니다."""
    print(">> RAG 체인 설정을 시작합니다...")
    load_dotenv()
    
    # 1. 문서 로드
    loader = DirectoryLoader(path="./data", glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    documents = loader.load()
    if not documents:
        raise ValueError("'./data' 폴더에 참조할 문서가 없습니다.")

    # 2. 문서 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(documents)

    # 3. 임베딩 및 벡터 DB 저장
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-srobert-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vector_store = FAISS.from_documents(split_docs, embeddings)

    # 4. 검색기(Retriever) 생성
    retriever = vector_store.as_retriever()

    # 5. 프롬프트 템플릿 정의
    template = """
    당신은 전문가입니다. 사용자의 질문에 대해 아래의 'context' 정보만을 사용하여 답변해주세요.
    [Context]: {context}
    [Question]: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 6. LLM 모델 정의
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1)

    # 7. RAG 체인 구성
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print(">> RAG 체인 설정이 완료되었습니다! ✅")
    return rag_chain

def get_rag_response(chain, query: str) -> str:
    """생성된 RAG 체인을 사용하여 질문에 대한 답변을 반환합니다."""
    print(f">> RAG 모델 호출: '{query}'")
    response = chain.invoke(query)
    print(">> RAG 모델 응답 수신 완료.")
    return response
```

### **3. API 서버 작성 (`main.py`)**

FastAPI를 사용하여 `/rag-query` 엔드포인트를 생성하고 `rag_model.py`의 로직을 호출합니다.

```python
# DataTide_ai/RAG_AI/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from rag_model import setup_rag_chain, get_rag_response

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

# 서버 시작 시 RAG 체인을 미리 로드합니다.
try:
    rag_chain = setup_rag_chain()
except Exception as e:
    print(f"🚨 RAG 체인 로딩 중 오류 발생: {e}")
    rag_chain = None

@app.post("/rag-query")
async def query_rag(request: QueryRequest):
    """사용자 질문을 받아 RAG 모델의 답변을 반환합니다."""
    if rag_chain is None:
        return {"error": "RAG 모델이 로드되지 않았습니다."}
    
    answer = get_rag_response(rag_chain, request.question)
    return {"answer": answer}
```

-----

## **2단계: 백엔드 서버 구축 (`DataTide_back`)**

사용자 요청을 받아 AI 서버와 통신하는 역할을 합니다.

### **1. 프로젝트 준비**

  - **필요 라이브러리 설치**
    ```bash
    pip install fastapi "uvicorn[standard]" httpx
    ```

### **2. AI 서버 호출 서비스 작성 (`services/rag_service.py`)**

`httpx`를 이용해 AI 서버의 API를 호출하는 비동기 함수를 구현합니다.

```python
# DataTide_back/services/rag_service.py

import httpx

# RAG AI 서버의 API 주소
RAG_API_URL = "http://127.0.0.1:8001/rag-query"

async def get_answer_from_rag(question: str) -> str:
    """HTTP 클라이언트를 사용해 RAG AI 서버에 질문을 보내고 답변을 받아옵니다."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(RAG_API_URL, json={"question": question}, timeout=30.0)
            response.raise_for_status() # 200번대 상태 코드가 아니면 예외 발생
            data = response.json()
            return data.get("answer", "답변을 가져오는 데 실패했습니다.")
        except httpx.RequestError as e:
            print(f"RAG API 요청 중 오류 발생: {e}")
            return "AI 서버에 연결할 수 없거나 응답이 없습니다."
```

### **3. 사용자 API 라우터 작성 (`routers/rag_router.py`)**

사용자에게 노출될 `/rag/ask` 엔드포인트를 정의하고 위에서 만든 서비스를 호출합니다.

```python
# DataTide_back/routers/rag_router.py

from fastapi import APIRouter
from pydantic import BaseModel
from services.rag_service import get_answer_from_rag

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QueryRequest):
    answer = await get_answer_from_rag(request.question)
    return {"question": request.question, "answer": answer}
```

### **4. 메인 어플리케이션에 라우터 등록 (`main.py`)**

```python
# DataTide_back/main.py

from fastapi import FastAPI
from routers import rag_router # 다른 라우터들도 이곳에서 import

app = FastAPI()

# 다른 라우터 등록
# app.include_router(...)

# RAG 라우터 등록
app.include_router(rag_router.router, prefix="/rag", tags=["RAG"])
```

-----

## **3단계: 시스템 실행 및 테스트**

### **1. 서버 실행**

두 개의 터미널을 열고 각각의 서버를 실행합니다.

  - **터미널 1: AI 서버 실행**

    ```bash
    # DataTide_ai/RAG_AI 폴더로 이동
    cd path/to/DataTide_ai/RAG_AI
    # 가상환경 활성화
    .\venv\Scripts\activate
    # 서버 시작 (8001 포트)
    uvicorn main:app --reload --port 8001
    ```

  - **터미널 2: 백엔드 서버 실행**

    ```bash
    # DataTide_back 폴더로 이동
    cd path/to/DataTide_back
    # 가상환경 활성화
    .\venv\Scripts\activate
    # 서버 시작 (8000 포트)
    uvicorn main:app --reload
    ```

### **2. 연동 테스트**

1.  웹 브라우저에서 백엔드 서버의 API 문서 `http://127.0.0.1:8000/docs` 로 접속합니다.
2.  `/rag/ask` 엔드포인트를 찾아 펼치고 \*\*"Try it out"\*\*을 클릭합니다.
3.  **Request body**에 질문을 JSON 형식으로 입력합니다. (예: `{"question": "오늘 날씨 어때?"}`)
4.  **"Execute"** 버튼을 클릭하여 요청을 보냅니다.
5.  **"Server response"** 섹션에서 AI 서버로부터 온 답변이 포함된 최종 응답을 확인합니다.

이 과정을 통해 두 서버가 성공적으로 연동되었음을 확인할 수 있습니다.
