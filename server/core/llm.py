from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from server.core.config import settings

"""GPT-4o-mini 채팅 모델"""
llm = AzureChatOpenAI(
        azure_endpoint=settings.AOAI_ENDPOINT,
        api_key=settings.AOAI_API_KEY,
        api_version=settings.AOAI_API_VERSION,
        azure_deployment=settings.AOAI_GPT4O_MINI,
        temperature=0,
        streaming=True
)
def get_chat_model():
    return llm

"""text-embedding-3-large 임베딩 모델"""
embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=settings.AOAI_ENDPOINT,
        api_key=settings.AOAI_API_KEY,
        api_version=settings.AOAI_API_VERSION,
        azure_deployment=settings.AOAI_EMBED_LARGE
    )
def get_embedding_model():
    return embeddings