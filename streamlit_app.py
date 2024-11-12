import streamlit as st
import openai
import time
import logging
import re

# 로깅 설정
logging.basicConfig(filename="login_attempts.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# 미리 정의된 유저 데이터 (아이디, 비밀번호, 이름)
USER_DATA = {
    "supered1": {"password": "supered1!", "name": "백남정"},
    "supered": {"password": "supered2!", "name": "백동재관리자"},
    "supered2": {"password": "supered2!", "name": "박정"},
    "ksj8639": {"password": "test12", "name": "강신조"}
}

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["name"] = ""

# 로그인 함수
def authenticate(username, password):
    if username in USER_DATA and USER_DATA[username]["password"] == password:
        return USER_DATA[username]["name"]
    return None

# 로그인 및 메인 화면
def app_screen():
    st.title("초등학교 서술형 평가 문항 인공지능 자동 채점 서비스 개발 및 적용 V1.7")
    st.write("*관련 문의: jay7math@gmail.com, 백동재, techficorp@gmail.com, 백남정 ")
    
    # 로그인되지 않은 경우 로그인 화면 표시
    if not st.session_state["logged_in"]:
        st.subheader("로그인 화면")
        st.write("인가된 사용자만 접근 가능합니다. 미 인가자는 접속이 불가합니다. 무단 접속 시 법적 조치될 수 있습니다.")
        
        # 사용자 입력 받기
        username = st.text_input("아이디를 입력하세요", key="username_input")
        password = st.text_input("비밀번호를 입력하세요", type="password", key="password_input")
        
        # 로그인 버튼
        if st.button("로그인"):
            logging.info(f"{username} 로그인 시도")
            
            # 인증 확인
            name = authenticate(username, password)
            if name:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["name"] = name
                logging.info(f"{username} 로그인 성공")
                st.success(f"로그인 성공: 환영합니다, {name}님!")
            else:
                st.error("로그인 실패: 아이디 또는 비밀번호가 올바르지 않습니다.")
                logging.info(f"{username} 로그인 실패")
    
    # 로그인된 경우 메인 콘텐츠 표시
    if st.session_state["logged_in"]:
        st.write(f"환영합니다, {st.session_state['name']}님!")
        
        # 로그아웃 버튼
        if st.button("로그아웃", key="logout_button"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["name"] = ""
            st.experimental_rerun()
        
        # 샘플 입력 안내
        st.subheader("샘플 입력 예시 1")
        st.write("[5단원][6국01-03]_토론하기 \n"
                 "1. 아파트는 혼자 있는 곳이 아니라 사람들이 많이 이용하는 곳입니다. "
                 "그러므로 한명이 피면 다른 사람까지 간접흡연을 하게 되어 주민들이 피해를 봅니다. "
                 "그러므로 저는 아파트에서 담배 피는 것에 반대 합니다.")
        
        st.subheader("샘플 입력 예시 2")
        st.write("[7단원][6국03-05]_기행문_쓰기 \n"
                 "일상생활에서의 토의 주제 1. 학급에서 회장과 반장을 어떻게 뽑을 것인가? "
                 "2. 우리반 안전 수칙을 어떻게 정할 것인가? 학습상황에서의 토의 주제 "
                 "1. 도덕시간 때 더 예의 있게 말할 것인가? 2. 수업시간 때에 떠들지 않을 것인가?")
        
        # 사용자 입력받기
        user_input_answer = st.text_input("평가기준과 주관식 답안을 입력하세요:")
        
        # OpenAI API 설정
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        ASSISTANT_ID = st.secrets["ASSISTANT_ID"]
        
        # 버튼 클릭 시 OpenAI API 호출
        if st.button("채점하기", key="grading_button") and user_input_answer:
            try:
                # 새 Thread 생성
                thread_id = openai.beta.threads.create().id
                
                # 메시지 전송 및 Run 실행
                openai.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=user_input_answer
                )
                run = openai.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=ASSISTANT_ID
                )
                
                # Run 상태 확인
                while run.status in ["queued", "in_progress"]:
                    run = openai.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                    time.sleep(0.5)
                
                # 응답 가져오기
                response = openai.beta.threads.messages.list(
                    thread_id=thread_id,
                    order="asc"
                ).data
                
                # 응답 출력 및 로그 기록
                st.write("### 채점 결과")
                for res in response:
                    # 메시지 내용 추출
                    message_content = res.content[0].text.value if res.content else ""
                    
                    # 불필요한 텍스트 패턴 제거
                    message_content = re.sub(r"TextContentBlock\(text=Text\(annotations=\[\], value='|'|\\n", "", message_content)
                    
                    # 로그에 원본 메시지 기록
                    logging.info(f"채점 결과 (원본): {message_content}")
                    
                    # 결과 출력 (HTML 개행 적용)
                    formatted_message = message_content.replace("\n", "<br>")
                    st.markdown(f"<div style='padding: 10px; background-color: #f9f9f9; border-radius: 5px;'>"
                                f"<strong>{'학생 주관식 답안' if res.role == 'user' else 'AI 채점'}</strong><br>{formatted_message}</div>",
                                unsafe_allow_html=True)
            
            except Exception as e:
                # 오류 메시지를 사용자에게 표시 (개행 추가)
                st.markdown(f"<div style='color: red;'>API 사용량 제한이 초과되었거나 기타 오류가 발생했습니다.<br>오류 내용: {str(e)}</div>",
                            unsafe_allow_html=True)
                logging.error(f"API 오류 발생: {str(e)}")

# 실행
app_screen()
