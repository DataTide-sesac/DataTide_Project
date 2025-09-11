# 1. 가장 깨끗하고 공식적인 Python 3.11 이미지를 기반으로 시작합니다.
FROM python:3.11-slim

# 2. 작업 공간을 설정합니다.
WORKDIR /app

# 3. requirements.txt 파일을 먼저 복사합니다.
COPY requirements.txt .

# 4. PyTorch CPU 버전을 먼저 명시적으로 설치합니다.
#    이것이 빌드 시간의 대부분을 차지하지만, 가장 확실한 방법입니다.
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 5. 나머지 라이브러리들을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 6. 프로젝트의 모든 파일을 복사합니다.
COPY . .

# 7. FastAPI 앱을 실행합니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]