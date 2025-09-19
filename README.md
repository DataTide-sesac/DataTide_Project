# 🌊 Team Project: DataTide

## 👥 팀명
**DataTide**  
(데이터의 흐름을 파도처럼 읽어내는 팀)

---

## 📱 서비스 형태
- **모바일 웹** 기반 서비스

---

## 🎨 프론트엔드
- **React**  
  - 예측 결과 시각화 및 UI 구현  
  - 사용자 친화적인 대시보드 제공
 
  - **파일 위치**
    - DataTide_front
  - **실행 방법**
    - cd DataTide_front
    - *(처음 실행할 시)* npm install --prefix DataTide_front
    - npm run dev

---

## ⚙️ 백엔드
- **FastAPI**  
  - 데이터 수집 및 전처리  
  - 예측형 AI 모델 실행  
  - 프론트엔드와의 API 연동
 
  - **파일 위치**
    - DataTide_back
  - **실행 방법**
    - cd DataTide_back
        - *(처음 실행할 시)* pip install -r requirements.txt
    - python -m uvicorn main:app --reload

---

## 🧠 AI 구성
- **예측형 AI**  
  - 수산물 리테일 생산량 / 판매량 / 수입량 예측
- **LLM (RAG)**  
  - 예측 결과를 자연스럽고 보기 좋은 문장으로 변환  
  - 사용자 질의응답(Q&A) 기능 제공
 
  - **파일 위치**
    - DataTide_ai
  - **실행 방법**
    - cd DataTide_ai
    - python 파일이름.py

---

## 🔄 시스템 흐름

### 📌 1순위
1. **수산물 데이터 수집**
2. **백엔드**
   - 데이터 전처리 및 계산
   - AI 모델을 이용한 예측 수행
3. **프론트엔드**
   - 예측 결과를 시각화하여 표출

### 📌 2순위
- **LLM + RAG**를 이용해  
  예측 결과를 **자연스럽고 보기 좋은 문장**으로 변환 후 출력

---

## 📊 데이터 소스

- **수산물 리테일 API**  
  [KMI 수산물 유통 종합정보시스템](https://fishdata.kmi.re.kr/fornt/openApi/main.do)

- **해양 온도 데이터**  
  [국립수산과학원 RISA](https://www.nifs.go.kr/risa/risaStatList.risa)

- **기상청 날씨 데이터** (위치, 기온, 풍속, 강수량, 적설)  
  [기상자료개방포털](https://data.kma.go.kr/data/grnd/selectAsosRltmList.do?pgmNo=36)

---

## 🖥️ 화면 레이아웃
![00_화면레이아웃_2](https://github.com/user-attachments/assets/f026f4e9-8bd2-4f42-9afb-7d1cf97ab95c)

---

## ⚙️ 워크 플로우
<img width="786" height="825" alt="00_워크플로우_2" src="https://github.com/user-attachments/assets/be0bee73-f4fc-4f25-8c8d-eebd98971a8d" />

---

## 🗂️ ERD (Entity Relationship Diagram)
<<<<<<< HEAD
> [!WARNING]
> 현재 DB 모델이 대규모로 리팩토링되어 아래 ERD는 최신이 아닙니다. 빠른 시일 내에 업데이트가 필요합니다.

![00_ERD_4](https://github.com/user-attachments/assets/013de0ff-6f5e-4b7c-8ea2-9e5d69d1fba7)
=======
![00_ERD_5](https://github.com/user-attachments/assets/3eafeb39-5945-40e5-b2ec-88789c95d15f)

---

## 🔵 랭그래프 (Lang Graph)
<img width="189" height="531" alt="LangGraph" src="https://github.com/user-attachments/assets/bf59a0ab-13f0-4bc4-9c0a-eadf428cc69c" />
>>>>>>> main


---

## ⚙️ 개발 환경

- **파이썬 버전** : 3.10.18
  - **데이터 관련 라이브러리** : pymysql numpy pandas matplotlib seaborn tqdm
  - **AI 관련 라이브러리** : torch torchvision torchaudio scikit-learn
  - **웹 관련 라이브러리** : fastapi

- **리액트 버전** : 19.1.1
  - **axios** : 1.11.0
  - **bootstrap** : 5.3.8
  - **react-bootstrap** : 2.10.10
  - **react-router-dom** : 7.8.2
 

---

## 🐍 가상환경 설정

### 1️⃣ 가상환경 생성 및 활성화
```bash
conda create -n DataTide python=3.10.18 -y
conda activate DataTide
```
### 2️⃣ 라이브러리 다운로드
```bash
cd DataTide_Project
pip install -r requirements.txt
```


---

## 👤 팀 역할 분담

- **데이터 전처리 / 분석** : 이형주, 임정훈  
- **AI 모델링** : 안수현  
- **웹 프론트엔드** : 신지원  
- **웹 백엔드** : 이나리  
- **발표자료 제작** : 팀원 전체 (5인 공동 참여)  

---


