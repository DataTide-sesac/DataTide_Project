from sqlalchemy.orm import Session
from DataTide_back.models.sea_weather import SeaWeather
from DataTide_back.schemas.sea_weather import SeaWeatherCreate
from DataTide_back.models.location import Location # To look up local_pk

def get_sea_weather(db: Session, sea_pk: int):
    return db.query(SeaWeather).filter(SeaWeather.sea_pk == sea_pk).first()

def get_sea_weathers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SeaWeather).offset(skip).limit(limit).all()

def create_sea_weather(db: Session, sea_weather: SeaWeatherCreate):
    # Look up local_pk from local_name
    location = db.query(Location).filter(Location.local_name == sea_weather.local_name).first()
    if not location:
        # This should ideally be handled by the router with an HTTPException
        # but for service layer, we can return None or raise a custom exception
        return None # Or raise a specific error

    db_sea_weather = SeaWeather(
        local_pk=location.local_pk,
        month_date=sea_weather.month_date,
        temperature=sea_weather.temperature,
        wind=sea_weather.wind,
        salinity=sea_weather.salinity,
        wave_height=sea_weather.wave_height,
        wave_period=sea_weather.wave_period,
        wave_speed=sea_weather.wave_speed,
        rain=sea_weather.rain,
        snow=sea_weather.snow
    )
    db.add(db_sea_weather)
    db.commit()
    db.refresh(db_sea_weather)
    return db_sea_weather
