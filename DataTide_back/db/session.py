import contextlib
from db.database import get_connection, close_connection

@contextlib.contextmanager
def db_session():
    """데이터베이스 세션 관리 컨텍스트 매니저"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        cursor.close()
        close_connection()