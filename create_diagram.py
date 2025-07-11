# create_diagram.py

from graphviz import Digraph

# 그래프 객체 생성
dot = Digraph('AI_Agent_User_Flow', comment='AI Agent User Flow Diagram')
from graphviz import Digraph

# 그래프 객체를 생성합니다.
# rankdir='TB'는 위에서 아래로 흐르는 Top-to-Bottom 레이아웃을 의미합니다.
dot = Digraph('AI_Agent_User_Flow', comment='AI Agent User Flow Diagram')

# ----------------- [수정된 부분 시작] -----------------
# 그래프 전체, 노드, 엣지에 한글 폰트('맑은 고딕')를 설정합니다.
# 윈도우 환경에서는 'Malgun Gothic'을 사용합니다.
dot.attr('graph', fontname='Malgun Gothic')
dot.attr('node', fontname='Malgun Gothic')
dot.attr('edge', fontname='Malgun Gothic')
# ----------------- [수정된 부분 끝] -------------------

dot.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='1')

# 노드의 기본 스타일을 설정합니다.
dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
# 엣지(화살표)의 기본 스타일을 설정합니다.
dot.attr('edge', fontsize='10')

# 다이어그램에 사용될 각 단계 (노드)를 정의합니다.
# 각 노드는 프로젝트의 특정 부분이나 행위를 나타냅니다.
dot.node('user', '사용자\n(User)', shape='ellipse', fillcolor='lightgrey')
dot.node('frontend', 'Streamlit UI\n(app/main_app.py)', fillcolor='azure')
dot.node('backend', 'FastAPI Backend\n(server/main.py)', fillcolor='lightyellow')
dot.node('agent', 'LangGraph Agent\n(server/agent/logic.py)', fillcolor='lightgoldenrodyellow')
dot.node('decision', 'LLM 의사결정\n(Tool 사용 or 답변)', shape='diamond', fillcolor='lightpink')
dot.node('tools', 'Tool 실행\n(server/tools/custom_tools.py)\n- 지식 검색, 일정 확인 등', shape='cylinder', fillcolor='honeydew')
dot.node('final_answer', '최종 답변 생성', fillcolor='palegreen')
dot.node('display', '실시간 답변 표시', fillcolor='azure')

# 각 단계를 연결하는 흐름 (엣지)을 정의합니다.
# label은 각 단계에서 어떤 일이 일어나는지 설명합니다.
dot.edge('user', 'frontend', label='1. 질문 입력')
dot.edge('frontend', 'backend', label='2. API 요청 (/chat/stream)')
dot.edge('backend', 'agent', label='3. Agent 호출')
dot.edge('agent', 'decision', label='4. LLM에 판단 요청')
dot.edge('decision', 'tools', label='5a. Tool 사용 결정')
dot.edge('tools', 'agent', label='6. Tool 실행 결과 반환 (Loop)')
dot.edge('decision', 'final_answer', label='5b. 최종 답변 결정')
dot.edge('final_answer', 'backend', label='7. 답변 스트리밍 생성')
dot.edge('backend', 'frontend', label='8. StreamingResponse 전송')
dot.edge('frontend', 'display', label='9. UI에 답변 표시')
dot.edge('display', 'user', label='10. 답변 확인')

# 'user_flow_diagram.png' 이름으로 이미지 파일을 저장합니다.
file_path = 'user_flow_diagram.png'
# render 함수는 실제 파일을 생성하는 역할을 합니다.
dot.render(file_path.replace('.png', ''), format='png', cleanup=True)

print(f"다이어그램이 '{file_path}' 파일로 성공적으로 저장되었습니다.")

