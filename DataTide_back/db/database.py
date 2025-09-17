import pymysql
from DataTide_back.core.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# 📄 글로벌 변수 정의 (필요시 재사용 가능)
_connection = None

def _create_connection():
   """새로운 데이터베이스 연결 생성"""
   global _connection
   if _connection is None or _connection.closed:
       _connection = pymysql.connect(
           host=DB_HOST,
           port=int(DB_PORT),
           user=DB_USER,
           password=DB_PASSWORD,
           db=DB_NAME,
           charset='utf8mb4',
           cursorclass=pymysql.cursors.DictCursor
       )
   return _connection

def get_connection():
   """현재 데이터베이스 연결 반환, 연결 없으면 새로 생성"""
   return _create_connection()

def close_connection():
   """데이터베이스 연결 닫기"""
   global _connection
   if _connection:
       _connection.close()
       _connection = None