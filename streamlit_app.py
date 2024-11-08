import streamlit as st
import openai
import time
import logging

# 로깅 설정
logging.basicConfig(filename="output_log.log", level=logging.INFO, format="%(asctime)s - %(message)s")

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
st.title("초등학교 서술형 평가 문항 인공지능 자동 채점 서비스 개발 및 적용")

# 샘플 입력 안내
st.subheader("샘플 입력 예시1\n")

st.write("[5단원][6국01-03]_토론하기 1. 아파트는 혼자 있는 곳이 아니라 사람들이 많이 이용하는 곳입니다. 그러므로 한명이 피면 다른 사람까지 간접흡연을 하게 되어 주민들이 피해를 봅니다. 그러므로 저는 아파트에서 담배 피는 것에 반대 합니다.")
st.subheader("샘플 입력 예시2\n")
st.write("[7단원][6국03-05]_기행문_쓰기	일상생활에서의 토의 주제 1.학급에서 회장과 반장을 어떻게 뽑을 것인가? 2.우리반 안전 수칙을 어떻게 정할 것인가? 학습상황에서의 토의 주제 1.도덕시간때 더 예의 있게 말할 것인가? 2.수업시간 때에 떠들지 않을 것인가?")
# 사용자 입력받기
user_input = st.text_input("평가기준과 주관식답안을 입력하세요:")

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
            role = "학생 응답" if res.role == "user" else "AI 채점"

            # res.content가 리스트일 경우 처리
            message_content = res.content
            if isinstance(message_content, list):
                # 리스트 항목을 줄바꿈으로 연결하여 텍스트로 변환
                message_content = "\n".join(str(item) for item in message_content)
            
            # 원래의 출력 내용을 로그에 남기기
            logging.info(f"{role}: {message_content}")

            # HTML 형식으로 불필요한 정보 제거 후 출력
            formatted_message = message_content.replace(", type='text'", "").replace("\n", "<br>")
            st.markdown(f"<div style='padding: 10px; background-color: #f9f9f9; border-radius: 5px;'>"
                        f"<strong>{role}</strong><br>{formatted_message}</div>",
                        unsafe_allow_html=True)

    except Exception as e:
        st.error(f"오류가 발생했습니다. 다시 시도해 주세요. 오류: {str(e)}")
