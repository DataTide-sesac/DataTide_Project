
from sqlalchemy import Column, BigInteger, Integer, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class SeaWeather(Base):
    __tablename__ = "sea_weather"

    sea_pk = Column(BigInteger, primary_key=True, autoincrement=True)
    local_pk = Column(Integer, ForeignKey("location.local_pk"))
    month_date = Column(Date)
    temperature = Column(Float)
    wind = Column(Float)
    salinity = Column(Float)
    wave_height = Column(Float)
    wave_period = Column(Float)
    wave_speed = Column(Float)
    rain = Column(Float)
    snow = Column(Float)

    # Relationship to location
    location = relationship("Location", back_populates="sea_weathers")