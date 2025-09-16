# config.py ㅣ프로젝트 설정 파일
#  SQLite 기반의 설정을 MySQL/MariaDB 기반으로 변경
import os
from dotenv import load_dotenv

# .env 파일 로드 (프로젝트 루트에 있다고 가정)
load_dotenv()

# DataTide_back/core/config.py
# 프로젝트 루트를 기준으로 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# core -> DataTide_back -> project_root
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))

# 데이터베이스 연결 설정
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "team_dt")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dt_1234")
DB_NAME = os.getenv("DB_NAME", "datatide_db")

# MySQL SQLAlchemy 연결 URL
DB_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# 로깅 및 디버깅용 설정
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 프로젝트 주요 경로들
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# 필요한 디렉토리 생성
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def get_database_config():
    """데이터베이스 연결 설정 딕셔너리 반환"""
    return {
        'host': DB_HOST,
        'port': int(DB_PORT),
        'user': DB_USER,
        'password': DB_PASSWORD,
        'database': DB_NAME,
        'charset': 'utf8mb4'
    }

if __name__ == "__main__":
    print("🔍 Database Configuration:")
    print(f"  - Host: {DB_HOST}")
    print(f"  - Port: {DB_PORT}")
    print(f"  - User: {DB_USER}")
    print(f"  - Database: {DB_NAME}")
    print("\n🌐 Database URL:")
    print(DB_URL)