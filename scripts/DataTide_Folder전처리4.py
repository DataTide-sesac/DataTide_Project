import os
import re
import fitz  # PyMuPDF
import pandas as pd

def parse_monthly_report(pdf_path, region, report_type):
    """
    월간 보고서 PDF 파일에서 'TOTAL' 행의 데이터를 추출합니다.
    날짜 정보와 데이터 모두 PDF 파일의 내용에서 직접 읽어옵니다.
    """
    try:
        filename = os.path.basename(pdf_path)
        print(f"    - 월간 보고서 처리 시도: {filename}")

        with fitz.open(pdf_path) as doc:
            text = "".join(page.get_text() for page in doc)

        # 1. PDF 내용에서 날짜 정보 추출
        date_match = re.search(r'(20\d{2})년\s*(\d{1,2})월', text)
        if not date_match:
            print(f"      [경고] PDF 내용에서 'YYYY년 MM월' 형식의 날짜를 찾을 수 없습니다({filename}). 건너뜁니다.")
            return None
        
        year, month = date_match.group(1), date_match.group(2).zfill(2)

        # 2. 'TOTAL' 행 데이터 추출 (안정성 강화)
        lines = text.split('\n')
        total_line = None
        for line in lines:
            if line.strip().upper().startswith('TOTAL'):
                total_line = line
                break
        
        if not total_line:
            print(f"      [경고] 'TOTAL' 키워드를 포함한 행을 찾을 수 없습니다.")
            return None

        values = re.findall(r'-?[\d\.:]+', total_line)
        values = [val.replace(':', '.') for val in values]
        values = [val for val in values if re.match(r'^-?\d+(\.\d+)?$', val)]

        if len(values) >= 3:
            # PDF의 TOTAL 행은 보통 '최대, 평균, 최소' 순서로 값을 가집니다.
            max_val, avg_val, min_val = values[0], values[1], values[2]
            print(f"      [성공] 데이터 추출: 최대={max_val}, 평균={avg_val}, 최소={min_val}")
            return {
                "날짜": f"{year}-{month}",
                "지역": region,
                "종류": report_type,
                "최대": float(max_val),
                "평균": float(avg_val),
                "최소": float(min_val),
            }
        else:
            print(f"      [경고] 'TOTAL' 행에서 유효한 숫자 그룹(3개)을 찾지 못했습니다. 찾은 값: {values}")
            return None

    except Exception as e:
        print(f"    [오류] 월간 보고서 처리 중 예외 발생 ({filename}): {e}")
    return None

def parse_annual_report(pdf_path, region, fallback_year, report_type):
    """
    년간 보고서 PDF 파일에서 월별 최대값 데이터를 추출합니다.
    """
    monthly_data = []
    try:
        filename = os.path.basename(pdf_path)
        print(f"    - 년간 보고서 처리 시도: {filename} (기준 연도: {fallback_year})")

        with fitz.open(pdf_path) as doc:
            text = "".join(page.get_text() for page in doc)
        
        year_match = re.search(r'(20\d{2})\s*실시간', text)
        year = year_match.group(1) if year_match else fallback_year

        lines = text.split('\n')
        total_line = None
        for line in lines:
            if line.strip().upper().startswith('TOTAL'):
                total_line = line
                break

        if not total_line:
            print(f"      [경고] 'TOTAL' 키워드를 포함한 행을 찾을 수 없습니다.")
            return []

        values = re.findall(r'-?[\d\.:]+', total_line)
        values = [val.replace(':', '.') for val in values]
        values = [val for val in values if re.match(r'^-?\d+(\.\d+)?$', val)]
            
        if len(values) >= 12:
            print(f"      [성공] 12개월 최대값 데이터 추출.")
            for i, max_val in enumerate(values[:12]):
                month = str(i + 1).zfill(2)
                monthly_data.append({
                    "날짜": f"{year}-{month}",
                    "지역": region,
                    "종류": report_type,
                    "최대": float(max_val),
                    "평균": None,
                    "최소": None,
                })
        else:
            print(f"      [경고] 'TOTAL' 행에서 12개의 월별 데이터를 찾지 못했습니다. 추출된 값: {values}")

    except Exception as e:
        print(f"    [오류] 년간 보고서 처리 중 오류 발생 ({filename}): {e}")
    return monthly_data

def process_sea_weather_data(root_dir='sea_weather', region='인천'):
    """
    지정된 경로의 해양 기상 데이터를 탐색하고 처리하여 CSV 파일로 저장합니다.
    """
    region_path = os.path.join(root_dir, region)
    if not os.path.exists(region_path):
        print(f"오류: '{region_path}' 경로를 찾을 수 없습니다.")
        return

    all_data = []
    processed_months = set()

    print("1단계: 월간 보고서 데이터를 처리합니다...")
    for year_folder in sorted(os.listdir(region_path)):
        year_path = os.path.join(region_path, year_folder)
        if os.path.isdir(year_path) and re.search(r'^\d{4}', year_folder):
            print(f"\n--- 연도 폴더 '{year_folder}' 탐색 시작 ---")
            for type_folder in sorted(os.listdir(year_path)):
                type_path = os.path.join(year_path, type_folder)
                if os.path.isdir(type_path):
                    for filename in sorted(os.listdir(type_path)):
                        if '월간보고서' in filename and filename.endswith('.pdf'):
                            pdf_path = os.path.join(type_path, filename)
                            data = parse_monthly_report(pdf_path, region, type_folder)
                            if data:
                                all_data.append(data)
                                processed_months.add((data['날짜'], data['종류']))
    
    print("\n2단계: 년간 보고서에서 누락된 데이터를 보충합니다...")
    for year_folder in sorted(os.listdir(region_path)):
        year_path = os.path.join(region_path, year_folder)
        if os.path.isdir(year_path):
            year_match = re.search(r'^\d{4}', year_folder)
            if not year_match: continue
            
            year = year_match.group(0)
            print(f"\n--- 연도 폴더 '{year_folder}' (연도: {year}) 년간 보고서 탐색 ---")
            for type_folder in sorted(os.listdir(year_path)):
                type_path = os.path.join(year_path, type_folder)
                if os.path.isdir(type_path):
                    for filename in sorted(os.listdir(type_path)):
                        if '년간보고서' in filename and filename.endswith('.pdf'):
                            pdf_path = os.path.join(type_path, filename)
                            annual_datas = parse_annual_report(pdf_path, region, year, type_folder)
                            for data in annual_datas:
                                if (data['날짜'], data['종류']) not in processed_months:
                                    all_data.append(data)

    if not all_data:
        print("\n처리된 데이터가 없습니다. 파일 경로와 내용을 다시 확인해주세요.")
        return

    print("\n3단계: 데이터를 CSV 파일로 변환합니다...")
    df = pd.DataFrame(all_data)
    df = df.sort_values(by=['날짜', '지역', '종류']).reset_index(drop=True)
    df = df[['날짜', '지역', '종류', '최대', '평균', '최소']]
    output_filename = f'{region}_해양관측_통합보고서.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"\n✅ 완료! 모든 데이터가 '{output_filename}' 파일로 저장되었습니다.")
    print(f"총 {len(df)}개의 데이터 행이 처리되었습니다.")

if __name__ == '__main__':
    process_sea_weather_data()

