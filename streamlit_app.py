import streamlit as st
import openai
import time
import json
#from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
#load_dotenv()
# Streamlit Secrets에서 API 키 로드
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]

try:
    # 간단한 API 호출 테스트 (예: 모델 목록 가져오기)
    models = openai.Model.list()
    #st.write("OpenAI API 연결 성공. 사용 가능한 모델 목록:")
    #st.write(models)
except openai.OpenAIError as e:  # 모든 OpenAI API 오류를 포괄하는 예외 처리
    st.error(f"OpenAI API 오류 발생: {str(e)}")


# OpenAI API 설정
#openai.api_key = os.getenv("OPENAI_API_KEY")
#ASSISTANT_ID = os.getenv("ASSISTANT_ID")
# OpenAI API 설정
#openai.api_key = os.getenv("OPENAI_API_KEY")
#ASSISTANT_ID = os.getenv("ASSISTANT_ID")
#openai.api_key = os.getenv("OPENAI_API_KEY")
#ASSISTANT_ID = os.getenv("ASSISTANT_ID")

#openai.api_key = "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"
#ASSISTANT_ID = "asst_OAbaHNhxMb7SRkm6ep980FWv"
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
st.write("샘플입력값\n")
st.write("[5단원][6국01-03]_토론하기	1. 아파트는 혼자 있는 곳이 아니라  사람들이 많이 이용 하는 곳입니다. 그러므로 한명이 피면 다른 사람까지 간접흡연을 하게되 하면  주민들이 피해를 봅니다. 그러므로 저는 아파트에서 담배 피는 것에 반대 합니다.")

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
