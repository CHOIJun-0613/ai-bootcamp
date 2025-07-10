from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.models.chat import ChatRequest
from server.agent.logic import invoke_agent

app = FastAPI(
    title="AI Secretary Agent API",
    description="LangGraph 기반의 AI 업무 자동화 비서 Agent API 입니다.",
    version="1.0.0"
)

# CORS 설정 (Streamlit 로컬 개발 환경과의 통신을 위해 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 프로덕션에서는 특정 도메인만 허용해야 합니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", summary="AI Agent와 대화")
def chat_with_agent(request: ChatRequest):
    """
    사용자의 질문을 받아 AI Agent를 실행하고 답변을 반환합니다.
    """
    try:
        response = invoke_agent(request.query)
        return {"response": response}
    except Exception as e:
        return {"error": f"Agent 실행 중 오류 발생: {str(e)}"}

# 서버 상태 확인을 위한 루트 엔드포인트
@app.get("/", summary="API 상태 확인")
def read_root():
    return {"status": "AI Agent API is running"}