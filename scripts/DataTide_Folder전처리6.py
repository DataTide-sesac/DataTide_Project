import os
import re
import pandas as pd
import tabula  # PDF 테이블 라이브러리

def process_pdf(file_path, report_type):
    """
    PDF 파일에서 'TOTAL' 요약 행을 찾아 데이터를 추출합니다.
    - 월간 보고서: 메인 데이터 테이블을 먼저 찾은 후, 그 안의 'TOTAL' 행에서 데이터를 추출합니다.
    - 연간 보고서: 'TOTAL' 행의 12개 숫자(월별 최대값)를 반환합니다.
    """
    try:
        tables = tabula.read_pdf(file_path, pages=1, multiple_tables=True, pandas_options={'header': None}, lattice=True, silent=True)
        if not tables:
            print(f"  [경고] 보고서에서 테이블을 찾을 수 없습니다: {os.path.basename(file_path)}")
            return None

        if report_type == 'monthly':
            # 1. '일', '최대', '평균', '최소' 키워드로 정확한 데이터 테이블부터 찾기
            main_data_table = None
            header_keywords = ['일', '최대', '평균', '최소']
            
            for df in tables:
                if df.empty:
                    continue
                # 테이블 내에 헤더 키워드가 모두 있는지 확인
                table_text = ' '.join(df.astype(str).values.flatten())
                if all(keyword in table_text for keyword in header_keywords):
                    main_data_table = df
                    break # 정확한 테이블을 찾았으므로 중단
            
            if main_data_table is None:
                print(f"  [경고] 유효한 데이터 테이블(헤더 포함)을 찾을 수 없습니다: {os.path.basename(file_path)}")
                return None
            
            # 2. 찾은 테이블 안에서 'TOTAL' 행 검색
            df_str = main_data_table.astype(str)
            summary_rows = df_str[df_str.apply(lambda row: row.str.contains('TOTAL', case=False, na=False).any(), axis=1)]

            if not summary_rows.empty:
                total_row_values = summary_rows.iloc[0].tolist()
                all_numbers_in_row = [num for cell in total_row_values for num in re.findall(r'-?\d+\.?\d*', str(cell))]
                
                if len(all_numbers_in_row) >= 3:
                    # TOTAL 행의 마지막 3개 숫자를 최대, 평균, 최소 값으로 사용
                    max_val, avg_val, min_val = all_numbers_in_row[-3:]
                    print(f"  [성공] 월간 TOTAL 데이터 추출: {os.path.basename(file_path)}")
                    return {'최대': max_val, '평균': avg_val, '최소': min_val}
            
            print(f"  [경고] 확인된 테이블 내에서 'TOTAL' 요약 행을 찾을 수 없습니다: {os.path.basename(file_path)}")
            return None

        elif report_type == 'yearly':
            # 연간 보고서는 바로 'TOTAL' 행을 찾습니다.
            for df in tables:
                if df.empty: continue
                df_str = df.astype(str)
                summary_rows = df_str[df_str.apply(lambda row: row.str.contains('TOTAL', case=False, na=False).any(), axis=1)]
                
                if not summary_rows.empty:
                    total_row_values = summary_rows.iloc[0].tolist()
                    all_numbers_in_row = [num for cell in total_row_values for num in re.findall(r'-?\d+\.?\d*', str(cell))]
                    
                    if len(all_numbers_in_row) >= 12:
                        print(f"  [성공] 연간 데이터 추출: {os.path.basename(file_path)}")
                        return {'monthly_max_values': all_numbers_in_row[:12]}
            
            print(f"  [경고] 연간 보고서에서 'TOTAL' 요약 행을 찾을 수 없습니다: {os.path.basename(file_path)}")
            return None

    except Exception as e:
        print(f"  [오류] 파일 처리 중 예외 발생 {os.path.basename(file_path)}: {e}")
        return None

def create_sea_weather_report(root_dir='sea_weather'):
    """
    디렉토리를 탐색하고 PDF 파일을 처리하여 통합된 CSV 보고서를 생성합니다.
    """
    all_data = []
    processed_months = set() # (날짜, 지역, 종류) 형식으로 이미 처리된 월을 기록
    
    if not os.path.isdir(root_dir):
        print(f"오류: 루트 디렉토리 '{root_dir}'를 찾을 수 없습니다.")
        return

    print("1단계: 월간 보고서 데이터를 처리합니다...")
    for region in sorted(os.listdir(root_dir)):
        region_path = os.path.join(root_dir, region)
        if not os.path.isdir(region_path): continue

        for year_folder in sorted(os.listdir(region_path)):
            year_path = os.path.join(region_path, year_folder)
            if not os.path.isdir(year_path): continue
            
            for data_type in sorted(os.listdir(year_path)):
                data_type_path = os.path.join(year_path, data_type)
                if not os.path.isdir(data_type_path): continue
                
                monthly_files = [f for f in os.listdir(data_type_path) if '월간' in f and f.lower().endswith('.pdf')]
                
                for filename in monthly_files:
                    file_path = os.path.join(data_type_path, filename)
                    
                    match = re.search(r'(\d{4})[년_]?\s?_?(\d{1,2})[월]?', filename)
                    if not match:
                        print(f"  [경고] 파일명에서 날짜 정보를 찾을 수 없습니다: '{filename}'.")
                        continue
                    
                    year, month = match.group(1), match.group(2).zfill(2)
                    date_key = f"{year}-{month}"
                    
                    data = process_pdf(file_path, 'monthly')
                    
                    if data:
                        all_data.append({
                            '날짜': date_key, '지역': region, '종류': data_type,
                            '최대': data.get('최대'), '평균': data.get('평균'), '최소': data.get('최소')
                        })
                        processed_months.add((date_key, region, data_type))

    print("\n2단계: 년간 보고서에서 누락된 데이터를 보충합니다...")
    for region in sorted(os.listdir(root_dir)):
        region_path = os.path.join(root_dir, region)
        if not os.path.isdir(region_path): continue

        for year_folder in sorted(os.listdir(region_path)):
            year_path = os.path.join(region_path, year_folder)
            if not os.path.isdir(year_path): continue
            
            year_match = re.search(r'(\d{4})', year_folder)
            if not year_match: continue
            year = year_match.group(1)

            for data_type in sorted(os.listdir(year_path)):
                data_type_path = os.path.join(year_path, data_type)
                if not os.path.isdir(data_type_path): continue
                
                yearly_files = [f for f in os.listdir(data_type_path) if '년간' in f and f.lower().endswith('.pdf')]

                for filename in yearly_files:
                    file_path = os.path.join(data_type_path, filename)
                    data = process_pdf(file_path, 'yearly')
                    
                    if data and 'monthly_max_values' in data:
                        for i, max_val in enumerate(data['monthly_max_values']):
                            month = str(i + 1).zfill(2)
                            date_key = f"{year}-{month}"
                            
                            if (date_key, region, data_type) not in processed_months:
                                all_data.append({
                                    '날짜': date_key, '지역': region, '종류': data_type,
                                    '최대': max_val, '평균': None, '최소': None
                                })

    if not all_data:
        print("\n추출된 데이터가 없습니다. CSV 파일이 생성되지 않았습니다.")
        return
        
    print("\n3단계: 데이터를 CSV 파일로 변환합니다...")
    df = pd.DataFrame(all_data)
    df.sort_values(by=['날짜', '지역', '종류'], inplace=True)
    df = df[['날짜', '지역', '종류', '최대', '평균', '최소']]
    
    output_filename = 'sea_weather_processed_report.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"\n✅ 처리 완료! 총 {len(df)}개의 데이터가 '{output_filename}' 파일에 저장되었습니다.")

if __name__ == '__main__':
    create_sea_weather_report()

