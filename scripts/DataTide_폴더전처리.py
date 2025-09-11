import os
import re
import pandas as pd
import pdfplumber

def find_target_value(header, row, target_month_header=None):
    """
    테이블의 헤더와 데이터 행을 기반으로 목표 값을 찾습니다.
    연간 보고서의 경우 target_month_header를 사용하고, 월간 보고서의 경우 우선순위에 따라 값을 찾습니다.
    """
    # 연간 보고서 처리: 특정 월의 데이터를 추출
    if target_month_header:
        try:
            # '1월', '2월' 등 월 헤더의 인덱스를 찾음
            month_col_index = header.index(target_month_header)
            raw_value = row[month_col_index]
        except (ValueError, IndexError):
            return None
    # 월간 보고서 처리: '평균' > '최대' > '최소' 순서로 값을 찾음
    else:
        priority_cols = ['평균', '최대', '최소']
        raw_value = None
        for col_name in priority_cols:
            try:
                col_index = header.index(col_name)
                # 해당 열에 값이 있으면 추출 후 반복 중단
                if row[col_index] is not None:
                    raw_value = row[col_index]
                    break
            except (ValueError, IndexError):
                continue
    
    # 추출된 값(raw_value)을 정리하여 숫자(float)로 변환
    if raw_value:
        # 괄호, 공백 등 불필요한 문자를 제거
        cleaned_value = re.sub(r'[()\s]', '', str(raw_value))
        if cleaned_value:
            try:
                return float(cleaned_value)
            except ValueError:
                return None
    return None

def parse_reports(root_path):
    """
    지정된 경로의 모든 PDF 보고서를 파싱하여 데이터를 추출합니다.
    """
    all_records = []
    print(f"'{root_path}' 폴더에서 데이터 추출을 시작합니다.")

    # 1. 폴더 구조 탐색
    for location in os.listdir(root_path):
        location_path = os.path.join(root_path, location)
        if not os.path.isdir(location_path):
            continue

        for year_folder in os.listdir(location_path):
            year_path = os.path.join(location_path, year_folder)
            if not os.path.isdir(year_path) or '월간보고서' not in year_folder:
                continue
            
            year = year_folder.split('_')[0]

            for data_type in os.listdir(year_path):
                data_type_path = os.path.join(year_path, data_type)
                if not os.path.isdir(data_type_path):
                    continue

                pdf_files = [f for f in os.listdir(data_type_path) if f.lower().endswith('.pdf')]
                
                # 연간 보고서 경로를 미리 찾아둠
                annual_report_path = next((os.path.join(data_type_path, f) for f in pdf_files if '년간보고서' in f), None)

                # 2. 월별 데이터 추출 (1월 ~ 12월)
                for month in range(1, 13):
                    month_str = f"{month:02d}"
                    extracted_value = None
                    
                    # 3. 우선순위 적용: 월간 보고서 먼저 확인
                    monthly_report_path = next((os.path.join(data_type_path, f) for f in pdf_files if f"_{year}_{month_str}_" in f and '월간보고서' in f), None)

                    if monthly_report_path:
                        try:
                            with pdfplumber.open(monthly_report_path) as pdf:
                                for page in pdf.pages:
                                    for table in page.extract_tables():
                                        header = [str(h).strip() for h in table[0]]
                                        total_row = next((r for r in table if r and 'TOTAL' in str(r[0])), None)
                                        if total_row:
                                            extracted_value = find_target_value(header, total_row)
                                            if extracted_value is not None: break
                                    if extracted_value is not None: break
                        except Exception as e:
                            print(f"월간 보고서 오류 ({monthly_report_path}): {e}")

                    # 4. 월간 보고서 값이 없으면 연간 보고서에서 추출
                    if extracted_value is None and annual_report_path:
                        try:
                            with pdfplumber.open(annual_report_path) as pdf:
                                target_month_header = f"{month}월"
                                for page in pdf.pages:
                                    for table in page.extract_tables():
                                        # '월'이 포함된 행을 찾아 헤더로 지정
                                        header = next(( [str(c).replace('\n', '') for c in r] for r in table if any('월' in str(c) for c in r) ), None)
                                        total_row = next((r for r in table if r and 'TOTAL' in str(r[0])), None)
                                        if header and total_row:
                                            extracted_value = find_target_value(header, total_row, target_month_header)
                                            if extracted_value is not None: break
                                    if extracted_value is not None: break
                        except Exception as e:
                            print(f"연간 보고서 오류 ({annual_report_path}): {e}")
                    
                    # 5. 최종 데이터를 리스트에 추가
                    if extracted_value is not None:
                        record = {
                            '날짜': f"{year}-{month_str}-01",
                            '지역': location,
                            '종류': data_type,
                            '평균': extracted_value
                        }
                        all_records.append(record)
                        print(f"추출 성공: {record}")

    return all_records

# --- 메인 코드 실행 ---
if __name__ == "__main__":
    # 'sea_weather' 폴더가 코드 파일과 같은 위치에 있다고 가정
    ROOT_DIRECTORY = 'sea_weather'
    
    if os.path.exists(ROOT_DIRECTORY):
        # 함수를 실행하여 데이터 추출
        final_data = parse_reports(ROOT_DIRECTORY)

        if final_data:
            # 추출된 데이터를 DataFrame으로 변환
            df = pd.DataFrame(final_data)
            
            # CSV 파일로 저장 (엑셀에서 한글이 깨지지 않도록 utf-8-sig 인코딩 사용)
            output_filename = '해양관측_데이터_통합.csv'
            df.to_csv(output_filename, index=False, encoding='utf-8-sig')
            
            print(f"\n✅ 모든 데이터 추출이 완료되었습니다. '{output_filename}' 파일로 저장되었습니다.")
            print("\n--- 미리보기 ---")
            print(df.head())
        else:
            print("\n⚠️ 추출된 데이터가 없습니다. 폴더 구조나 파일 내용을 확인해주세요.")
    else:
        print(f"\n❌ 오류: '{ROOT_DIRECTORY}' 폴더를 찾을 수 없습니다. 코드 파일과 같은 위치에 폴더가 있는지 확인해주세요.")