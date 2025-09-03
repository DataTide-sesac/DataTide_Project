import mysql.connector
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field

import time
import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, pipeline, AutoModelForSeq2SeqLM

from langchain.agents import Tool
from langchain.chains import LLMMathChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain

# --- 환경변수 불러오기 ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../..", ".env"))
openai_api_key = os.getenv("OPENAI_API_KEY")
hf_token = os.getenv("HF_TOKEN")  # HuggingFace 토큰

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
    SELECT a.actor_id, a.first_name, a.last_name, f.film_id, f.title
    FROM actor a
    JOIN film_actor fa ON a.actor_id = fa.actor_id
    JOIN film f ON fa.film_id = f.film_id
"""
cursor.execute(sql)
rows = cursor.fetchall()

texts = [f"배우 아이디: {row[0]}, 이름: {row[1]} {row[2]}, 필름 아이디: {row[3]}, 제목: {row[4]}" 
         for row in rows]


# --- 2. 청크화 ---
splitter = CharacterTextSplitter(chunk_size=10000, chunk_overlap=10)
chunks = []
for text in texts:
    chunks.extend(splitter.split_text(text))

# --- 3. 임베딩 & 벡터 DB ---
embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-m3')
# embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')


# 이미 FAISS DB가 있으면 재사용 가능
if os.path.exists("faiss_index"):
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
else:
    vectorstore = FAISS.from_texts(chunks, embeddings)
    vectorstore.save_local("faiss_index")

print("임베딩 & FAISS DB 준비 완료!")

# --- 4. LLM 준비 ---
# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0,
#     openai_api_key=openai_api_key
# )

# --- 4. HuggingFace LLM 불러오기 ---
# model_id = "mistralai/Mistral-7B-Instruct-v0.2"  # GPU 없으면 작은 모델 추천
model_id = "google/flan-t5-base"  # GPU 없으면 작은 모델 추천
tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=hf_token)
model = AutoModelForSeq2SeqLM.from_pretrained(
    model_id,
    # device_map="auto",   # GPU 자동 할당
    # torch_dtype="auto",
    use_auth_token=hf_token
)

pipe = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.1
)

llm = HuggingFacePipeline(pipeline=pipe)

# --- 5. 메모리 세팅 (대화형 기억) ---
memory = ConversationBufferWindowMemory(
    memory_key="chat_history",   # 내부적으로 사용할 key 이름
    k=5
)

# --- 6. Conversational Retrieval Chain ---
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
    memory=memory
)

# --- 7. RAG 검색 & 생성 ---
while True:
    # query = "배우 아이디 3번에 대해 좀 알려줘"
    query = input("질문해주세요. >> ")
    if query.lower() == "exit":
        break
    
    # ---  유사 문서 검색 ---
    retrieved_docs = vectorstore.similarity_search(query, k=50)

    # --- 8. LLM 문서 평가 (Structured Output) --- 
    # 여러 문서를 한 번에 LLM에게 보내고 yes/no 결과 받기
    docs_text = "\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(retrieved_docs)])
    response_text = llm.invoke(f"""
        Question: {query}
        Documents:
        {docs_text}

        For each document (numbered), answer 'yes' if relevant, 'no' if not.
        Please return results in the format:
        1: yes
        2: no
        3: yes
        ...
        """)

    # 관련 문서만 선택
    relevant_docs = []
    lines = [line.strip() for line in response_text.splitlines() if line.strip()]
    for line, doc in zip(lines, retrieved_docs):
        if 'yes' in line.lower():
            relevant_docs.append(doc)

    print(f"관련 문서 수: {len(relevant_docs)}")

    # --- invoke로 RAG 호출 ---
    inputs = {
        "question": query,
        # "chat_history": [],  # memory를 이미 chain에 넣었으면 생략 가능
        "input_documents": relevant_docs
    }

    # chain = load_qa_chain(llm=qa_chain, chain_type="stuff")
    response = qa_chain.invoke(inputs)
    print("RAG 답변:", response)
    print("=" * 50)
