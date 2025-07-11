from graphviz import Digraph

# 그래프 객체 생성 (Service Architecture)
dot = Digraph('AI_Service_Architecture', comment='Service Architecture Diagram')
dot.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='1.2')

# --- 폰트 및 전체 타이틀 설정 (한글 깨짐 방지) ---
dot.attr('graph', fontname='Malgun Gothic', label='AI 업무 자동화 비서 - 서비스 아키텍처 다이어그램', fontsize='20')
dot.attr('node', fontname='Malgun Gothic', shape='box', style='rounded,filled')
dot.attr('edge', fontname='Malgun Gothic', fontsize='10')

# --- 1. 사용자 인터페이스 (Frontend) ---
with dot.subgraph(name='cluster_frontend') as c:
    c.attr(label='사용자 인터페이스 (Frontend)', style='filled', color='azure')
    c.node('streamlit', 'Streamlit UI\n(사용자 질문/답변 표시)', fillcolor='azure2')

# --- 2. 백엔드 서버 (Backend) ---
with dot.subgraph(name='cluster_backend') as c:
    c.attr(label='백엔드 서버 (Backend)', style='filled', color='lightyellow')
    c.node('fastapi', 'FastAPI Server\n(API Gateway & Streaming)', fillcolor='yellow')

# --- 3. AI 코어 로직 (AI Core) ---
with dot.subgraph(name='cluster_ai_core') as c:
    c.attr(label='AI 코어 로직 (AI Core)', style='filled', color='lightgoldenrodyellow')
    c.node('langgraph', 'LangGraph Agent\n(상태 기반 워크플로우)', fillcolor='goldenrod1')
    c.node('tools', 'Custom Tools\n(지식 검색, 일정 확인 등)', shape='cylinder', fillcolor='honeydew2')
    c.node('langchain', 'LangChain\n(LLM 연동, 프롬프트 관리)', fillcolor='goldenrod2')

# --- 4. 외부 서비스 & 데이터 (External & Data) ---
with dot.subgraph(name='cluster_external') as c:
    c.attr(label='외부 서비스 & 데이터 (External & Data)', style='filled', color='lightpink')
    c.node('azure_openai', 'Azure OpenAI Service\n- GPT-4o-mini (Chat)\n- text-embedding-3 (Embedding)', shape='cloud', fillcolor='pink')
    c.node('chromadb', 'ChromaDB\n(Vector Store)', shape='cylinder', fillcolor='lightcoral')
    c.node('docs', '사내 문서\n(.txt, .md 등)', shape='folder', fillcolor='lightsalmon')

# --- 데이터 흐름 및 상호작용 연결 ---

# 실시간 처리 흐름 (Runtime Flow)
dot.edge('streamlit', 'fastapi', label='1. 실시간 API 요청 (HTTP/WebSocket)')
dot.edge('fastapi', 'langgraph', label='2. Agent 실행 요청')
dot.edge('langgraph', 'langchain', label='3. LLM 호출/프롬프트 실행')
dot.edge('langgraph', 'tools', label='4. Tool 사용 결정 및 실행')
dot.edge('tools', 'langgraph', label='5. Tool 실행 결과 반환')
dot.edge('langchain', 'azure_openai', label='6. LLM API 호출\n(의사결정/답변 생성)')
dot.edge('tools', 'chromadb', label='7. 벡터 검색 (RAG)')

# 데이터 수집 흐름 (Ingestion Flow - Dashed Line)
dot.edge('docs', 'azure_openai', label='문서 임베딩', style='dashed', arrowhead='normal', dir='forward')
dot.edge('azure_openai', 'chromadb', label='벡터 저장', style='dashed', arrowhead='normal', dir='forward')


# 파일 경로 설정 및 저장
file_path = 'service_architecture_diagram.png'
dot.render(file_path.replace('.png', ''), format='png', cleanup=True)

print(f"서비스 아키텍처 다이어그램이 '{file_path}' 파일로 저장되었습니다.")