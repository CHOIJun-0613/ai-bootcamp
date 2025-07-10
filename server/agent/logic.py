from typing import List, TypedDict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from server.core.llm import get_chat_model
from server.tools.custom_tools import available_tools

# 1. Agent의 상태(State) 정의
class AgentState(TypedDict):
    messages: List[BaseMessage]

# 2. 필요한 모델과 도구 준비
llm = get_chat_model()
# LLM에 도구 정보를 바인딩하여, LLM이 도구를 호출할 수 있도록 함
llm_with_tools = llm.bind_tools(available_tools)
tool_executor = ToolExecutor(available_tools)

# 3. Graph의 노드(Node) 정의
# Agent 노드: LLM을 호출하여 다음에 할 일을 결정 (도구 사용 or 사용자에게 답변)
def agent_node(state: AgentState):
    """LLM을 호출하여 응답을 생성하고, 도구 사용 여부를 결정합니다."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Tool 노드: Agent가 호출하기로 결정한 도구를 실행
def tool_node(state: AgentState):
    """마지막 AI 메시지에서 도구 호출을 찾아 실행하고 결과를 반환합니다."""
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls
    
    tool_outputs = []
    for tool_call in tool_calls:
        # tool_executor.invoke는 tool_call 딕셔너리를 받아 해당 함수를 실행
        output = tool_executor.invoke(tool_call)
        tool_outputs.append(
            ToolMessage(content=str(output), tool_call_id=tool_call["id"])
        )
    
    return {"messages": tool_outputs}

# 4. 조건부 엣지(Edge) 로직 정의
def should_continue(state: AgentState):
    """도구를 더 호출할지, 아니면 끝낼지 결정합니다."""
    if state["messages"][-1].tool_calls:
        # LLM이 도구 호출을 생성했다면, tool_node로 이동
        return "use_tool"
    else:
        # 더 이상 도구 호출이 없다면, 종료
        return END

# 5. Graph 생성 및 연결
graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tool_executor", tool_node)

# 그래프 흐름 정의
graph_builder.set_entry_point("agent")
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "use_tool": "tool_executor",
        END: END
    }
)
graph_builder.add_edge("tool_executor", "agent")

# 그래프 컴파일
agent_graph = graph_builder.compile()

# 6. 서비스 함수 생성
def invoke_agent(query: str):
    """사용자 입력을 받아 Agent를 실행하고 최종 응답을 반환합니다."""
    
    # 프롬프트 엔지니어링: 역할 부여 (Role-playing)
    system_prompt = """
    당신은 유능한 'AI 업무 자동화 비서'입니다.
    사용자의 요청을 명확하게 분석하고, 주어진 도구(Tool)들을 활용하여 단계적으로 문제를 해결해야 합니다.
    
    규칙:
    1. 사용자의 질문 의도를 파악하고, 가장 적절한 도구를 선택하세요.
    2. 도구 사용이 필요 없으면, 즉시 사용자에게 답변하세요.
    3. 도구(특히 search_knowledge_base)를 사용한 경우, 어떤 정보를 참고했는지 반드시 언급하며 답변을 생성하세요. (예: "회의록 문서를 참고한 결과...")
    4. 모든 답변은 한국어로, 친절하고 명확한 어조로 작성하세요.
    """
    
    initial_state = {
        "messages": [
            HumanMessage(content=query),
            # 시스템 프롬프트를 HumanMessage 앞에 두거나, llm.invoke의 system 인자로 전달할 수 있습니다.
            # 여기서는 명시적으로 리스트의 일부로 포함합니다.
            AIMessage(content=system_prompt) # LangGraph는 보통 메시지 순서를 유지하므로, 시스템 프롬프트의 위치를 조정할 수 있습니다.
                                             # 더 안정적인 방법은 LLM 호출 시 system 인자를 사용하는 것입니다.
                                             # 여기서는 데모를 위해 메시지 리스트에 포함합니다.
        ]
    }
    
    # 더 나은 프롬프트 전략: 시스템 프롬프트를 HumanMessage 앞에 두기
    final_input_state = {
        "messages": [
            HumanMessage(content=system_prompt), # 시스템 역할을 먼저 부여
            HumanMessage(content=query)
        ]
    }

    # Graph 실행 (Stream: 중간 과정을 모두 보여줌)
    final_state = agent_graph.invoke(final_input_state)
    
    # 최종 응답은 마지막 AI 메시지
    final_response = final_state["messages"][-1].content
    return final_response