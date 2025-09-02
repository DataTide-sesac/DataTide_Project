import mysql.connector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field

import time
import os
from dotenv import load_dotenv

from langchain.agents import Tool
from langchain.chains import LLMMathChain
from langchain.llms import OpenAI

# --- 환경변수 불러오기 ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../..", ".env"))
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

# --- 4. RAG 검색 & 생성 ---
query = "배우 아이디 3번에 대해 좀 알려줘"
retrieved_docs = vectorstore.similarity_search(query, k=50)

# ===============================
# 5. LLM 문서 평가 (Structured Output)
# ===============================
# 동일한 세팅의 llm을 LLMMathChain에게 전달
llm_math = LLMMathChain(llm=OpenAI(temperature=0, openai_api_key=openai_api_key))

# 수학적 툴
math_tool = Tool(
    name = 'calculator',
    func = llm_math.run,
    description = '수학 계산과 관련된 문제에 대해 필요하면 이 도구를 쓰시오.'
)

tools = [math_tool]

llm = ChatOpenAI(
    model="gpt-4o-mini", 
    temperature=0,
    openai_api_key=openai_api_key
    )

# 평가 결과 구조 정의
def parse_binary_score(text: str) -> str:
    text = text.lower()
    if 'yes' in text:
        return 'yes'
    else:
        return 'no'

relevant_docs = []
# 여러 문서를 한 번에 LLM에게 보내고 yes/no 결과 받기
docs_text = "\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(retrieved_docs)])
response_text = llm.predict(f"""
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

# LLM 응답 파싱
for line, doc in zip(response_text.splitlines(), retrieved_docs):
    if 'yes' in line.lower():
        relevant_docs.append(doc)

# for doc in retrieved_docs:
#     response = llm.predict(f"""
#     You are a grader. 
#     Question: {query}
#     Retrieved Document: {doc.page_content}
#     Answer 'yes' if the document is relevant, otherwise 'no'.
#     """)
#     score = parse_binary_score(response)
#     if score == 'yes':
#         relevant_docs.append(doc)
#     time.sleep(5)

print(f"관련 문서 수: {len(relevant_docs)}")


chain = load_qa_chain(llm=llm, chain_type="stuff")
response = chain.run(input_documents=relevant_docs, question=query)
print("RAG 답변:", response)
