# app/main_app.py

import streamlit as st
import requests
from datetime import datetime, timezone, timedelta

# --- Configuration and Helper Functions ---

# API 서버 주소
BACKEND_URL = "http://localhost:8001"
STREAM_ENDPOINT = f"{BACKEND_URL}/chat/stream"

# ✅ 3. 한국 시간(KST)을 위한 timezone 객체 생성
KST = timezone(timedelta(hours=9))

def stream_response_generator(user_input: str):
    """
    백엔드 API에 스트리밍 요청을 보내고, 받은 청크를 yield합니다.
    """
    try:
        with requests.post(
            STREAM_ENDPOINT, json={"message": user_input}, stream=True, timeout=600
        ) as response:
            response.raise_for_status()  # 오류 발생 시 예외를 발생시킴
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                yield chunk
    except requests.exceptions.RequestException as e:
        error_message = f"서버 연결에 실패했습니다: {e}"
        st.error(error_message)
        yield ""

# --- UI Layout ---

st.set_page_config(page_title="AI 업무 자동화 비서", page_icon="🤖", layout="wide")

# 세션 상태 초기화 (메시지 구조에 'time' 추가)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 화면을 2:8 비율의 두 개 컬럼으로 분리
left_column, right_column = st.columns([2, 8])

# --- 좌측 컬럼 (사용자 입력) ---
with left_column:
    st.subheader("🤖 질문하기")
    st.markdown("##### 예시 질문")
    st.markdown('<p style="font-size: 14px; color: #888888;">오늘 오후 3시에 어떤 일정이 있어?</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #888888;">어제 진행한 \'AI 도입 TF\' 회의록 요약해줘.</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #888888;">프로젝트 A 보고서 초안으로 발표자료 목차 만들어줘.</p>', unsafe_allow_html=True)

    # ✅ 1. st.rerun()을 통해 전송 후 입력창이 자동으로 비워집니다.
    with st.form("chat_form", border=False):
        prompt = st.text_area("이곳에 질문을 입력하세요:", height=150, key="chat_input")
        submitted = st.form_submit_button("전송")

# --- 우측 컬럼 (결과 출력) ---
with right_column:
    st.title("AI 업무 자동화 비서")
    st.caption("LangChain, LangGraph, RAG, FastAPI, Streamlit으로 구현한 AI 에이전트")
    st.divider()

    # '실시간 대화'와 '과거 기록'을 위한 컨테이너 분리
    new_chat_container = st.container()
    past_chat_container = st.container()

    # 새 질문 제출 시 처리 로직
    if submitted and prompt:
        request_time = datetime.now(KST)
        with new_chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                # ✅ 2. 요청 시각 표시
                st.markdown(f'<p style="font-size: 12px; color: #888888; text-align: right;">요청: {request_time.strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)

            with st.chat_message("assistant"):
                with st.spinner("AI 비서가 분석 중입니다..."):
                    response = st.write_stream(stream_response_generator(prompt))
                response_time = datetime.now(KST)
                # ✅ 2. 분석 완료 시각 표시
                st.markdown(f'<p style="font-size: 12px; color: #888888; text-align: right;">완료: {response_time.strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)

        # 완료된 대화를 세션 기록의 맨 앞에 추가 (시각 정보 포함)
        st.session_state.messages.insert(0, {"role": "assistant", "content": response, "time": response_time})
        st.session_state.messages.insert(0, {"role": "user", "content": prompt, "time": request_time})

        st.rerun()

    # '과거 기록' 표시 로직
    with past_chat_container:
        conversation_pairs = []
        for i in range(0, len(st.session_state.messages), 2):
            conversation_pairs.append(
                (st.session_state.messages[i], st.session_state.messages[i+1])
            )

        for user_msg, assistant_msg in conversation_pairs:
            with st.chat_message(user_msg["role"]):
                st.markdown(user_msg["content"])
                st.markdown(f'<p style="font-size: 12px; color: #888888; text-align: right;">요청: {user_msg["time"].strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)
            with st.chat_message(assistant_msg["role"]):
                st.markdown(assistant_msg["content"])
                st.markdown(f'<p style="font-size: 12px; color: #888888; text-align: right;">완료: {assistant_msg["time"].strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)