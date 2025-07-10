import streamlit as st
import requests

# API 서버 주소
BACKEND_URL = "http://localhost:8001"
STREAM_ENDPOINT = f"{BACKEND_URL}/chat/stream"

st.set_page_config(page_title="AI 업무 자동화 비서", page_icon="🤖")
st.title("🤖 AI 업무 자동화 비서")
st.caption("LangChain, FastAPI, Streamlit으로 구현한 스트리밍 챗봇")

# 세션 상태에 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def stream_response_generator(user_input: str):
    """
    백엔드 API에 스트리밍 요청을 보내고, 받은 청크를 yield합니다.
    """
    with requests.post(
        STREAM_ENDPOINT, json={"message": user_input}, stream=True, timeout=600
    ) as response:
        if response.status_code != 200:
            error_message = f"Error: {response.status_code} - {response.text}"
            st.error(error_message)
            yield error_message
            return

        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            yield chunk

# 사용자 입력 처리
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    # 사용자 메시지를 대화 기록에 추가하고 UI에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답을 스트리밍으로 표시
    with st.chat_message("assistant"):
        # st.write_stream은 제너레이터로부터 받은 텍스트를 점진적으로 화면에 씁니다.
        response = st.write_stream(stream_response_generator(prompt))

    # 전체 AI 응답을 대화 기록에 추가
    st.session_state.messages.append({"role": "assistant", "content": response})