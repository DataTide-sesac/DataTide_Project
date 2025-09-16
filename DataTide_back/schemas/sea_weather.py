from pydantic import BaseModel
from datetime import date
from typing import Optional

class SeaWeatherBase(BaseModel):
    month_date: date
    temperature: float
    wind: float
    salinity: float
    wave_height: float
    wave_period: float
    wave_speed: float
    rain: float
    snow: float

class SeaWeatherCreate(SeaWeatherBase):
    local_name: str # For creation, we'll use local_name

class SeaWeather(SeaWeatherBase):
    sea_pk: int
    local_pk: int # For response, we'll have local_pk

    class Config:
        from_attributes = True
