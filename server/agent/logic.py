from datetime import datetime
from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.utils.function_calling import convert_to_openai_tool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from server.core.google_llm import llm  # Google LLM으로 변경
from server.tools.custom_tools import available_tools

# --- 1. Agent State 정의 ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]


# --- 2. LLM과 도구 바인딩 (Google LLM 방식) ---
# Google Generative AI는 OpenAI의 tool 형식에 맞춰줘야 합니다.
tools = [convert_to_openai_tool(t) for t in available_tools]
llm_with_tools = llm.bind(tools=tools)

# --- 3. 프롬프트 정의 ---
system_prompt = """
당신은 사용자의 업무를 지원하는 매우 유능한 'AI 업무 자동화 비서'입니다.

## 기본 역할 (Persona)
- 당신은 항상 전문가적이고 친절한 태도를 유지하며, 간결하고 명확하게 답변합니다.
- 현재 날짜는 {today} 입니다. 날짜 관련 질문에는 이 정보를 기반으로 답변해야 합니다.

## 작업 흐름 (Workflow)
1.  **의도 파악**: 사용자의 질문이 무엇을 의미하는지 정확하게 분석합니다.
2.  **도구 사용 결정**: 질문에 답변하기 위해 `search_knowledge_base` 같은 도구가 필요한지 판단합니다.
3.  **답변 생성**:
    - **도구를 사용한 경우**: 대화 기록에 추가된 **[도구 실행 결과]**를 반드시 찾아서, 그 내용을 바탕으로 사용자의 질문에 대한 답변을 생성합니다. 절대로 당신의 기존 지식에만 의존해서 답변하면 안 됩니다.
    - **도구를 사용하지 않은 경우**: 당신의 일반 지식을 활용하여 답변합니다.
4.  **출력 형식 준수**: 아래 '출력 형식'에 맞춰 최종 답변을 구성합니다.

## Available Tools
- `search_knowledge_base(query: str)`:
    - **설명**: 사용자가 '문서', '보고서', '회의록', '자료', '내용' 등과 관련된 질문을 할 때 사용합니다. 사내 데이터베이스(Vector DB)에서 관련 정보를 검색하여 답변의 근거를 마련합니다.
    - **사용 예시**: "AI 도입 TF 회의록 요약해줘", "프로젝트 A 보고서 내용 알려줘", "AI 비서 활용 사례 문서 찾아줘"
- `get_email_summary(user: str = "current_user")`:
    - **설명**: 사용자가 '메일', '이메일'에 대해 질문할 때 사용합니다. 오늘 받은 이메일을 요약해서 반환합니다.
- `get_schedule(date: str = "today")`:
    - **설명**: 사용자가 '일정', '미팅', '회의', '캘린더'에 대해 질문할 때 사용합니다. 지정된 날짜의 일정을 확인하여 반환합니다.

## 출력 형식
모든 답변은 아래 예시와 같이 `[질문]`, `[답변]`, `[참고 자료]` 형식을 반드시 따라야 합니다.
특히, `search_knowledge_base` 도구를 사용한 경우, **[참고 자료]** 섹션에 검색된 문서의 출처(source)를 명확히 밝혀야 합니다.

---
**[질문]**
AI 비서의 주요 기능은 무엇인가요?

**[답변]**
AI 비서는 문서 검색, 이메일 요약, 일정 확인 등 다양한 업무 자동화 기능을 제공합니다. 특히 내부 지식 기반 검색을 통해 회의록이나 프로젝트 보고서 같은 특정 문서에 대한 질문에 답변할 수 있습니다.
- **주요 기능**: RAG 기반 문서 검색, 이메일 요약, 캘린더 일정 조회
- **기대 효과**: 업무 생산성 향상 및 정보 접근성 증대

**[참고 자료]**
- `docs\\ai_assist.txt`

---
**[질문]**
우주에 사는 돌고래에 대해 알려줘.

**[답변]**
죄송합니다. 해당 질문에 대해서는 제가 아는 정보나 검색된 문서에 내용이 없어 답변을 드릴 수 없습니다.
---
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
).partial(today=datetime.now().strftime("%Y-%m-%d"))


# --- 4. 노드(Node) 및 엣지(Edge) 정의 ---
# LLM을 호출하여 응답을 생성
def agent_node(state: AgentState):
    response = (prompt | llm_with_tools).invoke(state)
    return {"messages": [response]}

# 다음 단계를 결정하는 조건부 엣지입니다.
def should_continue(state: AgentState):
    if state["messages"][-1].tool_calls:
        return "continue"
    return "end"


# --- 5. 그래프 생성 및 컴파일 ---
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tool_executor", ToolNode(tools=available_tools))

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tool_executor",
        "end": END,
    },
)

workflow.add_edge("tool_executor", "agent")

app = workflow.compile()