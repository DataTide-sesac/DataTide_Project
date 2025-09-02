import tabula
import pandas as pd

# PDF 파일 경로
pdf_path = '대천해수욕장_유속_년간보고서.pdf'

try:
    # PDF에서 모든 표를 읽어옵니다.
    tables = tabula.read_pdf(pdf_path, pages='all', lattice=True)

    if tables:
        print(f"✅ 총 {len(tables)}개의 표를 찾았습니다. 각 표의 내용을 출력합니다.\n")
        
        # 찾은 모든 표(DataFrame)를 순서대로 출력
        for i, df in enumerate(tables):
            print(f"----------- 표 {i+1} -----------")
            print(df)
            print("\n" + "="*30 + "\n") # 표 구분을 위한 줄
            
    else:
        print("❌ PDF에서 표를 전혀 찾지 못했습니다.")

except Exception as e:
    print(f"오류가 발생했습니다: {e}")