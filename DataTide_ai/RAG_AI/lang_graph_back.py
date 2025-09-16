import mysql.connector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# 채팅을 위한 프롬프트 양식을 만듦
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
import langchain

# 시간 라이브러리
from datetime import datetime
import os
import json, requests
from tempfile import tempdir
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END  # 상태그래프와 END노드 세팅
from typing_extensions import TypedDict             # 상태그래프 커스터마이징
from langchain.agents import Tool
from langchain.chains import LLMMathChain

# tool 데코레이터를 사용해서 일반 함수를 '툴'로 인지시키기 위함
from langchain.tools import tool
#만든 툴을 사용하자!
from langchain.chat_models import init_chat_model


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
texts = []
def read_sql_1():
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
    
def read_sql_2():
    sql = """
        SELECT 
            CASE 
                WHEN i.item_name = 'Calamari' THEN '오징어'
                WHEN i.item_name = 'CutlassFish' THEN '갈치'
                WHEN i.item_name = 'Mackerel' THEN '고등어'
                ELSE i.item_name
            END AS item_name,
        ir.month_date, ir.production, ir.inbound, ir.sales
        FROM item_retail ir
        LEFT JOIN item i ON ir.item_pk = i.item_pk
    """
    cursor.execute(sql)
    rows = cursor.fetchall()

    texts = [f"""품목: {row[0]}, 날짜: {row[1]}, 생산량: {row[2]}, 수입량: {row[3]}, 판매량: {row[4]}
            """
            for row in rows]
    
    return texts
    
texts = read_sql_2()

# --- 2. 청크화 ---
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
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
model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    openai_api_key=openai_api_key,
    max_tokens=256  # 답변 길이를 늘려줍니다.
)

# 동일한 세팅의 llm을 LLMMathChain에게 전달
llm_math = LLMMathChain(llm=ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
        openai_api_key=openai_api_key,
        max_tokens=256  # 답변 길이를 늘려줍니다.
    ))

# 수학적 툴
math_tool = Tool(
    name = 'calculator',
    func = llm_math.run,
    description = '수학 계산과 관련된 문제에 대해 필요하면 이 도구를 쓰시오.'
)

# --- 5. 추가 데이터 분석 도구들 ---
@tool
def analyze_data(query: str) -> str:
    """RAG 데이터를 분석하고 계산을 수행합니다. 최대값, 최소값, 평균, 합계 등을 계산할 수 있습니다."""
    try:
        import re
        import statistics
        from collections import defaultdict
        
        # 벡터 저장소에서 관련 문서 검색
        docs = vectorstore.similarity_search(query, k=100)
        
        # 숫자 데이터 추출
        data_dict = defaultdict(list)
        
        for doc in docs:
            content = doc.page_content
            
            # 생산량, 수입량, 판매량 등의 숫자 데이터 추출
            patterns = {
                '생산량': r'생산량:\s*([0-9.]+)',
                '수입량': r'수입량:\s*([0-9.]+)',
                '판매량': r'판매량:\s*([0-9.]+)'
            }
            
            for key, pattern in patterns.items():
                matches = re.findall(pattern, content)
                for match in matches:
                    try:
                        value = float(match)
                        if value > 0:  # 0보다 큰 값만 포함
                            data_dict[key].append(value)
                    except ValueError:
                        continue
        
        # 분석 결과 생성
        result = "=== 데이터 분석 결과 ===\n"
        
        for key, values in data_dict.items():
            if values:
                result += f"\n【{key}】\n"
                result += f"  데이터 개수: {len(values)}개\n"
                result += f"  최대값: {max(values):.2f}\n"
                result += f"  최소값: {min(values):.2f}\n"
                result += f"  평균값: {statistics.mean(values):.2f}\n"
                result += f"  합계: {sum(values):.2f}\n"
                
                if len(values) > 1:
                    result += f"  표준편차: {statistics.stdev(values):.2f}\n"
        
        return result if result != "=== 데이터 분석 결과 ===\n" else "분석할 수 있는 숫자 데이터를 찾을 수 없습니다."
        
    except Exception as e:
        return f"데이터 분석 오류: {str(e)}"

# tools = [math_tool]
tools = [math_tool, analyze_data]
print(tools[0].name, tools[0].description)

# model(생각할 llm, agent의 두뇌),
# tools(agent가 사용가능한 도구 목록),
# prompt(agent가 판단할 때 어떤 기준이 있다면? 이걸 프롬프트가 담고 있다.)
prompt = ChatPromptTemplate.from_messages([
    ('system', '''당신은 품목당 날짜에 따른 생산, 수입, 판매량 데이터베이스 전문가입니다.
    만약 해당 내용에 대한 질문이 아니라면 저희는 품목당 날짜에 따른 생산, 수입, 판매량만 알려주는 챗봇이라 모른다고 답해줘.
    대답은 친절하게 해주세요.
    다음 도구들을 활용할 수 있어:
    1. calculator: 수학 계산
    2. analyze_data: 데이터 분석 및 통계 계산
    
    사용자의 질문에 따라 적절한 도구를 선택해서 사용해줘.'''),
    ('human', '{input}'),
    ('placeholder', '{agent_scratchpad}')   # tools을 사용하면서 남기는 중간 작업 내역
])

# agent를 만듦 => 이 agent는 tool을 calling =>
# model(두뇌)로 tools(도구)를 prompt(지시사항)에 맞게 판단해서 부름
agent = create_tool_calling_agent(model, tools, prompt)

# 에이전트의 실행
agent_executor = AgentExecutor(agent=agent, tools=tools)
# result = agent_executor.invoke({'input':'what is 2.1^2.1'})

# --- 6. RetrievalQA 체인 구성 ---
qa_chain = RetrievalQA.from_chain_type(
    llm=model,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
    return_source_documents=True,
)

# --- 7. LangGraph State 정의 ---
class AgentState(TypedDict):
    query: str
    chat_history: list
    current_time: str
    rag_result: str
    agent_result: str
    final_answer: str
    needs_agent: bool
    source_documents: list

# --- 8. LangGraph 노드 함수들 ---
def classify_query_node(state: AgentState):
    """질문 분류 노드 - Agent가 필요한지 판단"""
    query = state["query"]
    
    # 계산/분석이 필요한 키워드들
    analysis_keywords = ['최대', '최소', '평균', '합계', '분석', '통계', '계산', '비교', '총합']
    search_keywords = ['찾아', '검색', '언제', '어떤', '몇', '얼마', '가장']
    
    # 키워드에 따라 Agent 필요 여부 결정
    needs_agent = any(keyword in query for keyword in analysis_keywords + search_keywords)
    
    state["needs_agent"] = needs_agent
    print(f"🔍 질문 분류: {'Agent 필요' if needs_agent else 'RAG만 필요'}")
    
    return state

from zoneinfo import ZoneInfo
def get_time(state: AgentState):
    """현재 년도와 월 가져오기"""
    KST = ZoneInfo('Asia/Seoul')
    y = datetime.now(KST).year
    m = datetime.now(KST).month

    state["current_time"] = f"{y}년 {m}월"
    # print(f'{state["current_time"]}')

    return state


def rag_node(state: AgentState):
    """RAG 검색 노드"""
    print("📚 RAG 검색 시작...")
    
    try:
        # 대화 기록을 문자열로 변환
        history_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in state["chat_history"]])
        
        # RAG 프롬프트 구성
        rag_prompt = f"""
            당신은 품목당 날짜에 따른 생산, 수입, 판매량 데이터베이스 전문가입니다.
            만약 해당 내용에 대한 질문이 아니라면 저희는 품목당 날짜에 따른 생산, 수입, 판매량만 알려주는 챗봇이라 모른다고 답해줘.
            대답은 친절하게 해주세요.
            필요하다면 다음의 대화 기록을 참고하여 질문에 답변하세요.
            만약 답을 찾을 수 없다면, 모른다고 답하세요.

            현재 시각: {state["current_time"]}

            대화 기록:
            {history_str}

            질문: {state["query"]}
        """
        
        response = qa_chain.invoke({"query": rag_prompt})
        state["rag_result"] = response['result']
        state["source_documents"] = response.get('source_documents', [])
        
        print(f"✅ RAG 검색 완료: {len(state['source_documents'])}개 문서 참조")
        
    except Exception as e:
        print(f"❌ RAG 오류: {e}")
        state["rag_result"] = f"RAG 검색 오류: {str(e)}"
        state["source_documents"] = []
    
    return state

def agent_node(state: AgentState):
    """Agent 분석 노드"""
    print("🤖 Agent 분석 시작...")
    
    try:
        # RAG 결과를 포함한 입력 구성
        # RAG 검색 결과: {state["rag_result"]}
        # RAG 검색 결과: {texts}
        agent_input = f"""
        현재 시각: {state["current_time"]}

        검색 결과: {texts}
        
        원래 사용자 질문: {state["query"]}
        
        위 RAG 결과를 바탕으로 필요한 분석이나 계산을 수행해주세요.
        만약 추가적인 데이터 분석이 필요하다면 analyze_data 도구를 사용하고,
        수학 계산이 필요하다면 calculator 도구를 사용해주세요.
        """
        
        response = agent_executor.invoke({"input": agent_input})
        state["agent_result"] = response['output']
        
        print("✅ Agent 분석 완료")
        
    except Exception as e:
        print(f"❌ Agent 오류: {e}")
        state["agent_result"] = f"Agent 분석 오류: {str(e)}"
    
    return state

def combine_results_node(state: AgentState):
    """결과 통합 노드"""
    print("🔗 결과 통합 중...")
    
    if state["needs_agent"] and state["agent_result"] and "오류" not in state["agent_result"]:
        # Agent 결과가 있는 경우
        state["final_answer"] = f"""{state["agent_result"]}

{state["rag_result"]}"""
    else:
        # RAG만 사용하는 경우
        state["final_answer"] = state["rag_result"]
    
    print("✅ 결과 통합 완료")
    return state

# --- 9. 라우팅 함수 ---
def decide_next_step(state: AgentState):
    """다음 단계를 결정하는 라우팅 함수"""
    if state["needs_agent"]:
        return "agent"
    else:
        return "combine"

# --- 10. LangGraph 워크플로우 구성 ---
workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("classify", classify_query_node)
workflow.add_node("time", get_time)
workflow.add_node("rag", rag_node)
workflow.add_node("agent", agent_node)
workflow.add_node("combine", combine_results_node)

# 엣지 추가
def workflow_add_edge_2():
    workflow.add_edge(START, "classify")
    workflow.add_edge("classify", "time")
    workflow.add_conditional_edges(
        "time",
        decide_next_step,
        {
            "agent": "agent",
            "combine": "rag"
        }
    )
    workflow.add_edge("agent", "combine")
    workflow.add_edge("rag", "combine")
    workflow.add_edge("combine", END)

workflow_add_edge_2()

# 워크플로우 컴파일
app = workflow.compile()

print("🚀 LangGraph 워크플로우 준비 완료!")

# --- 11. 메인 대화 루프 ---
chat_history = []

while True:
    query = input("\n질문해주세요. >> ")
    if query.lower() == "exit":
        break
    
    print("\n" + "="*60)
    print(f"📝 사용자 질문: {query}")
    print("="*60)
    
    # LangGraph 실행
    try:
        result = app.invoke({
            "query": query,
            "chat_history": chat_history,
            "rag_result": "",
            "agent_result": "",
            "final_answer": "",
            "needs_agent": False,
            "source_documents": []
        })
        
        # 결과 출력
        final_answer = result['final_answer']
        source_docs = result['source_documents']
        
        # 대화 기록 업데이트 (최대 3개 유지)
        chat_history.append((query, final_answer))
        if len(chat_history) > 3:
            chat_history.pop(0)
        
        # 결과 표시
        print("\n" + "-"*50)
        if source_docs:
            print(f"📊 참조된 문서 수: {len(source_docs)}개")
        print(f"💬 답변:\n{final_answer}")
        print("="*50)
        
    except Exception as e:
        print(f"❌ 전체 처리 오류: {str(e)}")
        print("="*50)

# 갈치의 평균 생산량
# 총 9693
# 평균 1,384.714285

# 오징어의 평균 생산량
# 총 6435
# 평균 919.285714

# 고등어의 평균 생산량
# 총 60,483
# 평균 8,640.4285