import sys
import os

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from DataTide_back.api.v1.router import api_router

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

app.include_router(api_router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "DataTide Backend API에 오신걸 환영합니다!"}
