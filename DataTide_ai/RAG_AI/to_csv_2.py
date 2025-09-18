import mysql.connector
from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine

# --- 환경변수 불러오기 ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../..", ".env"))

# 본인 환경에 맞게 수정하세요
USER = os.getenv("MYSQL_USER")
PASSWORD = os.getenv("MYSQL_PASSWORD")
HOST = "localhost"
PORT = 3306
DB = os.getenv("MYSQL_DATABASE")


# SQLAlchemy 엔진 생성
conn = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
engine = create_engine(conn)

# ======================
# 2. 테이블 불러오기
# ======================
df = pd.read_sql("""
        SELECT 
            CASE 
                WHEN i.item_name = 'Calamari' THEN '오징어'
                WHEN i.item_name = 'CutlassFish' THEN '갈치'
                WHEN i.item_name = 'Mackerel' THEN '고등어'
                ELSE i.item_name
            END AS item_name,
        ir.month_date, ir.production, ir.inbound, ir.sales
        FROM item_predict ir
        LEFT JOIN item i ON ir.item_pk = i.item_pk
        WHERE ir.month_date BETWEEN '2025-08-01' AND '2026-02-01'
                          """, engine)

df = df.rename(columns={
    'item_name': '품목',
    'month_date': '날짜',
    'production': '생산량',
    'inbound': '수입량',
    'sales': '판매량'
})

df.to_csv("read_sql_2.csv", index=False, encoding="utf-8-sig")