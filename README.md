### 프로젝트 개요

이 프로젝트는 **LangChain, LangGraph, RAG (Retrieval-Augmented Generation), FastAPI, Streamlit**을 활용하여 개발된 **"AI 업무 자동화 비서"** 애플리케이션입니다. 사용자가 자연어로 질문하면, AI 에이전트가 자체적으로 판단하여 필요한 도구(Tool)를 사용하고, 사내 문서 검색이나 일정 확인 등을 수행하여 답변을 생성해주는 시스템입니다.

---

### 프로젝트 구조 (Architecture)

이 프로젝트는 크게 **프론트엔드(Frontend)**와 **백엔드(Backend)**로 나뉘어 있으며, 각 서버는 독립적으로 실행됩니다.

1.  **프론트엔드 (UI)**
    * **담당 파일**: `app/main_app.py`
    * **역할**: 사용자 인터페이스(UI)를 제공합니다. 사용자가 질문을 입력하고 AI 비서의 답변을 실시간으로 확인할 수 있는 웹 화면을 담당합니다.
    * **동작**:
        * 사용자가 질문을 입력하고 '전송' 버튼을 누르면, 백엔드 FastAPI 서버의 `/chat/stream` 엔드포인트로 요청을 보냅니다.
        * 백엔드로부터 스트리밍 형태로 전달되는 답변을 받아서 화면에 한 글자씩 타이핑되는 것처럼 실시간으로 출력합니다.
        * 전체 대화 기록은 세션(Session)에 저장하여 사용자가 이전 대화 내용을 볼 수 있도록 합니다.

2.  **백엔드 (AI Logic & API)**
    * **담당 파일**: `server/main.py`, `server/agent/logic.py` 등 `server` 디렉토리 하위 파일들
    * **역할**: AI 에이전트의 핵심 로직을 처리하고, 프론트엔드에 API를 제공합니다.
    * **동작**:
        * FastAPI를 사용하여 `/chat/stream`이라는 API 엔드포인트를 제공합니다.
        * 사용자의 질문(`message`)을 받으면, `invoke_agent` 함수를 호출하여 LangGraph로 구현된 AI 에이전트를 실행시킵니다.
        * AI 에이전트가 생성한 최종 답변을 스트리밍 응답(StreamingResponse) 형태로 프론트엔드에 전달합니다.

---

### 핵심 기술 스택 (Tech Stack)

* **FastAPI**: 백엔드 API 서버를 구축하는 데 사용되었습니다.
* **Streamlit**: 데이터 과학 및 AI 프로젝트를 위한 간단하고 빠른 웹 UI를 제작하는 데 사용되었습니다.
* **LangChain & LangGraph**: AI 에이전트의 로직을 구성하는 핵심 프레임워크입니다.
    * **LangChain**: LLM(거대 언어 모델)을 외부 도구 및 데이터와 쉽게 연결할 수 있도록 돕습니다.
    * **LangGraph**: 상태(State)를 기반으로 LLM과 도구들을 노드(Node)로 연결하여, 복잡한 멀티-에이전트 시스템이나 조건부 로직을 구현할 수 있게 합니다. 이 프로젝트에서는 사용자의 질문에 따라 '도구 사용' 또는 '최종 답변'으로 분기하는 로직을 `AgentState`와 `should_continue` 함수로 구현했습니다.
* **RAG (Retrieval-Augmented Generation)**:
    * **담당 파일**: `server/scripts/ingest_data.py`, `server/tools/custom_tools.py`
    * **설명**: 사용자의 질문과 관련된 정보를 **Vector DB**에서 검색한 후, 그 정보를 바탕으로 LLM이 답변을 생성하게 하는 기술입니다. 이를 통해 LLM이 알지 못하는 최신 정보나 내부 문서에 대해서도 답변할 수 있게 됩니다.
    * **구현**:
        1.  `ingest_data.py`: `docs` 폴더의 텍스트 파일들을 불러와(`DirectoryLoader`) 의미 단위로 잘게 나누고(`RecursiveCharacterTextSplitter`), **AzureOpenAIEmbeddings** 모델을 사용해 벡터로 변환한 뒤 **ChromaDB**에 저장합니다.
        2.  `custom_tools.py`: `search_knowledge_base`라는 도구를 통해 사용자의 질문이 들어오면 ChromaDB에서 가장 유사한 문서 조각(chunk) 3개를 검색하여 그 내용을 반환합니다.
* **Azure OpenAI Service**:
    * **담당 파일**: `server/core/llm.py`, `server/core/config.py`
    * **설명**: 채팅 모델(`GPT-4o-mini`)과 임베딩 모델(`text-embedding-3-large`)을 제공하는 클라우드 서비스입니다. `settings` 객체를 통해 API 엔드포인트, 키 등의 설정을 관리합니다.

---

### AI 에이전트 동작 원리

AI 에이전트는 **LangGraph**로 설계되었으며, 다음과 같은 흐름으로 동작합니다.

1.  **시작 (Entry Point)**: 사용자의 질문이 `agent_node`로 전달됩니다.
2.  **`agent_node` (LLM 호출)**:
    * 시스템 프롬프트("당신은 유능한 'AI 업무 자동화 비서'입니다...")와 사용자 질문을 함께 **GPT-4o-mini** 모델(`llm_with_tools`)에 전달합니다.
    * LLM은 질문 의도를 파악하고, `available_tools`에 정의된 도구들(`search_knowledge_base`, `get_email_summary`, `get_schedule`) 중 어떤 것을 사용해야 할지, 또는 그냥 답변해야 할지를 결정합니다.
3.  **`should_continue` (조건부 분기)**:
    * LLM의 답변에 **도구 호출(tool\_calls)**이 포함되어 있으면, `tool_executor` 노드로 이동합니다.
    * 도구 호출이 없으면, 그대로 **종료(END)**하고 최종 답변을 반환합니다.
4.  **`tool_executor` (도구 실행)**:
    * LLM이 요청한 도구(예: `search_knowledge_base('AI 비서 활용 사례')`)를 실제로 실행합니다.
    * 도구 실행 결과를 다시 `agent_node`로 전달합니다.
5.  **`agent_node` (재호출)**:
    * 이제 LLM은 **도구 실행 결과**까지 참고하여 사용자에게 보여줄 최종 답변을 생성합니다.
    * "회의록 문서를 참고한 결과..." 와 같이 어떤 근거로 답변했는지 명시하도록 프롬프트에 지시되어 있습니다.
6.  **종료**: 생성된 최종 답변이 사용자에게 전달됩니다.

---

### 프로젝트 실행 방법

`README.md` 파일에 설명된 대로, 3개의 터미널에서 각 단계를 순서대로 실행해야 합니다.

1.  **Vector DB 생성**: `python -m server.scripts.ingest_data` (최초 1회 실행)
    * `docs` 폴더의 문서들을(`ai_assist.txt`, `회의록_20250710.txt` 등) 읽어 `db` 폴더에 벡터 데이터베이스를 생성합니다.
2.  **백엔드 서버 실행**: `uvicorn server.main:app --host 0.0.0.0 --port 8001 --reload`
    * FastAPI로 구현된 AI 로직 서버를 8001 포트로 실행합니다.
3.  **프론트엔드 실행**: `streamlit run app/main_app.py`
    * Streamlit으로 만든 UI 서버를 실행하면, 웹 브라우저에서 AI 비서와 대화할 수 있습니다.

