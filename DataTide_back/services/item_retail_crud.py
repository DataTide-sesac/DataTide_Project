from db.session import db_session
from schemas.item_retail import ItemRetailCreate

def get_item_pk_by_name(item_name: str):
    """Helper function to get item_pk from item_name."""
    with db_session() as cursor:
        sql = "SELECT item_pk FROM item_retail WHERE item_name = %s"
        cursor.execute(sql, (item_name,))
        result = cursor.fetchone()
        return result['item_pk'] if result else None

def get_item_retail(retail_pk: int):
    """retail_pk로 단일 소매 정보 조회"""
    with db_session() as cursor:
        sql = "SELECT * FROM item_retail WHERE retail_pk = %s"
        cursor.execute(sql, (retail_pk,))
        return cursor.fetchone()

def get_item_retails(skip: int = 0, limit: int = 100):
    """모든 소매 정보 조회 (페이지네이션)"""
    with db_session() as cursor:
        sql = "SELECT * FROM item_retail ORDER BY retail_pk ASC LIMIT %s OFFSET %s"
        cursor.execute(sql, (limit, skip))
        return cursor.fetchall()

def create_item_retail(item_retail: ItemRetailCreate):
    """새 소매 정보 생성"""
    item_pk = get_item_pk_by_name(item_retail.item_name)
    if not item_pk:
        return None

    with db_session() as cursor:
        sql = """
            INSERT INTO item_retail
            (item_pk, production, inbound, sales, month_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            item_pk,
            item_retail.production,
            item_retail.inbound,
            item_retail.sales,
            item_retail.month_date
        )
        cursor.execute(sql, values)
        new_id = cursor.lastrowid

    return get_item_retail(new_id)
