import pymysql
import sys

# 데이터베이스 연결 정보
DB_CONFIG = {
    'host': 'localhost',
    'user': 'team_dt',
    'password': 'dt_1234',
    'database': 'datatide_db',
    'port': 3306,
    'charset': 'utf8'
}

def test_pymysql_connection():
    """PyMySQL을 사용한 직접 연결 테스트"""
    print("=== PyMySQL 직접 연결 테스트 ===")
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            charset=DB_CONFIG['charset']
        )
        
        with connection.cursor() as cursor:
            # 현재 데이터베이스 확인
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            
            # 서버 시간 확인
            cursor.execute("SELECT NOW()")
            server_time = cursor.fetchone()[0]
            
            # 테이블 목록 확인
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
        print(f"✅ 연결 성공!")
        print(f"📍 현재 데이터베이스: {current_db}")
        print(f"🕐 서버 시간: {server_time}")
        print(f"📋 테이블 개수: {len(tables)}개")
        
        if tables:
            print("📋 테이블 목록:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("📋 생성된 테이블이 없습니다.")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ PyMySQL 연결 실패: {e}")
        return False

def test_sqlalchemy_connection():
    """SQLAlchemy를 사용한 연결 테스트"""
    print("\n=== SQLAlchemy 연결 테스트 ===")
    try:
        # SQLAlchemy 연결 문자열
        DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8"
        
        print(f"🔗 연결 문자열: {DATABASE_URL}")
        
        # 엔진 생성
        engine = create_engine(DATABASE_URL, echo=True)
        
        # 연결 테스트
        with engine.connect() as connection:
            # 현재 데이터베이스 확인
            result = connection.execute(text("SELECT DATABASE(), NOW(), VERSION()"))
            db_info = result.fetchone()
            
            # 테이블 목록 확인
            result = connection.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            
        print(f"✅ SQLAlchemy 연결 성공!")
        print(f"📍 데이터베이스: {db_info[0]}")
        print(f"🕐 서버 시간: {db_info[1]}")
        print(f"🔧 MySQL 버전: {db_info[2]}")
        print(f"📋 테이블 개수: {len(tables)}개")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy 연결 실패: {e}")
        return False

def create_sample_table():
    """샘플 테이블 생성 테스트"""
    print("\n=== 샘플 테이블 생성 테스트 ===")
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # 테스트 테이블 생성
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS test_connection (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            """
            cursor.execute(create_table_sql)
            
            # 샘플 데이터 삽입
            insert_sql = "INSERT INTO test_connection (name) VALUES (%s)"
            cursor.execute(insert_sql, ('연결 테스트 성공',))
            
            # 데이터 조회
            cursor.execute("SELECT * FROM test_connection ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            
        connection.commit()
        connection.close()
        
        print(f"✅ 테이블 생성 및 데이터 삽입 성공!")
        print(f"📊 삽입된 데이터: ID={result[0]}, Name={result[1]}, Time={result[2]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 MySQL 데이터베이스 연결 테스트를 시작합니다.")
    print(f"🏠 호스트: {DB_CONFIG['host']}")
    print(f"👤 사용자: {DB_CONFIG['user']}")
    print(f"🗃️ 데이터베이스: {DB_CONFIG['database']}")
    print("=" * 50)
    
    # 필수 패키지 확인
    try:
        import pymysql
        import sqlalchemy
        print("📦 필요한 패키지가 설치되어 있습니다.")
    except ImportError as e:
        print(f"❌ 패키지 설치 필요: {e}")
        print("다음 명령어로 설치하세요:")
        print("pip install pymysql sqlalchemy")
        sys.exit(1)
    
    # 연결 테스트 실행
    pymysql_success = test_pymysql_connection()
    sqlalchemy_success = test_sqlalchemy_connection()
    
    if pymysql_success and sqlalchemy_success:
        table_success = create_sample_table()
        
        if table_success:
            print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
            print("✅ 이제 이 설정으로 프로젝트에서 데이터베이스를 사용할 수 있습니다.")
        else:
            print("\n⚠️ 연결은 성공했지만 테이블 생성에 문제가 있습니다.")
    else:
        print("\n❌ 데이터베이스 연결에 문제가 있습니다.")
        print("MySQL 서버가 실행 중인지, 사용자 권한이 올바른지 확인해 주세요.")

if __name__ == "__main__":
    main()