# DataTide 프로젝트 개요

## 1. 프로젝트 소개
이 프로젝트는 **해양 수산물 유통 데이터**를 기반으로 **수요 예측 및 정보 검색**을 지원하는 통합 시스템입니다. `DataTide_back`은 FastAPI를 활용한 백엔드 API를 제공하며, `DataTide_front`는 React 기반의 사용자 인터페이스를 담당합니다. `DataTide_ai`는 예측 및 RAG(Retrieval Augmented Generation) 기능을 통해 데이터 기반의 인사이트를 제공합니다.

## 2. 주요 기능
- **수산물 유통 데이터 관리**: 품목(item), 소매(item_retail), 지상 날씨(ground_weather), 해상 날씨(sea_weather), 지역(location) 등 다양한 유통 관련 데이터의 CRUD(생성, 읽기, 업데이트, 삭제) 기능 제공.
- **수요 예측**: 과거 유통 데이터 및 날씨 데이터를 기반으로 특정 수산물의 미래 수요를 예측하는 AI 모델 연동. (`Predict_AI` 모듈 활용)
- **정보 검색 (RAG)**: RAG(Retrieval Augmented Generation) 기술을 활용하여 수산물 관련 질의에 대한 정확하고 풍부한 정보 제공. (`RAG_AI` 모듈 활용)
- **데이터 시각화**: 프론트엔드에서 예측 결과 및 통계 데이터를 직관적인 차트와 그래프로 시각화하여 제공.

## 3. 기술 스택
- **백엔드**: Python (FastAPI), SQLAlchemy (ORM), Alembic (DB 마이그레이션), Uvicorn (ASGI 서버)
- **프론트엔드**: React.js, Vite (빌드 도구), CSS Modules (또는 Tailwind CSS, Styled Components 등 사용 시 명시)
- **AI/ML**: Python (scikit-learn, pandas, numpy 등 데이터 분석 및 모델링 라이브러리), FAISS (RAG를 위한 벡터 저장소)
- **데이터베이스**: PostgreSQL (또는 MySQL, SQLite 등 실제 사용하는 DB 명시)

## 4. 개발 환경 설정 및 애플리케이션 실행 방법 (루트 폴더에서 실행)

### 4.1. 백엔드 설정 및 실행

1.  **가상 환경 활성화:**
    ```bash
    conda activate DataTide
    ```
2.  **필요한 패키지 설치 (처음 실행하는 경우 또는 변경사항이 있는 경우):**
    ```bash
    pip install -r DataTide_back/requirements.txt
    ```
3.  **데이터베이스 설정:**
    `DataTide_back/core/config.py` 파일에서 데이터베이스 연결 정보를 설정합니다.
4.  **데이터베이스 마이그레이션 (필요시):**
    ```bash
    alembic upgrade head
    ```
5.  **백엔드 서버 실행:**
    ```bash
    uvicorn DataTide_back.main:app --reload
    ```
    (서버는 기본적으로 `http://127.0.0.1:8000` 에서 실행됩니다.)

### 4.2. 프론트엔드 설정 및 실행

1.  **의존성 설치 (처음 실행하는 경우 또는 변경사항이 있는 경우):**
    ```bash
    npm install --prefix DataTide_front
    ```
2.  **프론트엔드 개발 서버 실행:**
    ```bash
    npm run dev --prefix DataTide_front
    ```
    (서버는 기본적으로 `http://localhost:5173` 에서 실행됩니다.)

**참고:** 백엔드 서버와 프론트엔드 서버는 각각 별도의 터미널 창에서 실행해야 합니다.

### 4.3. AI/ML 모델 사용 (선택 사항)
- **예측 모델**: `DataTide_ai/Predict_AI/compare.py` 스크립트를 통해 예측 모델을 학습하고 평가할 수 있습니다.
- **RAG 모델**: `DataTide_ai/RAG_AI/rag.py` 및 `rag_2.py` 스크립트를 통해 RAG 시스템을 구축하고 활용할 수 있습니다. `faiss_index` 디렉토리에는 FAISS 인덱스 파일이 저장됩니다.

## 5. 데이터베이스 구조 (ERD)
프로젝트의 데이터베이스 구조는 다음 위치에서 확인할 수 있습니다:
- `문서_N/이미지/00_ERD_1.JPG` ~ `00_ERD_4.JPG`
- `DataTide_back/00_ERD_3.JPG`

## 6. 기여 방법
프로젝트에 기여하고 싶으시다면, 다음 단계를 따르세요:
1.  이 저장소를 포크(Fork)합니다.
2.  새로운 브랜치를 생성합니다 (`git checkout -b feature/your-feature-name`).
3.  변경 사항을 커밋합니다 (`git commit -m 'Add some feature'`).
4.  원격 저장소에 푸시합니다 (`git push origin feature/your-feature-name`).
5.  풀 리퀘스트(Pull Request)를 생성합니다.

## 7. 라이선스
[프로젝트 라이선스 정보. 예: MIT License]

## 8. 변수명 매핑표 (CSV 컬럼명 → 프로젝트 변수명)
| 한글컬럼명 | DB/프로젝트 변수명 |
|---|---|
| 품목명 | item_name |
| 날짜 | month_date |
| 생산 | production |
| 수입 | inbound |
| 판매 | sales |
| 일시 | month_date |
| 평균기온 | temperature |
| 평균강수 | rain |
| 지역 | local_name |
| 수온 | temperature |
| 염분 | salinity |
| 유속 | wave_speed |
| 유의파고 | wave_height |
| 유의파주기 | wave_period |
| 풍속 | wind |
| 강수량 | rain |
| 적설량 | snow |

앞으로 유사한 Python 패키지 내의 스크립트를 실행하실 때는 다음 사항들을 참고해 주시기 바랍니다:

1. 모듈 실행 방식 사용
프로젝트 루트에서 python -m 패키지명.모듈명 형태로 실행
상대 import 문제를 자연스럽게 해결
2. 디렉토리 구조 유지
각 패키지 디렉토리에 __init__.py 파일 존재 확인
적절한 import 구조 유지
3. 실행 위치 주의
항상 프로젝트 루트에서 실행하여 일관성 유지

---

### `ImportError: attempted relative import beyond top-level package` 오류 해결

**문제:**
`DataTide_back` 폴더 내의 `create_tables.py`와 같이 상대 경로(`from .db.database import ...` 또는 `from ..core.config import ...`)를 사용하는 스크립트를 해당 스크립트가 위치한 폴더(`DataTide_back`)에서 `python create_tables.py`와 같이 직접 실행할 경우 발생합니다. 파이썬이 스크립트의 패키지 구조를 올바르게 인식하지 못해 상대 경로를 해석할 수 없기 때문입니다.

**해결책:**
해당 스크립트를 파이썬 패키지 내의 모듈로 실행해야 합니다. 이를 위해서는 스크립트가 속한 패키지의 **부모 디렉토리(프로젝트 루트)**에서 `python -m` 명령어를 사용합니다.

**예시:**
`C:\datatide_workspaceN\DataTide_back\create_tables.py` 스크립트를 실행하려면, 프로젝트 루트 폴더(`C:\datatide_workspaceN`)로 이동한 후 다음 명령어를 실행합니다.

```bash
python -m DataTide_back.create_tables
```

이 방식은 파이썬이 `DataTide_back`을 하나의 패키지로 인식하고, 그 안의 `create_tables` 모듈을 올바르게 찾아 실행하도록 합니다.
