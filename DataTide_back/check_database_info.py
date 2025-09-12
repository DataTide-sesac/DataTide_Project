# check_database_info.py ㅣMySQL 데이터베이스 상태를 점검하는 코드
# MySQL에서 datatide_db가 최신 데이터베이스인지 확인
import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'team_dt',
    'password': 'dt_1234',
    'charset': 'utf8'
}

def check_all_databases():
    """모든 데이터베이스 목록 확인"""
    print("=== 전체 데이터베이스 목록 ===")
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # 모든 데이터베이스 목록
            cursor.execute("""
                SELECT 
                    SCHEMA_NAME as database_name,
                    DEFAULT_CHARACTER_SET_NAME as charset,
                    DEFAULT_COLLATION_NAME as collation
                FROM information_schema.SCHEMATA 
                WHERE SCHEMA_NAME NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
                ORDER BY SCHEMA_NAME
            """)
            
            databases = cursor.fetchall()
            
            print(f"📊 총 {len(databases)}개의 사용자 데이터베이스가 있습니다:")
            for i, db in enumerate(databases, 1):
                print(f"{i}. 🗃️  {db[0]} (문자셋: {db[1]})")
                
        connection.close()
        return databases
        
    except Exception as e:
        print(f"❌ 데이터베이스 목록 조회 실패: {e}")
        return []

def check_datatide_db_info():
    """datatide_db 상세 정보 확인"""
    print("\n=== datatide_db 상세 정보 ===")
    
    try:
        # datatide_db에 직접 연결
        config_with_db = DB_CONFIG.copy()
        config_with_db['database'] = 'datatide_db'
        connection = pymysql.connect(**config_with_db)
        
        with connection.cursor() as cursor:
            # 현재 데이터베이스 확인
            cursor.execute("SELECT DATABASE(), NOW()")
            current_info = cursor.fetchone()
            print(f"📍 현재 연결된 DB: {current_info[0]}")
            print(f"🕐 현재 시간: {current_info[1]}")
            
            # 테이블 목록과 정보
            cursor.execute("""
                SELECT 
                    table_name,
                    create_time,
                    update_time,
                    table_rows,
                    ROUND(data_length/1024/1024, 2) as size_mb
                FROM information_schema.tables 
                WHERE table_schema = 'datatide_db'
                ORDER BY create_time DESC
            """)
            
            tables = cursor.fetchall()
            
            if tables:
                print(f"\n📋 테이블 목록 ({len(tables)}개):")
                for table in tables:
                    name, created, updated, rows, size = table
                    print(f"  🔹 {name}")
                    print(f"     생성: {created or '정보없음'}")
                    print(f"     수정: {updated or '정보없음'}")
                    print(f"     행수: {rows or 0}개")
                    print(f"     크기: {size or 0}MB")
                    print()
                    
                # 가장 최근 활동
                latest_activity = max([t[1] or datetime.min for t in tables if t[1]])
                if latest_activity != datetime.min:
                    print(f"🔥 가장 최근 테이블 생성: {latest_activity}")
                    
            else:
                print("📋 생성된 테이블이 없습니다. (새로 만든 데이터베이스)")
                
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ datatide_db 정보 조회 실패: {e}")
        return False

def check_database_activity():
    """데이터베이스 활동 기록 확인"""
    print("\n=== 데이터베이스 활동 기록 ===")
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # 현재 프로세스 목록
            cursor.execute("SHOW PROCESSLIST")
            processes = cursor.fetchall()
            
            # datatide_db 관련 프로세스 찾기
            datatide_processes = [p for p in processes if p[3] == 'datatide_db']
            
            print(f"🔄 현재 MySQL 연결 수: {len(processes)}개")
            print(f"🎯 datatide_db 연결 수: {len(datatide_processes)}개")
            
            if datatide_processes:
                print("\n📡 현재 datatide_db에 연결된 세션:")
                for proc in datatide_processes:
                    print(f"  - ID: {proc[0]}, 사용자: {proc[1]}, 상태: {proc[4]}")
                    
        connection.close()
        
    except Exception as e:
        print(f"❌ 활동 기록 조회 실패: {e}")

def main():
    print("🔍 MySQL 데이터베이스 최신 상태 확인을 시작합니다.")
    print("=" * 60)
    
    # 1. 전체 데이터베이스 목록
    databases = check_all_databases()
    
    # 2. datatide_db가 존재하는지 확인
    if any(db[0] == 'datatide_db' for db in databases):
        print("✅ datatide_db가 존재합니다.")
        
        # 3. datatide_db 상세 정보
        check_datatide_db_info()
        
        # 4. 활동 기록
        check_database_activity()
        
    else:
        print("❌ datatide_db가 존재하지 않습니다!")
        print("다음 명령어로 생성하세요:")
        print("CREATE DATABASE datatide_db DEFAULT CHARACTER SET utf8;")

if __name__ == "__main__":
    main()