from db.session import db_session
from schemas.ground_weather import GroundWeatherCreate
from typing import List

def create_ground_weathers_bulk(weathers: List[GroundWeatherCreate]):
    """다수의 지상 날씨 정보 생성"""
    new_ids = []
    with db_session() as cursor:
        for weather in weathers:
            sql = """
                INSERT INTO ground_weather
                (month_date, temperature, rain)
                VALUES (%s, %s, %s)
            """
            values = (
                weather.month_date,
                weather.temperature,
                weather.rain
            )
            cursor.execute(sql, values)
            new_ids.append(cursor.lastrowid)

    if not new_ids:
        return []

    # Fetch all newly created items in a single query.
    with db_session() as cursor:
        placeholders = ','.join(['%s'] * len(new_ids))
        sql = f"SELECT * FROM ground_weather WHERE ground_pk IN ({placeholders})"
        cursor.execute(sql, tuple(new_ids))
        return cursor.fetchall()
