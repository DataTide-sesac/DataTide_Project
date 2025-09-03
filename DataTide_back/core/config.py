# core/config.py
import os

# 아래 "sqlite:///./test.db" 부분을 실제 MySQL 연결 주소로 수정해주세요.
# 예: "mysql+pymysql://user:password@host:port/db_name"
# 데이터베이스 URL 설정 (MySQL)                                              mysql에만든db명
DB_URL = os.getenv("DB_URL", "mysql+pymysql://team_dt:dt_1234@localhost:3306/datatide_db")

# 기타 설정...
