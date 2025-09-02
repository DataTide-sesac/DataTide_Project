import tabula
import pandas as pd

# PDF 파일 경로
pdf_path = '대천해수욕장_유속_년간보고서.pdf'

try:
    # stream=True 옵션을 사용하여 PDF의 모든 표를 읽어옵니다.
    # pandas_options={'header': None}은 첫 줄을 헤더로 인식하지 않도록 합니다.
    tables = tabula.read_pdf(pdf_path, pages='all', stream=True, pandas_options={'header': None})

    total_df_raw = None
    # 여러 표가 추출될 수 있으므로, 반복문을 통해 'TOTAL'이 포함된 표를 찾습니다.
    for df in tables:
        # 첫 번째 열(df[0])에 'TOTAL' 문자열이 포함된 행이 있는지 확인합니다.
        if df[0].astype(str).str.contains('TOTAL').any():
            total_df_raw = df
            break # 찾았으면 중단

    if total_df_raw is not None:
        # 'TOTAL'이 포함된 행의 인덱스를 찾습니다.
        start_index = total_df_raw[total_df_raw[0].astype(str).str.contains('TOTAL')].index[0]

        # 해당 위치부터 3개의 행(최대, 평균, 최소)을 선택합니다.
        result_df = total_df_raw.iloc[start_index : start_index + 3].copy()

        # --- 데이터 정리 ---
        # 1. '최대', '평균', '최소'가 있는 두 번째 열을 인덱스로 설정합니다.
        result_df.set_index(result_df.columns[1], inplace=True)
        # 2. 불필요해진 첫 번째 열('TOTAL' 열)을 삭제합니다.
        result_df = result_df.drop(columns=result_df.columns[0])
        # 3. 각 데이터 열에 '1월', '2월'... 이름을 붙여줍니다.
        months = [f'{i}월' for i in range(1, 13)]
        result_df.columns = months

        print("✅ 성공! 'TOTAL' 데이터를 정확하게 추출하고 정리했습니다.")
        print(result_df)

    else:
        print("❌ stream 옵션으로도 'TOTAL'을 포함한 표를 찾지 못했습니다.")

except FileNotFoundError:
    print(f"❌ '{pdf_path}' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")