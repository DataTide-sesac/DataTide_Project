# schemas/ground_weather.py
from pydantic import BaseModel
from datetime import date
from typing import List

class GroundWeatherBase(BaseModel):
    month_date: date
    temperature: float | None = None
    rain: float | None = None

class GroundWeatherCreate(GroundWeatherBase):
    pass

class GroundWeather(GroundWeatherBase):
    ground_pk: int

    class Config:
        from_attributes = True