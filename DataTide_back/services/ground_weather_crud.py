# services/ground_weather_crud.py
from sqlalchemy.orm import Session
    # Import 절대경로로 수정
from DataTide_back.models.ground_weather import GroundWeather
from DataTide_back.schemas.ground_weather import GroundWeatherCreate
from typing import List

def create_ground_weathers_bulk(db: Session, weathers: List[GroundWeatherCreate]):
    db_weathers = [GroundWeather(**weather.model_dump()) for weather in weathers]
    db.add_all(db_weathers)
    db.commit()
    return db_weathers
