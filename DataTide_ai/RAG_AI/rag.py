import mysql.connector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# 채팅을 위한 프롬프트 양식을 만듦
from langchain.prompts import ChatPromptTemplate

import time
import os
from dotenv import load_dotenv

# --- 환경변수 불러오기 ---
load_dotenv(dotenv_path='C:/datatide_workspaceN/DataTide_back/api/endpoints/.env')
openai_api_key = os.getenv("OPENAI_API_KEY")

mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")

# --- 1. MySQL 연결 ---
conn = mysql.connector.connect(
    host="localhost",
    user=mysql_user,
    password=mysql_password,
    database=mysql_database
)

# 디비에서 읽기
cursor = conn.cursor()
sql = """
    SELECT 
        CASE 
            WHEN i.item_name = 'Calamari' THEN '오징어'
            WHEN i.item_name = 'CutlassFish' THEN '갈치'
            WHEN i.item_name = 'Mackerel' THEN '고등어'
            ELSE i.item_name
        END AS item_name,
    ir.month_date, ir.production, ir.inbound, ir.sales, 
    gw.temperature as gw_temp, gw.rain as gw_rain,
    l.local_name,
    sw.temperature as sw_temp, sw.wind, sw.salinity, sw.wave_height, sw.wave_period, sw.wave_speed, sw.rain as sw_rain, sw.snow as sw_snow
    FROM item_retail ir
    LEFT JOIN sea_weather sw ON ir.month_date = sw.month_date
    LEFT JOIN ground_weather gw ON ir.month_date = gw.month_date
    LEFT JOIN location l ON sw.local_pk = l.local_pk
    LEFT JOIN item i ON ir.item_pk = i.item_pk
"""
cursor.execute(sql)
rows = cursor.fetchall()

texts = [f"""품목: {row[0]}, 날짜: {row[1]}, 생산량: {row[2]}, 수입량: {row[3]}, 판매량: {row[4]},
         전국 지상 날씨: {row[5]}, 전국 지상 강수량: {row[6]}, 지역: {row[7]},
         해양 날씨: {row[8]}, 염분: {row[9]}, 유의파고: {row[10]}, 유의파주기: {row[11]}, 유속: {row[12]}, 해양 강수량: {row[13]}, 해양 적설량: {row[14]}
        """
        for row in rows]


# --- 2. 청크화 ---
splitter = CharacterTextSplitter(chunk_size=10000, chunk_overlap=10)
chunks = []
for text in texts:
    chunks.extend(splitter.split_text(text))

# --- 3. 임베딩 & 벡터 DB ---
embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-m3')

if os.path.exists("faiss_index"):
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
else:
    vectorstore = FAISS.from_texts(chunks, embeddings)
    vectorstore.save_local("faiss_index")

print("임베딩 & FAISS DB 준비 완료!")

# --- 4. LLM 준비 ---
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=openai_api_key,
    max_tokens=1024  # 답변 길이를 늘려줍니다.
)

# --- 5. 메모리 세팅 (대화형 기억) ---
chat_history = []

# --- 6. RetrievalQA 체인 구성 ---
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 50}),
    return_source_documents=True,
)

# --- 7. RAG 검색 & 생성 ---
while True:
    query = input("질문해주세요. >> ")
    if query.lower() == "exit":
        break

    # 현재 대화 기록을 문자열로 변환합니다.
    history_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in chat_history])
    history_str += "\n"
    # print(history_str)

    # 사용자 지정 프롬프트 템플릿
    prompt = f"""
        당신은 품목당 생산, 수입, 판매량 데이터베이스 전문가 챗봇입니다.
        대답은 친절하게 해주세요.
        필요하다면 다음의 대화 기록을 참고하여 질문에 답변하세요.
        만약 답을 찾을 수 없다면, 모른다고 답하세요.

        대화 기록:
        {chat_history}

        질문: {query}
    """
    
    # invoke 호출 시, query와 chat_history를 모두 전달합니다.
    response = qa_chain({"query": prompt})

    # 대화 기록 업데이트
    # 질문과 답변을 (질문, 답변) 튜플로 저장합니다.
    chat_history.append((query, response['result']))
    
    # 최대 대화 기록을 5개로 유지 (k=5)
    if len(chat_history) > 5:
        chat_history.pop(0)

    # print("RAG 전체:", response)
    print("-" * 50)
    print("RAG 답변:", response["result"])
    print("=" * 50)