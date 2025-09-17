# services/rag_service.py
import os
from langchain_community.chat_models import ChatOpenAI
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

# --- Global variable for the LLM -- -
llm = None

def initialize_llm():
    """
    Initializes the LLM.
    This should be called once at application startup.
    """
    global llm

    # --- Load environment variables ---
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    df = pd.read_csv("C:\\datatide_workspaceN\\DataTide_back\\services\\read_sql_1.csv")  # CSV 파일을 읽습니다.
    # --- Initialize LLM ---
    llm = create_pandas_dataframe_agent(
    ChatOpenAI(model="gpt-4.1-mini", temperature=0),
    df,
    verbose=False,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    allow_dangerous_code=True,
)
    print("LLM is ready.")

def get_llm_response(query: str) -> dict:
    """
    Gets a response from the LLM for a given query.
    """
    global llm
    if not llm:
        return {"answer": "LLM이 아직 준비되지 않았습니다. 잠시 후 다시 시도해주세요."}

    prompt = f"""
        품목에는 대상이, 날짜는 해당 기록의 날짜가, 생산량, 수입량, 판매량을 행 기준으로 파악하면 돼.
        만약 해당 내용에 대한 질문이 아니라면 저희는 품목당 날짜에 따른 생산, 수입, 판매량만 알려주는 챗봇이라 모른다고 답해줘.
        단위는 톤입니다. 대답은 친절히.
        만약 답을 찾을 수 없다면, 모른다고 답하세요.
        필요하다면 다음의 대화 기록을 참고하여 질문에 답변하세요.


        질문: {query}
    """
    
    try:
        response = llm.invoke({"input": prompt})
        print(response)
        return {"answer": response['output']}
    except Exception as e:
        print(f"Error during LLM query: {e}")
        return {"error": "LLM에서 답변을 가져오는 데 실패했습니다."}