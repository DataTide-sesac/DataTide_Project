import os

# 확인할 기본 폴더 경로
root_dir = 'sea_weather'
pdf_found = False

print(f"'{root_dir}' 폴더에서 파일 탐색을 시작합니다...")

# 1. sea_weather 폴더가 바탕화면에 있는지 확인
if not os.path.isdir(root_dir):
    print(f"오류: '{root_dir}' 폴더를 현재 위치(바탕화면)에서 찾을 수 없습니다.")
    print("스크립트와 같은 위치에 폴더가 있는지 확인해주세요.")
else:
    # 2. 폴더 안을 탐색하며 .pdf 파일이 있는지 확인
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.lower().endswith('.pdf'):
                print(f"  -> PDF 파일 찾음: {os.path.join(dirpath, f)}")
                pdf_found = True

    print("-" * 20)
    if pdf_found:
        print("탐색 완료: PDF 파일을 성공적으로 찾았습니다.")
        print("경로에는 문제가 없습니다. 원본 스크립트의 다른 부분을 확인해야 합니다.")
    else:
        print("탐색 완료: 하지만 'sea_weather' 폴더 내에서 PDF 파일을 찾지 못했습니다.")
        print("폴더 내에 '2015_월간보고서'와 같은 하위 폴더와 PDF 파일이 제대로 들어있는지 확인해주세요.")