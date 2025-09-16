# routers/sample.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_sample():
    return {"message": "이것은 sample router입니다. from sample.py"}