import os
import re
import pandas as pd
import tabula
from pathlib import Path
from tqdm import tqdm

# --- 1. 월간 보고서 처리 함수 ---
def process_monthly_report(pdf_path):
    """월간 보고서 PDF에서 일별 최대, 평균, 최소 데이터를 추출합니다."""
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
        # 마지막 3개 열(최대, 평균, 최소)과 첫번째 열(일) 선택
        df = df.iloc[:, [0, -3, -2, -1]]
        df.columns = ['일', '최대', '평균', '최소']

        # 'TOTAL' 행 제거 및 숫자형 데이터 변환
        df = df[df['일'] != 'TOTAL']
        df = df.dropna().astype({'일': int, '최대': float, '평균': float, '최소': float})

        # 날짜(date) 열 생성
        df['date'] = pd.to_datetime(df.apply(lambda row: f"{year}-{month}-{int(row['일']):02d}", axis=1))
        
        # 최종 데이터프레임 정리
        return df[['date', '최대', '평균', '최소']].set_index('date')

    except Exception as e:
        print(f"⚠️ 월간 보고서 처리 오류 '{pdf_path.name}': {e}")
        return None

# --- 2. 연간 보고서 처리 함수 ---
def process_annual_report(pdf_path):
    """연간 보고서 PDF에서 월별 TOTAL 최대, 평균, 최소 데이터를 추출합니다."""
    try:
        # 파일명 또는 경로에서 연도 정보 추출 (e.g., 2015_월간보고서 폴더)
        match = re.search(r'(\d{4})', str(pdf_path))
        if not match:
            return None
        year = match.group(1)

        # Tabula를 사용하여 PDF의 표 읽기
        tables = tabula.read_pdf(pdf_path, pages='all', stream=True, lattice=True)
        if not tables:
            return None
        
        df = tables[0]
        # 'TOTAL' 행만 선택 (가장 마지막 3개 행)
        total_df = df.tail(3).copy()
        
        # 데이터 정리
        total_df = total_df.drop(total_df.columns[[0, 1]], axis=1) # '일자', '구분' 열 삭제
        total_df.index = ['최대', '평균', '최소']
        total_df.columns = [f'{i}월' for i in range(1, 13)]
        
        # 데이터 형태 변환 (행과 열 전환)
        result_df = total_df.transpose()
        result_df = result_df.reset_index().rename(columns={'index': '월'})
        
        # 날짜(date) 열 생성 (매월 1일 기준으로)
        result_df['date'] = pd.to_datetime(result_df['월'].apply(lambda m: f"{year}-{m.replace('월', '')}-01"))
        
        # 숫자형으로 변환
        result_df[['최대', '평균', '최소']] = result_df[['최대', '평균', '최소']].astype(float)

        return result_df[['date', '최대', '평균', '최소']].set_index('date')

    except Exception as e:
        print(f"⚠️ 연간 보고서 처리 오류 '{pdf_path.name}': {e}")
        return None

# --- 3. 메인 실행 로직 ---
def main():
    """지정된 폴더 내의 모든 해양 데이터 PDF를 처리하여 CSV로 저장합니다."""
    
    # PDF 파일이 있는 최상위 폴더 경로를 지정하세요.
    root_directory = Path('./sea_weather') # 현재 폴더에 sea_weather가 있다고 가정
    
    # 처리된 데이터를 저장할 리스트
    all_data = []

    # 모든 PDF 파일 목록 가져오기
    pdf_files = list(root_directory.rglob('*.pdf'))
    
    # tqdm을 사용하여 진행 상황 표시
    for pdf_path in tqdm(pdf_files, desc="PDF 처리 중"):
        filename = pdf_path.name
        
        if '월간보고서' in filename:
            processed_data = process_monthly_report(pdf_path)
            if processed_data is not None:
                all_data.append(processed_data)
        elif '년간보고서' in filename:
            processed_data = process_annual_report(pdf_path)
            if processed_data is not None:
                all_data.append(processed_data)

    if not all_data:
        print("❌ 처리할 PDF 파일을 찾지 못했거나 데이터를 추출하지 못했습니다.")
        return

    # 모든 데이터 합치기
    final_df = pd.concat(all_data)
    
    # 날짜 순으로 정렬하고 중복 데이터 제거
    final_df = final_df.sort_index()
    final_df = final_df[~final_df.index.duplicated(keep='first')]

    # CSV 파일로 저장
    output_path = 'sea_data_combined.csv'
    final_df.to_csv(output_path)

    print(f"\n✅ 성공! 모든 데이터가 '{output_path}' 파일에 저장되었습니다.")
    print("--- 최종 데이터 샘플 ---")
    print(final_df.head())
    print("...")
    print(final_df.tail())


if __name__ == '__main__':
    main()