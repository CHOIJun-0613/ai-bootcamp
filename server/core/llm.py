from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from .config import settings

def get_chat_model():
    """GPT-4o-mini 채팅 모델"""
    return AzureChatOpenAI(
        azure_endpoint=settings.AOAI_ENDPOINT,
        api_key=settings.AOAI_API_KEY,
        api_version=settings.AOAI_API_VERSION,
        azure_deployment=settings.AOAI_GPT4O_MINI,
        temperature=0,
        streaming=True
    )

def get_embedding_model():
    """text-embedding-3-large 임베딩 모델"""
    return AzureOpenAIEmbeddings(
        azure_endpoint=settings.AOAI_ENDPOINT,
        api_key=settings.AOAI_API_KEY,
        api_version=settings.AOAI_API_VERSION,
        azure_deployment=settings.AOAI_EMBED_LARGE
    )