import streamlit as st
import openai
import time

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
st.title("초등학교 서술형 평가 문항 인공지능 자동 채점 서비스 개발 및 적용 V1.7")

# 샘플 입력 안내
st.subheader("샘플 입력 예시")
st.write("[5단원][6국01-03]_토론하기 1. 아파트는 혼자 있는 곳이 아니라 사람들이 많이 이용하는 곳입니다. 그러므로 한명이 피면 다른 사람까지 간접흡연을 하게 되어 주민들이 피해를 봅니다. 그러므로 저는 아파트에서 담배 피는 것에 반대 합니다.")

# 사용자 입력받기
user_input = st.text_input("문항을 입력하세요:")

# 버튼 클릭 시 OpenAI API 호출
if st.button("채점하기") and user_input:
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
        st.write("### 채점 결과")
        for res in response:
            role = "User" if res.role == "user" else "Assistant"
            message = res.content
            # 역할에 따라 구분하여 표시
            if role == "User":
                #st.markdown(f"**[학생 응답]**\n> {message}\n", unsafe_allow_html=True)
            #else:
             #   st.markdown(f"**[AI 채점]**\n> {message}\n", unsafe_allow_html=True)
                   st.write(f"**[{role}]**\n> {message}\n")
            else:
                st.write(f"**[{role}]**\n> {message}\n")

    except Exception as e:
        st.error(f"오류가 발생했습니다. 다시 시도해 주세요. 오류: {str(e)}")
