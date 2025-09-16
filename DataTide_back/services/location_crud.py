from db.session import db_session
from schemas.location import LocationCreate

def get_locations(skip: int = 0, limit: int = 100):
    """모든 지역 정보 조회 (페이지네이션)"""
    sql = "SELECT * FROM location ORDER BY local_pk ASC LIMIT %s OFFSET %s"
    with db_session() as cursor:
        cursor.execute(sql, (limit, skip))
        return cursor.fetchall()

def get_location_by_pk(local_pk: int):
    """지역코드로 지역 정보 조회"""
    sql = "SELECT * FROM location WHERE local_pk = %s"
    with db_session() as cursor:
        cursor.execute(sql, (local_pk,))
        return cursor.fetchone()

def get_location_by_name(local_name: str):
    """지역 이름으로 지역 정보 조회"""
    sql = "SELECT * FROM location WHERE local_name = %s"
    with db_session() as cursor:
        cursor.execute(sql, (local_name,))
        return cursor.fetchone()

def create_location(location: LocationCreate):
    """새 지역 정보 추가"""
    sql = "INSERT INTO location (local_name) VALUES (%s)"
    new_id = None
    with db_session() as cursor:
        cursor.execute(sql, (location.local_name,))
        new_id = cursor.lastrowid
    return get_location_by_pk(new_id)

def update_location(local_pk: int, new_local_name: str):
    """기존 지역 정보 수정"""
    sql = "UPDATE location SET local_name = %s WHERE local_pk = %s"
    with db_session() as cursor:
        cursor.execute(sql, (new_local_name, local_pk))
        return cursor.rowcount > 0

def delete_location(local_pk: int):
    """지역 정보 삭제"""
    sql = "DELETE FROM location WHERE local_pk = %s"
    with db_session() as cursor:
        cursor.execute(sql, (local_pk,))
        return cursor.rowcount > 0
