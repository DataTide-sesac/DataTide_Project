import os
import tabula
import pandas as pd

def process_pdf_to_csv(pdf_path, output_dir):
    """
    단일 PDF 파일을 읽어 표를 추출하고, 지정된 경로에 CSV 파일로 저장합니다.
    """
    # 출력될 CSV 파일의 전체 경로를 생성합니다. (파일 확장자 변경)
    file_name = os.path.basename(pdf_path)
    csv_file_name = os.path.splitext(file_name)[0] + '.csv'
    csv_path = os.path.join(output_dir, csv_file_name)

    # 이미 처리된 파일은 건너뜁니다.
    if os.path.exists(csv_path):
        print(f"이미 변환된 파일: {csv_file_name}")
        return

    print(f"처리 중: {file_name} ...")
    
    try:
        # PDF에서 표를 추출합니다. stream=True 옵션은 보고서 형식에 적합합니다.
        tables = tabula.read_pdf(pdf_path, stream=True, pages='all')
        
        if not tables:
            print(f"경고: {file_name}에서 표를 찾지 못했습니다.")
            return

        # 일반적으로 월간보고서의 주 내용은 첫 번째 표에 있습니다.
        main_table_df = tables[0]

        # 추출된 데이터프레임을 CSV로 저장합니다.
        main_table_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ 변환 완료: {csv_file_name}")

    except Exception as e:
        print(f"❌ 오류 발생 ({file_name}): {e}")


def main():
    """
    지정된 루트 디렉토리부터 모든 하위 디렉토리를 탐색하며 PDF 변환 작업을 수행합니다.
    """
    # --- 설정 부분 ---
    # 기준이 되는 상위 폴더 경로 (예: 'sea_weather/인천')
    root_directory = os.path.join('sea_weather', '인천')
    # 결과물이 저장될 상위 폴더 이름
    output_directory = os.path.join('sea_weather', '인천_CSV_결과')
    # -----------------

    print("="*50)
    print("PDF to CSV 변환 작업을 시작합니다.")
    print(f"대상 폴더: {os.path.abspath(root_directory)}")
    print(f"저장 폴더: {os.path.abspath(output_directory)}")
    print("="*50)

    # 루트 디렉토리가 존재하지 않으면 오류 메시지 출력 후 종료
    if not os.path.isdir(root_directory):
        print(f"오류: 대상 폴더 '{root_directory}'를 찾을 수 없습니다.")
        return

    # os.walk를 사용하여 모든 하위 폴더를 순회
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            # PDF 파일만 대상으로 처리
            if filename.lower().endswith('.pdf'):
                # 원본 파일의 전체 경로
                pdf_full_path = os.path.join(dirpath, filename)
                
                # 원본 폴더 구조를 유지하는 출력 폴더 경로 생성
                relative_path = os.path.relpath(dirpath, root_directory)
                output_path_for_csv = os.path.join(output_directory, relative_path)
                
                # 출력 폴더가 없으면 생성
                os.makedirs(output_path_for_csv, exist_ok=True)
                
                # PDF 처리 함수 호출
                process_pdf_to_csv(pdf_full_path, output_path_for_csv)

    print("\n모든 작업이 완료되었습니다.")


if __name__ == '__main__':
    main()