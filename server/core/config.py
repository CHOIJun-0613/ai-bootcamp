# core/config.py

import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

class Settings:
    AOAI_ENDPOINT: str = os.getenv("AOAI_ENDPOINT")
    AOAI_API_KEY: str = os.getenv("AOAI_API_KEY")
    AOAI_API_VERSION: str = os.getenv("AOAI_API_VERSION", "2024-05-01-preview")
    AOAI_GPT4O_MINI: str = os.getenv("AOAI_DEPLOY_GPT4O_MINI")
    AOAI_GPT4O: str = os.getenv("AOAI_DEPLOY_GPT4O")
    AOAI_EMBED_LARGE: str = os.getenv("AOAI_DEPLOY_EMBED_3_LARGE")

    # Vector DB Path
    CHROMA_PATH: str = "db"

settings = Settings()