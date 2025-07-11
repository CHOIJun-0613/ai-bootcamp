import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from server.agent.logic import invoke_agent

# .env 파일에서 환경 변수 로드
load_dotenv()

# FastAPI 앱 초기화
app = FastAPI(
    title="AI 업무 자동화 비서 백엔드",
    description="LangChain, LangGraph, FastAPI를 이용한 AI Agent 서버",
)

# 요청 본문 모델 정의
class ChatRequest(BaseModel):
    message: str

async def stream_agent_response(user_input: str):
    """
    동기적으로 동작하는 AI 에이전트를 비동기 환경에서 실행하고,
    그 최종 결과를 한 글자씩 스트리밍하여 타이핑 효과를 줍니다.
    """
    loop = asyncio.get_running_loop()
    
    # 동기 함수인 invoke_agent가 FastAPI의 비동기 루프를 막지 않도록 별도 스레드에서 실행합니다.
    final_response = await loop.run_in_executor(
        None, invoke_agent, user_input
    )
    
    # 최종 생성된 전체 답변을 한 글자씩 보내 스트리밍처럼 보이게 합니다.
    for char in final_response:
        yield char
        await asyncio.sleep(0.01) # 자연스러운 타이핑 효과를 위한 지연

@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    클라이언트에게 Agent의 응답을 스트리밍하는 엔드포인트입니다.
    """
    return StreamingResponse(
        stream_agent_response(request.message), media_type="text/plain"
    )