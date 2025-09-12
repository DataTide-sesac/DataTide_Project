import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 데이터베이스 설정
class DatabaseConfig:
    """데이터베이스 설정 클래스"""
    
    # MySQL 연결 정보
    DB_HOST = 'localhost'
    DB_USER = 'team_dt'
    DB_PASSWORD = 'dt_1234'
    DB_NAME = 'datatide_db'
    DB_PORT = 3306
    DB_CHARSET = 'utf8'
    
    # SQLAlchemy 연결 URI
    # 기존 프로젝트의 설정 파일에서
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://team_dt:dt_1234@localhost:3306/datatide_db?charset=utf8'
    
    # SQLAlchemy 설정
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # SQL 쿼리 로그 출력 (개발 시에만 True)

# SQLAlchemy 엔진 및 세션 설정
engine = create_engine(
    DatabaseConfig.SQLALCHEMY_DATABASE_URI,
    echo=DatabaseConfig.SQLALCHEMY_ECHO,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=3600    # 1시간마다 연결 재생성
)

# 세션 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 (모델 정의 시 사용)
Base = declarative_base()

def get_db_session():
    """데이터베이스 세션 가져오기"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """데이터베이스 테이블 초기화"""
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블이 초기화되었습니다.")

if __name__ == "__main__":
    print("🔧 데이터베이스 설정 파일입니다.")
    print(f"📍 연결 정보: {DatabaseConfig.SQLALCHEMY_DATABASE_URI}")