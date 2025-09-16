# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import api_router
from services import rag_service

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("애플리케이션 시작: RAG 파이프라인 초기화를 시작합니다...")
    rag_service.initialize_rag_pipeline()
    print("애플리케이션 시작: RAG 파이프라인 초기화가 완료되었습니다.")

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def read_root():
    return {"message": "DataTide Backend API에 오신걸 환영합니다!"}