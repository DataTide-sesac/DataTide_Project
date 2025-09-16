# services/rag_service.py (최종 버전)
import os
import mysql.connector
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
import time

# --- 전역 변수 ---
qa_chain = None
FAISS_INDEX_PATH = "faiss_index_storage" # FAISS DB를 저장할 폴더 이름

def initialize_rag_pipeline():
    global qa_chain
    start_time = time.time()
    print(f"[{time.time() - start_time:.2f}초] 1. 환경변수 로딩 시작...")
    load_dotenv()
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    db_user = os.getenv("MYSQL_USER")
    db_password = os.getenv("MYSQL_PASSWORD")
    db_name = os.getenv("MYSQL_DATABASE")
    db_host = "localhost"

    print(f"[{time.time() - start_time:.2f}초] 2. 임베딩 모델 로딩 시작...")
    embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-m3')
    print(f"[{time.time() - start_time:.2f}초] 임베딩 모델 로딩 완료.")

    # --- ✨ FAISS DB가 이미 존재하는지 확인 ---
    if os.path.exists(FAISS_INDEX_PATH):
        print(f"[{time.time() - start_time:.2f}초] 저장된 FAISS DB를 불러옵니다...")
        vectorstore = FAISS.load_local(
            FAISS_INDEX_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True # 이 옵션이 필요합니다
        )
        print(f"[{time.time() - start_time:.2f}초] FAISS DB 로딩 완료.")
    else:
        # --- DB가 없으면 새로 생성 ---
        print(f"[{time.time() - start_time:.2f}초] 3. DB 연결 및 데이터 조회 시작...")
        try:
            conn = mysql.connector.connect(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
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
            conn.close()
            print(f"[{time.time() - start_time:.2f}초] DB에서 총 {len(rows)}개의 데이터를 가져왔습니다.")
        except Exception as e:
            print(f"DB 연결 또는 데이터 조회 중 오류 발생: {e}")
            return

        print(f"[{time.time() - start_time:.2f}초] 4. 텍스트 데이터로 변환 시작...")
        texts = [
            f"품목: {row[0]}, 날짜: {row[1]}, 생산량: {row[2]}, 수입량: {row[3]}, 판매량: {row[4]}, "
            f"전국 지상 온도: {row[5]}, 전국 지상 강수량: {row[6]}, 지역: {row[7]}, "
            f"해양 온도: {row[8]}, 풍속: {row[9]}, 염분: {row[10]}, 유의파고: {row[11]}, 유의파주기: {row[12]}, 유속: {row[13]}, 해양 강수량: {row[14]}, 해양 적설량: {row[15]}"
            for row in rows
        ]

        print(f"[{time.time() - start_time:.2f}초] 5. FAISS 벡터 DB 생성 시작... (시간이 오래 걸릴 수 있습니다)")
        vectorstore = FAISS.from_texts(texts, embeddings)
        print(f"[{time.time() - start_time:.2f}초] FAISS 벡터 DB 생성 완료. 디스크에 저장합니다...")
        vectorstore.save_local(FAISS_INDEX_PATH)
        print(f"[{time.time() - start_time:.2f}초] FAISS DB 저장 완료.")

    print(f"[{time.time() - start_time:.2f}초] 6. LLM 및 QA 체인 구성 시작...")
    llm = ChatOpenAI(
        model="gpt-4o-mini", temperature=0,
        openai_api_key=openai_api_key, max_tokens=1024
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
        return_source_documents=True,
    )
    print(f"[{time.time() - start_time:.2f}초] RAG 파이프라인 준비 완료.")

def get_rag_response(query: str) -> dict:
    global qa_chain
    if not qa_chain:
        return {"answer": "RAG 파이프라인이 아직 준비되지 않았습니다."}
    prompt = f"질문: {query}"
    try:
        response = qa_chain.invoke({"query": prompt})
        return {"answer": response.get("result", "답변을 생성하지 못했습니다.")}
    except Exception as e:
        print(f"RAG 응답 생성 중 오류 발생: {e}")
        return {"error": "모델 응답 생성에 실패했습니다."}