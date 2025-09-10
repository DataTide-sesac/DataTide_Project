from fastapi import FastAPI
from routers import sample, items, rag, rag_router # rag 라우터 import

app = FastAPI()

# /api/sample 경로로 라우터 포함
app.include_router(sample.router, prefix="/api/sample", tags=["sample"])
# /api/items 경로로 라우터 포함
app.include_router(items.router, prefix="/api/items", tags=["items"])
# /api/rag 경로로 라우터 포함
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
# rag_router 추가
app.include_router(rag_router.router, prefix="/rag", tags=["RAG"])

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}