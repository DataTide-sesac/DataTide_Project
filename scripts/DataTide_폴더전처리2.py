def extract_data_from_pdf(pdf_path):
    """
    PDF 파일 경로를 입력받아 날짜, 지역, 평균값을 추출하는 함수 (최종 디버깅 버전)
    """
    print(f"\n--- Processing: {os.path.basename(pdf_path)} ---")
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        # 1. 지역(관측소명) 추출
        region_match = re.search(r"관측소명:\s*(\S+)", text)
        region = region_match.group(1).strip() if region_match else None
        print(f"  -> Region Found: {region}")

        # 2. 날짜(년/월) 추출
        date_match = re.search(r"(\d{4})년\s*(\d{2})월", text)
        if date_match:
            year, month = date_match.groups()
            date = f"{year}-{month}-01"
        else:
            date = None
        print(f"  -> Date Found: {date}")

        # 3. 'TOTAL' 행의 '평균' 값 추출
        average = None
        lines = text.split('\n')
        for line in lines:
            if line.strip().startswith("TOTAL"):
                # ↓↓↓↓↓↓↓↓↓↓ 'TOTAL' 행의 원본과 숫자 추출 결과를 출력하는 부분 ↓↓↓↓↓↓↓↓↓↓
                print(f"  -> Found TOTAL line text: '{line.strip()}'")
                numeric_values = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                print(f"  -> Numbers extracted from line: {numeric_values}")
                # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                if len(numeric_values) >= 3:
                    average = numeric_values[-2]
                break
        print(f"  -> Average Found: {average}")
        
        # 4. 최종 성공 여부 판단
        if date and region and average:
            print("  -> SUCCESS: All data extracted.")
            return date, region, average
        else:
            print("  -> FAILURE: Missing one or more data points. Skipping file.")
            return None, None, None
            
    except Exception as e:
        print(f"  -> CRITICAL ERROR: An exception occurred: {e}")
        return None, None, None