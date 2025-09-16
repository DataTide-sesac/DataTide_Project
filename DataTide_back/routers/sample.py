from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_sample():
    return {"message": "This is a sample router from sample.py"}