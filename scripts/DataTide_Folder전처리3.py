import pandas as pd
import tabula
import re
from pathlib import Path
from tqdm import tqdm

def process_monthly_report_total(pdf_path):
    """월간 보고서 PDF에서 TOTAL 행의 최대, 평균, 최소 데이터만 추출합니다."""
    try:
        # 파일명에서 연도와 월 정보 추출 (e.g., 인천_수온_2015_01_월간보고서.pdf)
        match = re.search(r'_(\d{4})_(\d{2})_', pdf_path.name)
        if not match:
            return None
        year, month = match.groups()

        # Tabula를 사용하여 PDF의 표 읽기
        tables = tabula.read_pdf(pdf_path, pages='1', stream=True, pandas_options={'header': 0})
        if not tables:
            return None
        
        df = tables[0]

        # 첫 번째 열 이름이 '일' 또는 다른 이름일 수 있어, 이름으로 행을 찾지 않고 위치 기반으로 찾습니다.
        # 'TOTAL' 이라는 텍스트를 가진 행을 찾습니다.
        # df.iloc[:, 0].astype(str)를 통해 첫 열을 문자열로 바꿔서 검색합니다.
        total_row = df[df.iloc[:, 0].astype(str).str.contains('TOTAL', na=False)]
        
        if total_row.empty:
            print(f"⚠️ 'TOTAL' 행을 찾지 못함: {pdf_path.name}")
            return None

        # TOTAL 행에서 마지막 3개 값(최대, 평균, 최소)을 가져옵니다.
        summary_values = total_row.iloc[0, -3:].values
        
        # 해당 월의 1일 날짜를 생성합니다.
        report_date = pd.to_datetime(f"{year}-{month}-01")

        # 추출한 값으로 새로운 DataFrame을 만듭니다.
        result_df = pd.DataFrame([summary_values], 
                                 columns=['최대', '평균', '최소'], 
                                 index=[report_date])
        
        # 데이터 타입을 숫자(float)로 변환합니다.
        result_df = result_df.astype(float)
        
        return result_df

    except Exception as e:
        print(f"⚠️ 처리 오류 '{pdf_path.name}': {e}")
        return None

def main():
    """지정된 폴더 내의 월간 보고서 PDF를 처리하여 월별 요약 CSV로 저장합니다."""
    
    # PDF 파일이 있는 최상위 폴더 경로
    root_directory = Path('./sea_weather')
    
    all_monthly_data = []

    # '월간보고서'가 포함된 PDF 파일 목록만 가져오기
    pdf_files = [p for p in root_directory.rglob('*.pdf') if '월간보고서' in p.name]
    
    if not pdf_files:
        print("❌ 처리할 월간 보고서 PDF 파일을 찾지 못했습니다.")
        return

    # tqdm을 사용하여 진행 상황 표시
    for pdf_path in tqdm(pdf_files, desc="월간 보고서 처리 중"):
        processed_data = process_monthly_report_total(pdf_path)
        if processed_data is not None:
            all_monthly_data.append(processed_data)

    if not all_monthly_data:
        print("❌ PDF에서 데이터를 추출하지 못했습니다.")
        return

    # 모든 월별 데이터 합치기
    final_df = pd.concat(all_monthly_data)
    
    # 날짜 순으로 정렬
    final_df.sort_index(inplace=True)
    final_df.index.name = 'date'

    # CSV 파일로 저장 (한글 깨짐 방지)
    output_path = 'sea_data_monthly_summary.csv'
    final_df.to_csv(output_path, encoding='utf-8-sig')

    print(f"\n✅ 성공! 모든 월별 요약 데이터가 '{output_path}' 파일에 저장되었습니다.")
    print("--- 최종 데이터 샘플 ---")
    print(final_df.head())

if __name__ == '__main__':
    main()