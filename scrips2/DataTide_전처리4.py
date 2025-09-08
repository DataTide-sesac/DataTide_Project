import tabula
import pandas as pd

# PDF 파일 경로
pdf_path = '대천해수욕장_유속_년간보고서.pdf'

try:
    # stream=True 옵션으로 PDF의 표를 읽어옵니다.
    tables = tabula.read_pdf(pdf_path, pages='all', stream=True, pandas_options={'header': 0})

    # tabula가 페이지 전체를 하나의 큰 표로 읽어오므로, 첫 번째 표를 선택합니다.
    if tables:
        main_df = tables[0]
        
        # 표의 가장 마지막 3개 행(최대, 평균, 최소)을 선택합니다.
        result_df = main_df.tail(3).copy()

        # --- 데이터 정리 ---
        # 1. 필요 없는 '일자', '구분' 열을 삭제합니다.
        result_df = result_df.drop(columns=['일자', '구분'])
        
        # 2. 행의 인덱스를 정확한 이름으로 직접 설정합니다.
        result_df.index = ['최대', '평균', '최소']
        
        # 3. 데이터에 맞게 열 이름을 '1월'부터 '12월'까지로 다시 설정합니다.
        months = [f'{i}월' for i in range(1, 13)]
        result_df.columns = months

        print("✅ 성공! 최종적으로 'TOTAL' 데이터를 완벽하게 추출하고 정리했습니다.")
        print(result_df)

    else:
        print("❌ PDF에서 표를 찾지 못했습니다.")

except FileNotFoundError:
    print(f"❌ '{pdf_path}' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")