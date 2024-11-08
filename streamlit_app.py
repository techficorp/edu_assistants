import streamlit as st
import openai
import time
import json
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
#load_dotenv()


# OpenAI API 설정
#openai.api_key = os.getenv("OPENAI_API_KEY")
#ASSISTANT_ID = os.getenv("ASSISTANT_ID")
# OpenAI API 설정
#openai.api_key = os.getenv("OPENAI_API_KEY")
#ASSISTANT_ID = os.getenv("ASSISTANT_ID")
#openai.api_key = os.getenv("OPENAI_API_KEY")
#ASSISTANT_ID = os.getenv("ASSISTANT_ID")

openai.api_key = "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"
ASSISTANT_ID = "asst_OAbaHNhxMb7SRkm6ep980FWv"
#st.write("API Key:", os.getenv("OPENAI_API_KEY"))
#st.write("Assistant ID:", os.getenv("ASSISTANT_ID"))
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

# 버튼 클릭 시 OpenAI API 호출
if st.button("Submit") and user_input:
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
        st.write(f"**{role}:** {res['content']}")
