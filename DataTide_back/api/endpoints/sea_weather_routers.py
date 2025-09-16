from fastapi import APIRouter, HTTPException, status
from typing import List

from services import sea_weather_crud
from schemas.sea_weather import SeaWeather, SeaWeatherCreate

router = APIRouter(prefix="/sea_weathers", tags=["sea_weathers"])

@router.post("/", response_model=SeaWeather)
def create_sea_weather(sea_weather: SeaWeatherCreate):
    db_sea_weather = sea_weather_crud.create_sea_weather(sea_weather=sea_weather)
    if db_sea_weather is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with name '{sea_weather.local_name}' not found."
        )
    return db_sea_weather

@router.get("/", response_model=List[SeaWeather])
def read_sea_weathers(skip: int = 0, limit: int = 100):
    sea_weathers = sea_weather_crud.get_sea_weathers(skip=skip, limit=limit)
    return sea_weathers

@router.get("/{sea_pk}", response_model=SeaWeather)
def read_sea_weather(sea_pk: int):
    db_sea_weather = sea_weather_crud.get_sea_weather(sea_pk=sea_pk)
    if db_sea_weather is None:
        raise HTTPException(status_code=404, detail="SeaWeather not found")
    return db_sea_weather
