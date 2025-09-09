# models/ground_weather.py
from sqlalchemy import Column, BigInteger, Date, Float
from DataTide_back.core.database import Base

class GroundWeather(Base):
    __tablename__ = "ground_weather"

    ground_pk = Column(BigInteger, primary_key=True, autoincrement=True)
    month_date = Column(Date)
    temperature = Column(Float, nullable=True)
    rain = Column(Float, nullable=True)
