# services/item_crud.py
from db.session import db_session
from schemas.item import ItemCreate

def get_item(item_pk: int):
    """item_pk로 단일 아이템 조회"""
    with db_session() as cursor:
        sql = "SELECT * FROM item WHERE item_pk = %s"
        cursor.execute(sql, (item_pk,))
        return cursor.fetchone()

def get_item_by_name(item_name: str):
    """item_name으로 단일 아이템 조회"""
    with db_session() as cursor:
        sql = "SELECT * FROM item WHERE item_name = %s"
        cursor.execute(sql, (item_name,))
        return cursor.fetchone()

def get_items(skip: int = 0, limit: int = 100):
    """모든 아이템 조회 (페이지네이션)"""
    with db_session() as cursor:
        sql = "SELECT * FROM item ORDER BY item_pk ASC LIMIT %s OFFSET %s"
        cursor.execute(sql, (limit, skip))
        return cursor.fetchall()

def create_item(item: ItemCreate):
    """새 아이템 생성"""
    with db_session() as cursor:
        sql = "INSERT INTO item (item_name) VALUES (%s)"
        cursor.execute(sql, (item.item_name,))
        new_id = cursor.lastrowid
    return get_item(new_id)

def create_multiple_items(items: list[ItemCreate]):
    """다수의 새 아이템 생성"""
    new_ids = []
    with db_session() as cursor:
        # executemany is efficient but doesn't return IDs easily.
        # Looping to get each new ID.
        for item in items:
            sql = "INSERT INTO item (item_name) VALUES (%s)"
            cursor.execute(sql, (item.item_name,))
            new_ids.append(cursor.lastrowid)

    if not new_ids:
        return []

    # Fetch all newly created items in a single query.
    with db_session() as cursor:
        placeholders = ','.join(['%s'] * len(new_ids))
        sql = f"SELECT * FROM item WHERE item_pk IN ({placeholders})"
        cursor.execute(sql, tuple(new_ids))
        return cursor.fetchall()
