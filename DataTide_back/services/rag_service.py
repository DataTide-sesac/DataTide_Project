# services/rag_service.py
import os
import mysql.connector
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# --- Global variable for the RAG chain ---
qa_chain = None

def initialize_rag_pipeline():
    """
    Initializes the entire RAG pipeline.
    This should be called once at application startup.
    """
    global qa_chain

    # --- Load environment variables ---
    dotenv_path = 'C:/datatide_workspaceN/DataTide_back/api/endpoints/.env'
    load_dotenv(dotenv_path=dotenv_path)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER", "team_dt")
    db_password = os.getenv("DB_PASSWORD", "dt_1234")
    db_name = os.getenv("DB_NAME", "datatide_db")

    # --- 1. Fetch data from MySQL ---
    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
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
    except Exception as e:
        print(f"Error connecting to DB or fetching data for RAG: {e}")
        return

    texts = [f"품목: {row[0]}, 날짜: {row[1]}, 생산량: {row[2]}, 수입량: {row[3]}, 판매량: {row[4]}, "
             f"전국 지상 날씨: {row[5]}, 전국 지상 강수량: {row[6]}, 지역: {row[7]}, "
             f"해양 날씨: {row[8]}, 염분: {row[9]}, 유의파고: {row[10]}, 유의파주기: {row[11]}, 유속: {row[12]}, 해양 강수량: {row[13]}, 해양 적설량: {row[14]}"
             for row in rows]

    # --- 2. Chunking ---
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_text(' '.join(texts))

    # --- 3. Embedding & Vector DB ---
    embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-m3')
    faiss_index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'faiss_index'))

    if os.path.exists(faiss_index_path):
        vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
        print("FAISS index loaded from disk.")
    else:
        print("Building new FAISS index...")
        vectorstore = FAISS.from_texts(chunks, embeddings)
        vectorstore.save_local(faiss_index_path)
        print("FAISS index built and saved to disk.")

    # --- 4. LLM & QA Chain ---
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=openai_api_key,
        max_tokens=1024
    )

    global qa_chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
        return_source_documents=True,
    )
    print("RAG pipeline is ready.")

def get_rag_response(query: str) -> dict:
    """
    Gets a response from the RAG model for a given query.
    """
    global qa_chain
    if not qa_chain:
        return {"answer": "RAG 파이프라인이 아직 준비되지 않았습니다. 잠시 후 다시 시도해주세요."}

    prompt = f"""
        당신은 품목당 생산, 수입, 판매량 데이터베이스 전문가 챗봇입니다.
        대답은 친절하게 해주세요.
        만약 답을 찾을 수 없다면, 모른다고 답하세요.

        질문: {query}
    """
    
    try:
        response = qa_chain({"query": prompt})
        return {"answer": response.get("result", "답변을 찾을 수 없습니다.")}
    except Exception as e:
        print(f"Error during RAG query: {e}")
        return {"error": "RAG 모델에서 답변을 가져오는 데 실패했습니다."}
