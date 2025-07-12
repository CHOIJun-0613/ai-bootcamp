# server/core/google_llm.py

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from server.core.config import settings

# Google LLM 초기화
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0,
)

# Google Embeddings 초기화
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=settings.GOOGLE_API_KEY
)

# LLM에 Tool을 바인딩 (기존 llm.py 구조와 유사하게)
# 참고: Google LLM은 tool_choice를 직접 지원하지 않으므로, 필요 시 별도 로직 구현 필요
# 여기서는 기본적인 LLM 기능에 초점을 맞춥니다.
llm_with_tools = llm

# 간단한 체인 예시 (기존 구조와 호환성을 위해)
chain = (
    ChatPromptTemplate.from_template("{input}")
    | llm_with_tools
    | StrOutputParser()
)
