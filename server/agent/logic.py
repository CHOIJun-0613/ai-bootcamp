import operator
from typing import List, Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from server.core.llm import get_chat_model
from server.tools.custom_tools import available_tools

# --- 1. 상태(State) 정의 수정 ---
# messages 필드에 operator.add를 사용하여, 새로운 메시지가 항상 리스트에 추가되도록 설정합니다.
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# 모델과 도구 준비
llm = get_chat_model()
llm_with_tools = llm.bind_tools(available_tools)

# --- 2. 노드(Node) 로직 수정 ---
# 각 노드는 이제 전체 대화 기록이 아닌, '자신이 생성한 새 메시지'만 반환하면 됩니다.
# LangGraph가 알아서 상태(messages)에 추가해 줄 것입니다.

# Agent 노드
def agent_node(state: AgentState):
    """LLM을 호출하여 다음 메시지를 생성합니다."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 조건부 엣지 로직
def should_continue(state: AgentState):
    """마지막 메시지에 도구 호출이 있는지 확인하여 다음 단계를 결정합니다."""
    if state["messages"][-1].tool_calls:
        return "use_tool"
    else:
        return END

# Graph 생성
graph_builder = StateGraph(AgentState)

# Agent 노드 추가
graph_builder.add_node("agent", agent_node)

# ToolNode를 사용해 도구 실행 노드를 간단하게 추가
tool_node = ToolNode(available_tools)
graph_builder.add_node("tool_executor", tool_node)

# 그래프 흐름 정의
graph_builder.set_entry_point("agent")
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {"use_tool": "tool_executor", END: END}
)
graph_builder.add_edge("tool_executor", "agent")

# 그래프 컴파일
agent_graph = graph_builder.compile()

# 서비스 함수 (이 부분은 변경 없음)
def invoke_agent(query: str):
    system_prompt = """
    당신은 유능한 'AI 업무 자동화 비서'입니다.
    사용자의 요청을 명확하게 분석하고, 주어진 도구(Tool)들을 활용하여 단계적으로 문제를 해결해야 합니다.
    
    규칙:
    1. 사용자의 질문 의도를 파악하고, 가장 적절한 도구를 선택하세요.
    2. 도구 사용이 필요 없으면, 즉시 사용자에게 답변하세요.
    3. 도구(특히 search_knowledge_base)를 사용한 경우, 어떤 정보를 참고했는지 반드시 언급하며 답변을 생성하세요. (예: "회의록 문서를 참고한 결과...")
    4. 모든 답변은 한국어로, 친절하고 명확한 어조로 작성하세요.
    """
    
    initial_messages = [
        HumanMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    
    # 올바른 형식으로 invoke 함수 호출
    final_state = agent_graph.invoke({"messages": initial_messages})
    final_response = final_state["messages"][-1].content
    return final_response