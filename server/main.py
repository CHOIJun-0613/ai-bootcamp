import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드 (OPENAI_API_KEY 등)
load_dotenv()

# FastAPI 앱 초기화
app = FastAPI(
    title="AI Bootcamp Backend",
    description="LangChain과 FastAPI를 이용한 스트리밍 AI 서버",
)

# LangChain 모델 및 체인 설정
# 실제 프로젝트에서는 RAG, LangGraph 등 더 복잡한 체인을 사용하게 됩니다.
# 여기서는 스트리밍 시연을 위해 간단한 체인을 구성합니다.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI assistant. Answer the user's questions."),
        ("human", "{user_input}"),
    ]
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm | StrOutputParser()

# 요청 본문 모델 정의
class ChatRequest(BaseModel):
    message: str

async def stream_ai_response(user_input: str):
    """
    LangChain의 astream()을 사용하여 AI 응답을 비동기적으로 스트리밍합니다.
    """
    # astream은 응답의 각 청크(chunk)를 비동기적으로 반환하는 제너레이터입니다.
    async for chunk in chain.astream({"user_input": user_input}):
        yield chunk
        # 실제 응답처럼 보이게 하기 위해 약간의 딜레이를 추가합니다.
        await asyncio.sleep(0.01)

@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    클라이언트에게 AI 응답을 스트리밍하는 엔드포인트입니다.
    """
    return StreamingResponse(
        stream_ai_response(request.message), media_type="text/plain"
    )