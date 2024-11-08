import streamlit as st
import openai
import time
import json

# OpenAI API 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]

# 새 Thread 생성 함수
def create_new_thread():
    thread = openai.beta.threads.create()
    return thread.id

# 메시지 전송 및 Run 실행 함수
def submit_message(assistant_id, thread_id, user_message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run

# Run 상태 확인 함수
def wait_on_run(run, thread_id):
    while run.status in ["queued", "in_progress"]:
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        time.sleep(0.5)
    return run

# 응답 가져오기 함수
def get_response(thread_id):
    messages = openai.beta.threads.messages.list(thread_id=thread_id, order="asc").data[-2:]
    return messages

# Streamlit 웹 페이지 구성
st.title("OpenAI Assistants API Chatbot")
st.write("Ask a question and get an answer from the assistant!")

# 사용자 입력받기
user_input = st.text_input("Enter your question:")

# 스타일 추가
st.markdown("""
    <style>
        .user-message, .assistant-message {
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
            max-width: 600px;
        }
        .user-message {
            background-color: #daf7a6;
            text-align: left;
        }
        .assistant-message {
            background-color: #f0e5ff;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

# 버튼 클릭 시 OpenAI API 호출
if st.button("Submit") and user_input:
    try:
        # 새 Thread 생성
        thread_id = create_new_thread()
        
        # 메시지 전송 및 Run 실행
        run = submit_message(ASSISTANT_ID, thread_id, user_input)
        
        # Run 상태 확인
        wait_on_run(run, thread_id)
        
        # 응답 가져오기
        response = get_response(thread_id)
        
        # 응답 출력
        st.write("### Chat History")
        for res in response:
            role = "User" if res.role == "user" else "Assistant"
            message = res['content']
            if role == "User":
                st.markdown(f'<div class="user-message"><strong>{role}:</strong> {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message"><strong>{role}:</strong> {message}</div>', unsafe_allow_html=True)

    except openai.OpenAIError as e:
        st.error(f"An error occurred: {e}")
