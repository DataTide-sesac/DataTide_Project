from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base

class Location(Base):
    __tablename__ = "location"

    local_pk = Column(Integer, primary_key=True, autoincrement=True)
    local_name = Column(String(30))

    # Relationship to sea_weather
    sea_weathers = relationship("SeaWeather", back_populates="location")