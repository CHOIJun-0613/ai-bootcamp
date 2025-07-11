import streamlit as st
import requests
from datetime import datetime, timezone, timedelta

# --- Configuration and Helper Functions ---

# API 서버 주소
BACKEND_URL = "http://localhost:8001"
STREAM_ENDPOINT = f"{BACKEND_URL}/chat/stream"

# 한국 시간(KST)을 위한 timezone 객체 생성
KST = timezone(timedelta(hours=9))

def stream_response_generator(user_input: str):
    """
    백엔드 API에 스트리밍 요청을 보내고, 타임아웃을 포함한 예외를 처리
    """
    try:
        # 60초 타임아웃 설정
        with requests.post(
            STREAM_ENDPOINT, json={"message": user_input}, stream=True, timeout=60
        ) as response:
            response.raise_for_status()  # 200 OK가 아닌 경우 예외 발생
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                yield chunk
    # Timeout 예외를 별도로 처리
    except requests.exceptions.Timeout:
        error_message = "요청 시간이 초과되었습니다. (60초) 서버가 응답하는 데 시간이 더 필요하거나, 문제가 발생했을 수 있습니다."
        st.error(error_message)
        yield ""
    except requests.exceptions.RequestException as e:
        error_message = f"서버 연결에 실패했습니다: {e}"
        st.error(error_message)
        yield ""

# --- UI Layout ---

st.set_page_config(page_title="AI 업무 자동화 비서", page_icon="🤖", layout="wide")

# 세션 상태 변수 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "prompt_to_submit" not in st.session_state:
    st.session_state.prompt_to_submit = ""
if "prompt_to_process" not in st.session_state:
    st.session_state.prompt_to_process = ""

# 화면을 두 개 컬럼으로 분리
left_column, right_column = st.columns([3, 7])

# --- 좌측 컬럼 (사용자 입력) ---
with left_column:
    st.subheader("🤖 질문하기")
    st.markdown("##### 예시 질문")
    st.markdown('<p style="font-size: 14px; color: #888888;">오늘 오후 3시에 어떤 일정이 있어?</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #888888;">7월10일 진행한 \'AI 도입 TF\' 회의록 요약해줘.</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #888888;">프로젝트 A 보고서 초안으로 발표자료 목차 만들어줘.</p>', unsafe_allow_html=True)

    def handle_submit():
        st.session_state.prompt_to_process = st.session_state.prompt_to_submit
        st.session_state.prompt_to_submit = ""

    with st.form("chat_form", border=False):
        st.text_area("이곳에 질문을 입력하세요:", height=150, key="prompt_to_submit")
        st.form_submit_button("전송", on_click=handle_submit)


# --- 우측 컬럼 (결과 출력) ---
with right_column:
    st.title("AI 업무 자동화 비서")
    st.caption("LangChain, LangGraph, RAG, FastAPI, Streamlit으로 구현한 AI 에이전트")
    st.divider()

    new_chat_container = st.container()
    past_chat_container = st.container()

    if st.session_state.prompt_to_process:
        prompt = st.session_state.prompt_to_process
        with new_chat_container:
            request_time = datetime.now(KST)
            with st.chat_message("user"):
                st.markdown(prompt)
                st.markdown(f'<p style="font-size: 12px; color: #888888; text-align: right;">요청: {request_time.strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)

            with st.chat_message("assistant"):
                with st.spinner("AI 비서가 분석 중입니다..."):
                    placeholder = st.empty()
                    full_response = ""
                    for chunk in stream_response_generator(prompt):
                        full_response += chunk
                        placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                    response = full_response
                
                response_time = datetime.now(KST)
                st.markdown(f'<p style="font-size: 12px; color: #888888; text-align: right;">완료: {response_time.strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)

        # ✨ 해결책: 저장 순서를 [질문] -> [답변] 순으로 수정합니다.
        # 이렇게 하면 session_state.messages 리스트는 [답변, 질문, 이전 답변, 이전 질문, ...] 순이 됩니다.
        st.session_state.messages.insert(0, {"role": "user", "content": prompt, "time": request_time})
        st.session_state.messages.insert(0, {"role": "assistant", "content": response, "time": response_time})
        
        st.session_state.prompt_to_process = ""
        st.rerun()

    with past_chat_container:
        # 저장 순서에 맞춰 화면 표시 로직을 유지합니다.
        for i in range(0, len(st.session_state.messages), 2):
            if i + 1 < len(st.session_state.messages):
                assistant_msg = st.session_state.messages[i]
                user_msg = st.session_state.messages[i+1]
                
                with st.chat_message(user_msg["role"]):
                    st.markdown(user_msg["content"])
                    st.markdown(f'<p style="font-size: 12px; color: #888888; text-align: right;">요청: {user_msg["time"].strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)
                with st.chat_message(assistant_msg["role"]):
                    st.markdown(assistant_msg["content"])
                    st.markdown(f'<p style="font-size: 12px; color: #888888; text-align: right;">완료: {assistant_msg["time"].strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)