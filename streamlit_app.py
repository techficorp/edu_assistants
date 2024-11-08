import streamlit as st
import openai
import time
import os

# Streamlit Secrets에서 API 키 로드
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
st.write("샘플입력값\n")
st.write("[5단원][6국01-03]_토론하기 1. 아파트는 혼자 있는 곳이 아니라 사람들이 많이 이용 하는 곳입니다. 그러므로 한명이 피면 다른 사람까지 간접흡연을 하게되 하면 주민들이 피해를 봅니다. 그러므로 저는 아파트에서 담배 피는 것에 반대 합니다.")

# 사용자 입력받기
user_input = st.text_input("Enter your question:")

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
            # 예외 처리를 통해 res가 예상 구조가 아닐 경우 기본 메시지 출력
            try:
                st.write(f"**{role}:** {res['content']}")
            except KeyError:
                st.write(f"**{role}:** (응답을 처리할 수 없습니다)")
    except Exception:
        st.error("알 수 없는 오류가 발생했습니다. 다시 시도해 주세요.")
