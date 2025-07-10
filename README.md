# ai-bootcamp
ai-bootcamp

# AI 업무 자동화 비서 프로젝트

LangChain, LangGraph, RAG, FastAPI, Streamlit을 활용하여 개발한 AI 업무 자동화 비서입니다.

## 🚀 프로젝트 실행 방법

### 애플리케이션 실행
애플리케이션은 **3단계**로 실행해야 합니다. 각 단계마다 **새로운 터미널**을 사용하세요.

#### **1단계: Vector DB 생성 (최초 1회만 실행)**
`docs` 폴더의 문서를 읽어 `db` 디렉토리에 데이터베이스를 생성합니다.
python -m server.scripts.ingest_data.py

#### **2단계: FastAPI 백엔드 서버 실행**
AI Agent 로직을 처리하는 API 서버를 실행합니다.
uvicorn server.main:app --host 0.0.0.0 --port 8001 --reload

#### **3단계: Streamlit 프론트엔드 실행**
사용자 인터페이스(UI)를 실행합니다.
streamlit run app/main_app.py

실행 후, 터미널에 나타나는 URL(보통 http://localhost:8501)에 접속하면 AI 비서와 대화할 수 있습니다.