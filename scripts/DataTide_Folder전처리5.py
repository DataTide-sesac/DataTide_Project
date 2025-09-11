import os
import re
import pandas as pd
import tabula # PDF table reader

def process_pdf(file_path, report_type):
    """
    PDF 파일에서 해양 기상 데이터를 추출합니다. 보고서 유형에 따라 다른 로직을 사용합니다.
    - 'monthly': 일별 데이터 테이블을 읽어 월별 통계를 계산합니다. (로직 대폭 개선)
    - 'yearly': 요약 행에서 최대값을 추출합니다.
    """
    try:
        if report_type == 'monthly':
            # 월간 보고서를 위한 개선된 처리 로직
            # header=None으로 우선 읽어온 후, 직접 헤더를 찾습니다.
            tables = tabula.read_pdf(file_path, pages=1, multiple_tables=True, pandas_options={'header': None}, lattice=True)
            
            if not tables:
                print(f"Warning: 월간 보고서에서 테이블을 찾을 수 없습니다: {file_path}")
                return None

            data_df = None
            required_cols = ['최대', '평균', '최소']
            
            for df in tables:
                if df.empty:
                    continue
                
                # '일', '최대', '평균', '최소' 문자열이 포함된 행을 찾아 헤더로 설정
                header_row_index = -1
                for i, row in df.iterrows():
                    # NaN 값을 제외하고 문자열로 합쳐서 검색
                    row_str = ' '.join(str(x) for x in row if pd.notna(x))
                    if '일' in row_str and '최대' in row_str and '평균' in row_str and '최소' in row_str:
                        header_row_index = i
                        break
                
                if header_row_index != -1:
                    new_header = df.iloc[header_row_index]
                    # 헤더 행 바로 다음부터 데이터로 사용
                    temp_df = df[header_row_index + 1:].copy()
                    temp_df.columns = [str(col).strip().replace('\r', ' ').replace('\n', ' ') for col in new_header]
                    
                    # 필요한 모든 열이 있는지 확인
                    if all(col in temp_df.columns for col in required_cols):
                        data_df = temp_df[required_cols].copy()
                        break # 올바른 테이블을 찾았으므로 루프 종료
            
            if data_df is None:
                print(f"Warning: 유효한 데이터 테이블('최대', '평균', '최소' 열 포함)을 찾을 수 없습니다: {file_path}")
                return None
            
            # 데이터 정제 및 숫자 변환
            for col in required_cols:
                # 각 셀에서 첫 번째로 발견되는 숫자만 정규표현식으로 추출
                data_df[col] = data_df[col].apply(lambda s: re.search(r'-?\d+\.?\d*', str(s)).group(0) if re.search(r'-?\d+\.?\d*', str(s)) else None)
                data_df[col] = pd.to_numeric(data_df[col], errors='coerce')
            
            data_df.dropna(inplace=True)

            if data_df.empty:
                print(f"Warning: 정제 후 유효한 숫자 데이터가 없습니다: {file_path}")
                return None
                
            # 월별 통계 계산
            monthly_max = data_df['최대'].max()
            monthly_avg = data_df['평균'].mean()
            monthly_min = data_df['최소'].min()

            return {
                '최대': f"{monthly_max:.2f}",
                '평균': f"{monthly_avg:.2f}",
                '최소': f"{monthly_min:.2f}"
            }

        elif report_type == 'yearly':
            # 연간 보고서는 기존 로직 유지
            tables = tabula.read_pdf(file_path, pages=1, multiple_tables=True, pandas_options={'header': None}, lattice=True)
            if not tables:
                print(f"Warning: 연간 보고서에서 테이블을 찾을 수 없습니다: {file_path}")
                return None

            keywords = ['Total', 'TOTAL', '합계', '총계', '평균', '최대']
            
            for df in tables:
                if df.empty: continue
                df_str = df.astype(str)
                
                for keyword in keywords:
                    summary_rows = df_str[df_str.apply(lambda row: row.str.contains(keyword, case=False, na=False).any(), axis=1)]
                    
                    if not summary_rows.empty:
                        values = summary_rows.iloc[0].tolist()
                        cleaned_values = []
                        for v in values:
                            found_numbers = re.findall(r'-?\d+\.?\d*', str(v))
                            cleaned_values.extend(found_numbers)
                        
                        if cleaned_values:
                            return {'최대': cleaned_values[0], '평균': '', '최소': ''}

            print(f"Warning: 연간 보고서의 요약 행을 찾을 수 없습니다: {file_path}")
            return None

    except Exception as e:
        print(f"파일 처리 오류 {file_path}: {e}")
        return None

def create_sea_weather_report(root_dir='sea_weather'):
    """
    디렉토리를 탐색하고 PDF 파일을 처리하여 통합된 CSV 보고서를 생성합니다.
    """
    all_data = []
    
    if not os.path.isdir(root_dir):
        print(f"오류: 루트 디렉토리 '{root_dir}'를 찾을 수 없습니다.")
        return

    for region in os.listdir(root_dir):
        region_path = os.path.join(root_dir, region)
        if not os.path.isdir(region_path): continue

        for year_folder in os.listdir(region_path):
            year_path = os.path.join(region_path, year_folder)
            if not os.path.isdir(year_path): continue
            
            year_match = re.search(r'(\d{4})', year_folder)
            if not year_match: continue
            year = year_match.group(1)

            for data_type in os.listdir(year_path):
                data_type_path = os.path.join(year_path, data_type)
                if not os.path.isdir(data_type_path): continue
                
                files_in_dir = os.listdir(data_type_path)
                monthly_files = [f for f in files_in_dir if '월간' in f and f.lower().endswith('.pdf')]
                yearly_files = [f for f in files_in_dir if '년간' in f and f.lower().endswith('.pdf')]

                if monthly_files:
                    files_to_process = monthly_files
                    report_type = 'monthly'
                elif yearly_files:
                    files_to_process = yearly_files
                    report_type = 'yearly'
                else:
                    continue

                for filename in files_to_process:
                    file_path = os.path.join(data_type_path, filename)
                    
                    month = '01' # 연간 보고서 기본값
                    if report_type == 'monthly':
                        month_match = re.search(r'(\d{4})_(\d{2})', filename)
                        if month_match:
                            month = month_match.group(2)
                        else:
                            print(f"Warning: 파일명에서 월 정보를 추출할 수 없습니다: '{filename}'. 건너뜁니다.")
                            continue
                    
                    data = process_pdf(file_path, report_type)

                    if data:
                        all_data.append({
                            '날짜': f"{year}-{month}-01",
                            '지역': region,
                            '종류': data_type,
                            '최대': data.get('최대'),
                            '평균': data.get('평균'),
                            '최소': data.get('최소')
                        })

    if not all_data:
        print("추출된 데이터가 없습니다. CSV 파일이 비어있을 수 있습니다.")
        df = pd.DataFrame(columns=['날짜', '지역', '종류', '최대', '평균', '최소'])
    else:
        df = pd.DataFrame(all_data)
        
    output_filename = 'sea_weather_processed_report.csv'
    try:
        df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"처리 완료. 데이터가 '{output_filename}' 파일에 저장되었습니다.")
    except Exception as e:
        print(f"CSV 파일 저장 오류: {e}")

if __name__ == '__main__':
    create_sea_weather_report()

