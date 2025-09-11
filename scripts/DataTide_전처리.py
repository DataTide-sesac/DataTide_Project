# 필요한 라이브러리 설치
#pip install tabula-py pandas

import tabula
import pandas as pd

# PDF 파일 경로를 지정합니다.
pdf_path = '대천해수욕장_유속_년간보고서.pdf'

try:
    # tabula로 PDF의 모든 페이지에서 표를 DataFrame 리스트로 읽어옵니다.
    # lattice=True 옵션은 표의 선을 기준으로 셀을 나누는 데 도움이 됩니다.
    tables = tabula.read_pdf(pdf_path, pages='all', lattice=True)

    # 추출된 모든 표 중에서 'TOTAL'을 포함하는 표를 찾습니다.
    total_df = None
    for df in tables:
        # 첫 번째 열에 'TOTAL'이라는 문자열이 포함되어 있는지 확인합니다.
        if 'TOTAL' in df.iloc[:, 0].astype(str).values:
            total_df = df
            break # 찾았으면 반복을 중단합니다.

    if total_df is not None:
        # 'TOTAL'이 포함된 행의 인덱스를 찾습니다.
        start_index = total_df[total_df.iloc[:, 0].str.contains('TOTAL', na=False)].index[0]
        
        # 'TOTAL' 데이터는 보통 최대, 평균, 최소 3개의 행으로 구성되므로 해당 부분만 선택합니다.
        result_df = total_df.iloc[start_index : start_index + 3].copy()

        # 보기 좋게 데이터를 정리합니다.
        # 1. 첫 번째 열(구분)을 인덱스로 설정
        result_df.set_index(result_df.columns[1], inplace=True)
        # 2. 불필요한 첫 번째, 두 번째 열 삭제
        result_df = result_df.drop(columns=[result_df.columns[0], result_df.columns[1]])
        # 3. 월(Month)을 컬럼명으로 설정
        months = [f'{i}월' for i in range(1, 13)]
        result_df.columns = months
        
        print("✅ 성공적으로 'TOTAL' 데이터를 추출했습니다.")
        print(result_df)

    else:
        print("❌ PDF에서 'TOTAL' 데이터를 포함하는 표를 찾지 못했습니다.")

except FileNotFoundError:
    print(f"❌ '{pdf_path}' 파일을 찾을 수 없습니다. 파일이 코드와 같은 폴더에 있는지 확인해주세요.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")