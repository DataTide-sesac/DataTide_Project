from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

    # Import 절대경로로 수정
from DataTide_back.services import ground_weather_crud
from DataTide_back.schemas.ground_weather import GroundWeather, GroundWeatherCreate
from DataTide_back.core.database import get_db

router = APIRouter()

@router.post("/bulk", response_model=List[GroundWeather])
def create_ground_weathers_in_bulk(weathers: List[GroundWeatherCreate], db: Session = Depends(get_db)):
    return ground_weather_crud.create_ground_weathers_bulk(db=db, weathers=weathers)
