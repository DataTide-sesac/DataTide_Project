from db.session import db_session
from schemas.sea_weather import SeaWeatherCreate
from services.location_crud import get_location_by_name

def get_sea_weather(sea_pk: int):
    """sea_pk로 단일 해상 날씨 정보 조회"""
    with db_session() as cursor:
        sql = "SELECT * FROM sea_weather WHERE sea_pk = %s"
        cursor.execute(sql, (sea_pk,))
        return cursor.fetchone()

def get_sea_weathers(skip: int = 0, limit: int = 100):
    """모든 해상 날씨 정보 조회 (페이지네이션)"""
    with db_session() as cursor:
        sql = "SELECT * FROM sea_weather ORDER BY sea_pk ASC LIMIT %s OFFSET %s"
        cursor.execute(sql, (limit, skip))
        return cursor.fetchall()

def create_sea_weather(sea_weather: SeaWeatherCreate):
    """새 해상 날씨 정보 생성"""
    location = get_location_by_name(sea_weather.local_name)
    if not location:
        return None
    local_pk = location['local_pk']

    with db_session() as cursor:
        sql = """
            INSERT INTO sea_weather
            (local_pk, month_date, temperature, wind, salinity,
             wave_height, wave_period, wave_speed, rain, snow)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            local_pk,
            sea_weather.month_date,
            sea_weather.temperature,
            sea_weather.wind,
            sea_weather.salinity,
            sea_weather.wave_height,
            sea_weather.wave_period,
            sea_weather.wave_speed,
            sea_weather.rain,
            sea_weather.snow
        )
        cursor.execute(sql, values)
        new_id = cursor.lastrowid

    return get_sea_weather(new_id)
