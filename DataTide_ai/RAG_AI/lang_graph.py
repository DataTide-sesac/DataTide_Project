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
from datetime import datetime, timedelta
import os, pickle, time
import numpy as np
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
    # 🔥 캐시 확인 (새로 추가된 부분)
    cached_result = cache.get(query, "analyze")
    if cached_result:
        return f"[캐시됨] {cached_result}"  # 🚀 즉시 리턴!
    
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
    ('system', '''당신은 품목당(갈치, 오징어, 고등어) 날짜에 따른 생산, 수입, 판매량 데이터베이스 전문가입니다.
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
    retriever=vectorstore.as_retriever(search_kwargs={"k": 30}),
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

# ==========================================
# 해결책 1: 질문 정규화 및 의미 기반 캐싱
# ==========================================

class SmartCache:
    def __init__(self, cache_dir="cache", expire_hours=12):
        self.cache_dir = cache_dir
        self.expire_hours = expire_hours
        self.memory_cache = {}
        self.access_count = 0
        self.last_cleanup = datetime.now()
        self.running = False
        self.cleanup_thread = None
        
        # 🔥 의미 기반 캐싱을 위한 임베딩 모델
        self.embeddings = embeddings

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        print(f"🗄️ 스마트 캐시 초기화: {cache_dir}, 만료: {expire_hours}시간")
        
        # 🔥 백그라운드 정리 스레드 시작
        self._start_background_cleanup()

    def _start_background_cleanup(self):
        """백그라운드 캐시 정리 스레드 시작"""
        import threading
        
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._background_worker, daemon=True)
        self.cleanup_thread.start()
        print("🧵 백그라운드 캐시 정리 스레드 시작")
    
    def _background_worker(self):
        """백그라운드에서 주기적으로 캐시 정리"""
        while self.running:
            try:
                # 30분마다 정리
                time.sleep(1800)
                
                if not self.running:
                    break
                
                start_time = time.time()
                cleaned = self._cleanup_expired_caches()
                elapsed = time.time() - start_time
                
                if cleaned > 0:
                    print(f"🧹 백그라운드 정리: {cleaned}개 삭제 ({elapsed:.2f}초)")
                
            except Exception as e:
                print(f"❌ 백그라운드 정리 오류: {e}")
                time.sleep(300)  # 오류시 5분 대기
    
    def _cleanup_expired_caches(self):
        """만료된 캐시들을 실제로 정리"""
        cleaned_count = 0
        current_time = datetime.now()
        expire_threshold = timedelta(hours=self.expire_hours)
        
        # 메모리 캐시 정리
        expired_keys = []
        for key, cached_data in self.memory_cache.items():
            if current_time - cached_data['timestamp'] > expire_threshold:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
            cleaned_count += 1
        
        # 디스크 캐시 정리  
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'rb') as f:
                            cached_data = pickle.load(f)
                        
                        if current_time - cached_data['timestamp'] > expire_threshold:
                            os.remove(file_path)
                            cleaned_count += 1
                    except:
                        # 손상된 파일도 삭제
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                        except:
                            pass
        
        return cleaned_count
    
    def stop_cleanup(self):
        """캐시 정리 스레드 중지"""
        self.running = False
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        print("🛑 백그라운드 캐시 정리 중지")
    
    def __del__(self):
        """캐시 객체 소멸됨"""
        self.stop_cleanup()
        
    def _normalize_query(self, query):
        """질문을 정규화해서 유사한 질문들을 같게 만듦"""        
        # 1. 기본 정규화
        normalized = query.lower().strip()
        
        # 2. 불필요한 단어 제거
        stop_words = ['은', '는', '이', '가', '을', '를', '의', '에', '서', '에서', 
                     '어떻게', '얼마', '뭐', '무엇', '언제', '어디서']
        for word in stop_words:
            normalized = normalized.replace(word, '')
        
        # 3. 공백 정리
        normalized = ' '.join(normalized.split())
        
        # 4. 동의어 통일
        synonyms = {
            '생산량': ['생산', '생산량', '산출량', 'production'],
            '판매량': ['판매', '판매량', '매출량', 'sales'],
            '수입량': ['수입', '수입량', 'import', 'inbound'],
            '갈치': ['갈치', 'galchi', '갈치생선', 'cutlassFish'],
            '오징어': ['오징어', 'squid', '오징어류', 'calamari'],
            '고등어': ['고등어', 'mackerel', '고등어류']
        }
        
        for standard, variations in synonyms.items():
            for variation in variations:
                if variation in normalized:
                    normalized = normalized.replace(variation, standard)
        
        return normalized
    
    def _get_semantic_similarity(self, query1, query2):
        """두 질문의 의미적 유사도를 계산"""
        try:
            # 임베딩 벡터 생성
            emb1 = self.embeddings.embed_query(query1)
            emb2 = self.embeddings.embed_query(query2)
            
            # 코사인 유사도 계산
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return similarity
        except:
            return 0.0
    
    def _find_similar_cache(self, query, threshold=0.85):
        """유사한 질문의 캐시를 찾음"""
        normalized_query = self._normalize_query(query)
        
        # 1. 정규화된 질문으로 정확히 일치하는 캐시 찾기
        for cache_key, cached_data in self.memory_cache.items():
            if 'original_query' in cached_data:
                cached_normalized = self._normalize_query(cached_data['original_query'])
                if cached_normalized == normalized_query:
                    return cached_data
        
        # 2. 의미적 유사도 기반으로 캐시 찾기
        best_match = None
        best_similarity = 0
        
        for cache_key, cached_data in self.memory_cache.items():
            if 'original_query' in cached_data:
                similarity = self._get_semantic_similarity(query, cached_data['original_query'])
                if similarity > threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = cached_data
        
        if best_match:
            print(f"🎯 의미적 유사 캐시 히트! 유사도: {best_similarity:.2f}")
            return best_match
        
        return None
    
    def _get_cache_key(self, query, context_type="rag"):
        """캐시 조회"""
        cache_key = f"{query}_{context_type}"
        return cache_key
    
    def _is_expired(self, timestamp):
        now = datetime.now()
        hours = now - timestamp
        if hours > timedelta(hours=12):
            print("캐시 12시간 이상 지남")
            return True
        
        return False
    
    def get(self, query, context_type="rag"):
        """개선된 캐시 조회 - 유사한 질문도 찾음"""
        self.access_count += 1
        
        # 1. 기존 방식으로 정확한 캐시 확인
        cache_key = self._get_cache_key(query, context_type)
        if cache_key in self.memory_cache:
            cached_data = self.memory_cache[cache_key]
            if not self._is_expired(cached_data['timestamp']):
                # 🔥 100번 접근마다 지연 정리 실행
                if self.access_count % 100 == 0:
                    import threading
                    threading.Thread(target=self._light_cleanup, daemon=True).start()

                print(f"💾 정확한 캐시 히트: {query[:30]}...")
                return cached_data
        
        # 2. 유사한 질문의 캐시 확인
        similar_cache = self._find_similar_cache(query)
        if similar_cache and not self._is_expired(similar_cache['timestamp']):
            return similar_cache
        
        # 2. 디스크 캐시 확인 (기존 코드와 동일)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                if not self._is_expired(cached_data['timestamp']):
                    self.memory_cache[cache_key] = cached_data
                    print(f"💽 디스크 캐시 히트: {query[:30]}...")
                    return cached_data
                else:
                    os.remove(cache_file)
            except:
                pass
        
        return None
    
    def set(self, query, result, context_type="rag"):
        """캐시 저장 시 원본 질문도 함께 저장"""
        cache_key = self._get_cache_key(query, context_type)
        
        cached_data = {
            'result': result,
            'timestamp': datetime.now(),
            'original_query': query,  # 🔥 원본 질문 저장
            'context_type': context_type
        }
        
        self.memory_cache[cache_key] = cached_data
        print(f"💾 스마트 캐시 저장: {query[:30]}...")
    
    def _light_cleanup(self):
        """지연 정리: 일부 캐시만 확인해서 정리"""
        current_time = datetime.now()
        
        # 최근 5분 내에 정리했으면 스킵
        if current_time - self.last_cleanup < timedelta(minutes=5):
            return
        
        cleaned_count = 0
        checked_count = 0
        
        # 메모리 캐시 일부만 확인 (최대 50개)
        cache_items = list(self.memory_cache.items())
        for key, cached_data in cache_items[:50]:
            checked_count += 1
            if self._is_expired(cached_data['timestamp']):
                del self.memory_cache[key]
                cleaned_count += 1
        
        if cleaned_count > 0:
            print(f"🐌 지연 정리: {checked_count}개 확인, {cleaned_count}개 삭제")
        
        self.last_cleanup = current_time

# 전역 캐시 인스턴스
cache = SmartCache(cache_dir="lang_cache", expire_hours=12)

# --- 8. LangGraph 노드 함수들 ---
def classify_query_node(state: AgentState):
    """질문 분류 노드 - Agent가 필요한지 판단"""
    query = state["query"]
    
    # 계산/분석이 필요한 키워드들
    analysis_keywords = ['최대', '최소', '평균', '합계', '분석', '통계', '계산', '비교', '총합', '가장']
    search_keywords = ['찾아', '검색', '언제', '어떤', '몇', '얼마']
    
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

    # 🔥 캐시 확인 (새로 추가된 부분)
    cached_result = cache.get(query, "rag")
    if cached_result:
        print("💾 RAG 캐시 히트!")
        state["rag_result"] = cached_result["result"]
        state["source_documents"] = cached_result.get("source_docs", [])
        return state  # 🚀 LLM 호출 없이 바로 리턴!
    
    try:
        # 대화 기록을 문자열로 변환
        history_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in state["chat_history"]])
        
        # RAG 프롬프트 구성
        rag_prompt = f"""
            당신은 품목당(갈치, 오징어, 고등어) 날짜에 따른 생산, 수입, 판매량 데이터베이스 전문가입니다.
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

        cache.set(query=query, result=response['result'], context_type="rag")
        
    except Exception as e:
        print(f"❌ RAG 오류: {e}")
        state["rag_result"] = f"RAG 검색 오류: {str(e)}"
        state["source_documents"] = []
    
    return state

def agent_node(state: AgentState):
    """Agent 분석 노드"""
    print("🤖 Agent 분석 시작...")

    # 🔥 복합 캐시 키 생성 (새로 추가된 부분)
    cached_result = cache.get(query, "agent")

    if cached_result:
        print("💾 Agent 캐시 히트!")
        state["agent_result"] = cached_result["result"]
        return state  # 🚀 Agent 실행 없이 바로 리턴!
    
    try:
        # RAG 결과를 포함한 입력 구성
        # RAG 검색 결과: {state["rag_result"]}
        # RAG 검색 결과: {texts}

        # 대화 기록을 문자열로 변환
        history_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in state["chat_history"]])

        agent_input = f"""
        현재 시각: {state["current_time"]}

        검색 결과: {texts}
        
        원래 사용자 질문: {query}

        대화 기록:
        {history_str}
        
        위 검색 결과를 바탕으로 필요한 분석이나 계산을 수행해주세요.
        만약 추가적인 데이터 분석이 필요하다면 analyze_data 도구를 사용하고,
        수학 계산이 필요하다면 calculator 도구를 사용해주세요.
        """
        
        response = agent_executor.invoke({"input": agent_input})
        state["agent_result"] = response['output']
        
        print("✅ Agent 분석 완료")

        cache.set(query=query, result=response['output'], context_type="agent")
        
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
        return "rag"

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
            "rag": "rag"
        }
    )
    workflow.add_edge("agent", "combine")
    workflow.add_edge("rag", "combine")
    workflow.add_edge("combine", END)

workflow_add_edge_2()

# 워크플로우 컴파일
app = workflow.compile()
def lang_graph_png():
    from IPython.display import Image, display

    try:
        #우리가 만든 app의 graph를 이미지로 그려서 display()로 감싸 출력하는 함수
        with open("LangGraph.png", "wb") as f:
            f.write(app.get_graph().draw_mermaid_png())
        # display(Image("LangGraph.png"))

    except Exception:
        print("랭그래프 png 실패")

# lang_graph_png()

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
            "current_time": "",
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

        # if cache.get(query, "rag"):
        #     print(f"💾 캐시 활용으로 토큰 절약!")  # 🔥 새로 추가
        # else:
        #     print(f"캐시 추가!!!")
        
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