# check_location_data.py ㅣlocation 테이블의 local_pk와 local_name을 확인하는 코드
# pip install tabulate  # tabulate 패키지 설치 필요

import pymysql
from tabulate import tabulate
from datetime import date

DB_CONFIG = {
    'host': 'localhost',
    'user': 'team_dt',
    'password': 'dt_1234',
    'database': 'datatide_db',
    'charset': 'utf8'
}

def check_location_table():
    """location 테이블의 local_pk, local_name 조회"""
    print("🗺️  Location 테이블 데이터 확인")
    print("=" * 50)
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # 1. 테이블 구조 먼저 확인
            cursor.execute("DESCRIBE location")
            columns = cursor.fetchall()
            
            print("📋 테이블 구조:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NOT NULL' if col[2] == 'NO' else 'NULL'}")
            
            print("\n" + "="*50)
            
            # 2. local_pk, local_name 데이터 조회
            cursor.execute(
                "SELECT local_pk, local_name FROM location ORDER BY local_pk"
            )
            
            results = cursor.fetchall()
            
            if results:
                print(f"\n📊 Location 데이터 ({len(results)}개 지역):")
                print("-" * 30)
                
                # 테이블 형태로 출력
                headers = ["지역코드(PK)", "지역명"]
                table_data = []
                
                for row in results:
                    local_pk, local_name = row
                    table_data.append([local_pk, local_name])
                
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                # 추가 정보
                print(f"\n📈 통계:")
                print(f"  - 총 지역 수: {len(results)}개")
                print(f"  - PK 범위: {results[0][0]} ~ {results[-1][0]}")
                
                # 지역명 목록을 한 줄로
                location_names = [row[1] for row in results]
                print(f"  - 지역 목록: {', '.join(location_names)}")
                
            else:
                print("❌ location 테이블에 데이터가 없습니다.")
                
        connection.close()
        
    except Exception as e:
        print(f"❌ 데이터 조회 실패: {e}")

def check_location_with_other_data():
    """location과 다른 테이블의 연관 데이터 확인"""
    print("\n\n🔗 다른 테이블과의 연관성 확인")
    print("=" * 50)
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # ground_weather 테이블에서 location 사용 현황
            cursor.execute(
                "SELECT l.local_pk, l.local_name, COUNT(gw.local_pk) as weather_count " +
                "FROM location l " +
                "LEFT JOIN ground_weather gw ON l.local_pk = gw.local_pk " +
                "GROUP BY l.local_pk, l.local_name " +
                "ORDER BY l.local_pk"
            )
            
            weather_results = cursor.fetchall()
            
            if weather_results:
                print("\n🌤️  지상 기상 데이터 연관성:")
                headers = ["지역코드", "지역명", "기상데이터 개수"]
                table_data = []
                
                for row in weather_results:
                    table_data.append([row[0], row[1], f"{row[2]}개"])
                
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # sea_weather 테이블에서 location 사용 현황 (local_pk 컬럼이 있다면)
            cursor.execute("SHOW COLUMNS FROM sea_weather LIKE 'local_pk'")
            if cursor.fetchone():
                cursor.execute(
                    "SELECT l.local_pk, l.local_name, COUNT(sw.local_pk) as sea_weather_count " +
                    "FROM location l " +
                    "LEFT JOIN sea_weather sw ON l.local_pk = sw.local_pk " +
                    "GROUP BY l.local_pk, l.local_name " +
                    "ORDER BY l.local_pk"
                )
                
                sea_results = cursor.fetchall()
                
                if sea_results:
                    print("\n🌊 해양 기상 데이터 연관성:")
                    headers = ["지역코드", "지역명", "해양데이터 개수"]
                    table_data = []
                    
                    for row in sea_results:
                        table_data.append([row[0], row[1], f"{row[2]}개"])
                    
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
        connection.close()
        
    except Exception as e:
        print(f"❌ 연관 데이터 조회 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🗺️  DataTide Location 데이터 확인")
    print(f"📅 실행 시간: {date.today()}")
    
    # 기본 location 데이터 확인
    check_location_table()
    
    # 다른 테이블과의 연관성 확인
    check_location_with_other_data()
    
    print("\n✅ Location 데이터 확인이 완료되었습니다!")

if __name__ == "__main__":
    main()