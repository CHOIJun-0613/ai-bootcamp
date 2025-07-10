import streamlit as st
import requests
import json

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8001/chat"

# --- Streamlit UI 설정 ---
st.set_page_config(
    page_title="🤖 AI 업무 자동화 비서",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI 업무 자동화 비서")
st.markdown("""
이 AI 비서는 당신의 반복적인 업무를 도와줍니다.
- **이메일 요약**: "오늘 온 메일 요약해 줘"
- **일정 확인**: "오늘 내 일정 알려줘"
- **문서 검색 (RAG)**: "프로젝트 A 보고서 내용 알려줘" 또는 "7월 10일 회의록 요약해줘"
""")

# --- 채팅 기록 관리 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 사용자 입력 처리 ---
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    # 사용자 메시지 표시 및 저장
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI 응답 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # FastAPI 백엔드 호출
            with st.spinner("생각하는 과정 표시... 🤔"):
                response = requests.post(API_URL, json={"query": prompt})
                response.raise_for_status() # 오류 발생 시 예외 처리
                
                api_response = response.json()
                
                if "response" in api_response:
                    full_response = api_response["response"]
                elif "error" in api_response:
                    full_response = f"오류 발생: {api_response['error']}"
                else:
                    full_response = "알 수 없는 응답 형식입니다."

            message_placeholder.markdown(full_response)

        except requests.exceptions.RequestException as e:
            full_response = f"API 서버에 연결할 수 없습니다: {e}"
            message_placeholder.error(full_response)
        except Exception as e:
            full_response = f"처리 중 오류가 발생했습니다: {e}"
            message_placeholder.error(full_response)

    # AI 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})