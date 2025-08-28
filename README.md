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
    - *(처음 실행할 시)* npm install
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
![00_화면레이아웃_1](https://github.com/user-attachments/assets/54d3b725-12f9-4d07-b297-5302553959b1)

---

## ⚙️ 워크 플로우
![00_워크플로우_1](https://github.com/user-attachments/assets/ddab7376-647b-44c3-aa76-29a554bd6886)

---

## 🗂️ ERD (Entity Relationship Diagram)
![00_ERD_1](https://github.com/user-attachments/assets/e9459ce4-a720-4a25-ba05-77eeeb291f6e)


---

## 👤 팀 역할 분담

- **데이터 전처리 / 분석** : 이형주, 임정훈  
- **AI 모델링** : 안수현  
- **웹 프론트엔드** : 신지원  
- **웹 백엔드** : 이나리  
- **발표자료 제작** : 팀원 전체 (5인 공동 참여)  

---


