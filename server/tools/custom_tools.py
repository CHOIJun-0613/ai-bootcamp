from langchain.tools import tool
from langchain_community.vectorstores import Chroma
from core.llm import get_embedding_model
from core.config import settings
import datetime

# --- RAG Tool ---
@tool
def search_knowledge_base(query: str) -> str:
    """
    "사용자가 '문서', '보고서', '회의록' 등과 관련된 질문을 할 때 사용합니다.
    사내 데이터베이스(Vector DB)에서 관련 정보를 검색하여 답변의 근거를 마련합니다."
    
    Args:
        query (str): 사용자의 원본 질문 또는 검색에 최적화된 키워드.

    Returns:
        str: 검색된 문서의 내용.
    """
    embedding_model = get_embedding_model()
    vectorstore = Chroma(persist_directory=settings.CHROMA_PATH, embedding_function=embedding_model)
    
    # k=3은 가장 유사한 3개의 청크를 가져오라는 의미
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    docs = retriever.invoke(query)
    
    # 검색된 문서 내용을 하나의 문자열로 합쳐서 반환
    return "\n\n".join([doc.page_content for doc in docs])

# --- Dummy Tools for Demo ---
@tool
def get_email_summary(user: str = "current_user") -> str:
    """
    "사용자가 '메일', '이메일'에 대해 질문할 때 사용합니다.
    오늘 받은 이메일을 요약해서 반환합니다."
    
    Args:
        user (str): 요약할 이메일의 사용자. 기본값은 현재 로그인한 사용자입니다.

    Returns:
        str: 이메일 요약 정보.
    """
    # 실제 구현에서는 MS Graph API, Gmail API 등을 연동해야 합니다.
    # 여기서는 데모를 위해 고정된 값을 반환합니다.
    return f"{user}님, 오늘 3개의 새 이메일이 있습니다. 주요 내용은 '프로젝트 A 주간 보고 요청'과 '2025년 하반기 워크샵 일정 안내' 입니다."

@tool
def get_schedule(date: str = "today") -> str:
    """
    "사용자가 '일정', '미팅', '회의', '캘린더'에 대해 질문할 때 사용합니다.
    지정된 날짜의 일정을 확인하여 반환합니다."

    Args:
        date (str): 조회할 날짜. 기본값은 'today' 입니다.

    Returns:
        str: 해당 날짜의 일정 정보.
    """
    # 실제 구현에서는 Google Calendar API, Outlook Calendar API 등과 연동해야 합니다.
    # 여기서는 데모를 위해 고정된 값을 반환합니다.
    today = datetime.date.today().strftime("%Y년 %m월 %d일")
    if date == "today":
        return f"오늘({today})의 주요 일정은 다음과 같습니다:\n- 14:00 ~ 15:00: AI Agent 개발 과제 중간 점검 회의\n- 17:00: 팀 저녁 식사"
    else:
        return f"{date}에는 특별한 일정이 없습니다."

# 모든 도구를 리스트로 묶어서 내보내기
available_tools = [search_knowledge_base, get_email_summary, get_schedule]