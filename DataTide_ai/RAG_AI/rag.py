# -*- coding: utf-8 -*-
import os, glob
from dotenv import load_dotenv
from PyPDF2 import PdfReader

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.chat_models import ChatOpenAI

# --- 환경변수 불러오기 ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../..", ".env"))
openai_api_key = os.getenv("OPENAI_API_KEY")

# --- PDF 읽기 ---
folder_path = "../../data/sea_weather/경북/2015_월간보고서/수온"
pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

all_texts = ""
for pdf_file in pdf_files:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        all_texts += page.extract_text() or ""

# --- 청크 나누기 (chunk_size 늘리고 overlap 줄여서 호출 최소화) ---
splitter = CharacterTextSplitter(
    chunk_size=1000,  # 기존 500 → 1000으로 늘림
    chunk_overlap=20,  # 기존 10 → 20 (조금 겹치도록)
    separator='\n'
)
chunks = splitter.split_text(all_texts)

# --- 임베딩 & 벡터 DB ---
embeddings = HuggingFaceBgeEmbeddings(model_name='BAAI/bge-m3')
vectorstore = FAISS.from_texts(chunks, embeddings)

# --- 검색 ---
query = "2015년 수온 1월 1일 온도가 뭐야?"
retrieved_docs = vectorstore.similarity_search(query, k=1)  # k=1로 최소화

# --- LLM으로 QA 체인 실행 ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)
chain = load_qa_chain(llm=llm, chain_type="stuff")  # 한 번에 합쳐서 전달

response = chain.run(input_documents=retrieved_docs, question=query)
print("RAG 답변:", response)

# --- 벡터 DB 저장 (선택 사항) ---
# vectorstore.save_local('faiss')
