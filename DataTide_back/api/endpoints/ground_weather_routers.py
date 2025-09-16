from fastapi import APIRouter
from typing import List

from services import ground_weather_crud
from schemas.ground_weather import GroundWeather, GroundWeatherCreate

router = APIRouter()

@router.post("/bulk", response_model=List[GroundWeather])
def create_ground_weathers_in_bulk(weathers: List[GroundWeatherCreate]):
    return ground_weather_crud.create_ground_weathers_bulk(weathers=weathers)
