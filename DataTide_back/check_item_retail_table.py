import pymysql

conn = pymysql.connect(
    host='localhost',
    user='team_dt',
    password='dt_1234',
    db='datatide_db',
    charset='utf8mb4'  # 한글 등 문자 지원
)

try:
    with conn.cursor() as cursor:
        cursor.execute("select * from item;")
        result = cursor.fetchone()
        if result:
            print("item_retail 테이블이 존재합니다.")
        else:
            print("item_retail 테이블이 없습니다.")
finally:
    conn.close()
