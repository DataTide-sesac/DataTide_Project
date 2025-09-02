from sqlalchemy import Column, BigInteger, Date, Float
from core.database import Base

class GroundWeather(Base):
    __tablename__ = "ground_weather"

    ground_pk = Column(BigInteger, primary_key=True, autoincrement=True)
    month_date = Column(Date)
    temperature = Column(Float)
    rain = Column(Float)
    snow = Column(Float)