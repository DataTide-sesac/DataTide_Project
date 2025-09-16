from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import DB_URL  # 데이터베이스 URL을 별도 config에서 관리

engine = create_engine(DB_URL, pool_pre_ping=True)  # 커넥션 풀 관리 및 유휴 커넥션 검사

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# DB 세션 제공용 Dependency (FastAPI/비슷한 구조에서 활용 가능)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
