# Dockerfile

# 1. 베이스 이미지 선택 (파이썬 3.11 슬림 버전)
FROM python:3.11-slim

# 2. 작업 디렉토리 설정 (컨테이너 내부의 폴더)
WORKDIR /app

# 3. 라이브러리 목록을 먼저 복사하고 설치합니다.
# (파일이 변경되지 않으면 캐시를 사용해 빌드 속도가 빨라집니다.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 현재 폴더의 모든 파일을 작업 디렉토리로 복사합니다.
COPY . .

# 5. 외부에서 접속할 수 있도록 컨테이너의 8000번 포트를 개방합니다.
EXPOSE 8000

# 6. 컨테이너가 시작될 때 실행할 기본 명령어를 지정합니다.
# --host 0.0.0.0 옵션은 외부 접속을 허용하기 위해 필수입니다.
# 위 CMD 라인을 주석 처리하고 아래 라인으로 대체합니다.
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]