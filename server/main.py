from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from server.agent.logic import app as agent_graph

app = FastAPI(
    title="AI 업무 자동화 비서 API",
    description="LangGraph와 FastAPI를 이용한 AI 에이전트 API 서버입니다.",
    version="1.0.0",
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def get_messages(req: ChatRequest) -> dict:
    return {"messages": [HumanMessage(content=req.message)]}


@app.post("/chat/stream")
async def stream(
    input_data: Annotated[dict, Depends(get_messages)],
):
    """AI 로직의 중첩된 데이터 구조를 올바르게 처리하는 최종 API"""
    stream = agent_graph.astream(input_data)

    async def event_stream():
        last_sent_content = ""
        async for chunk in stream:
            if "agent" in chunk:
                # 'agent' 키 안에서 'messages'를 가져옴...
                agent_output = chunk["agent"]
                messages = agent_output.get("messages")
                
                if not messages:
                    continue

                last_message = messages[-1]

                if isinstance(last_message, AIMessage) and last_message.content:
                    if last_message.content != last_sent_content:
                        new_part = last_message.content[len(last_sent_content):]
                        last_sent_content = last_message.content
                        yield new_part

    return StreamingResponse(event_stream(), media_type="text/plain")


@app.get("/")
async def read_root():
    return {"message": "AI Agent Server is running."}