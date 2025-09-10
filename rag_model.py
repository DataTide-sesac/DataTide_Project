# DataTide_ai/RAG_AI/rag_model.py

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# --------------------------------------------------------------------------
# 1. RAG 체인 설정 함수 (서버가 시작될 때 한 번만 실행)
# --------------------------------------------------------------------------
def setup_rag_chain():
    """
    RAG 파이프라인의 모든 구성 요소를 설정하고,
    사용자 질문에 답변할 수 있는 'chain' 객체를 생성하여 반환합니다.
    """
    print(">> RAG 체인 설정을 시작합니다...")

    # .env 파일에서 API 키 로드
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")

    # 1. 문서 로드 (Load)
    # 'data' 폴더에서 .txt 파일들을 모두 로드합니다.
    print(">> 1. 문서를 로드합니다...")
    loader = DirectoryLoader(
        path="./data",           # 데이터가 있는 폴더 경로
        glob="**/*.txt",       # .txt 확장자를 가진 모든 파일 대상
        loader_cls=TextLoader, # 텍스트 파일을 로드할 클래스
        loader_kwargs={'encoding': 'utf-8'} # 한글 처리를 위한 인코딩
    )
    documents = loader.load()
    if not documents:
        raise ValueError("'./data' 폴더에 참조할 .txt 문서가 없습니다.")
    print(f">> 총 {len(documents)}개의 문서를 로드했습니다.")


    # 2. 문서 분할 (Split)
    # 로드된 문서를 의미 있는 작은 단위(chunk)로 분할합니다.
    print(">> 2. 문서를 청크 단위로 분할합니다...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,         # 각 청크의 최대 크기
        chunk_overlap=50        # 청크 간의 중첩 크기
    )
    split_docs = text_splitter.split_documents(documents)
    print(f">> 총 {len(split_docs)}개의 청크로 분할되었습니다.")


    # 3. 임베딩 (Embedding) & 벡터 DB 저장 (Store)
    # 텍스트 청크들을 벡터로 변환하고, FAISS 벡터 저장소에 저장합니다.
    # 한국어 모델을 사용하여 더 정확한 의미 검색이 가능합니다.
    print(">> 3. 임베딩 및 벡터 DB 저장을 시작합니다...")
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-srobert-multitask", # 한국어 특화 임베딩 모델
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vector_store = FAISS.from_documents(split_docs, embeddings)
    print(">> 벡터 DB(FAISS) 생성이 완료되었습니다.")


    # 4. 검색기 생성 (Retrieve)
    # 벡터 저장소로부터 관련성 높은 문서를 검색하는 retriever를 생성합니다.
    retriever = vector_store.as_retriever()


    # 5. 프롬프트 템플릿 정의 (Prompt)
    # LLM에 질문과 함께 전달할 프롬프트의 형식을 정의합니다.
    # 주어진 'context' 내에서만 답변하도록 명확하게 지시하는 것이 중요합니다.
    template = """
    당신은 수산물 전문가입니다. 사용자의 질문에 대해 아래의 'context' 정보만을 사용하여 답변해주세요.
    만약 context에 답변에 필요한 정보가 없다면, "제공된 정보만으로는 답변하기 어렵습니다."라고 솔직하게 답변하세요.

    [Context]
    {context}

    [Question]
    {question}
    """
    prompt = ChatPromptTemplate.from_template(template)


    # 6. LLM 모델 정의 (LLM)
    # OpenAI의 GPT 모델을 사용합니다.
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1)


    # 7. RAG 체인 구성 (Chain)
    # LangChain Expression Language (LCEL)을 사용하여 파이프라인을 연결합니다.
    # 이 체인은 retriever로 문서를 찾고, prompt를 만들고, llm으로 답변을 생성합니다.
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print(">> RAG 체인 설정이 완료되었습니다! ✅")
    return rag_chain

# --------------------------------------------------------------------------
# 2. 응답 생성 함수 (API가 호출할 함수)
# --------------------------------------------------------------------------
def get_rag_response(chain, query: str) -> str:
    """
    미리 생성된 RAG 체인을 사용하여 사용자의 질문(query)에 대한 답변을 생성합니다.
    """
    print(f">> RAG 모델 호출: '{query}'")
    
    # 체인을 실행하여 답변을 얻습니다.
    response = chain.invoke(query)
    
    print(">> RAG 모델 응답 수신 완료.")
    return response