import streamlit as st
import openai
import time
import logging
import re  # 불필요한 텍스트 제거에 사용

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
    st.title("초등학교 서술형 평가 문항 인공지능 자동 채점 서비스 개발 및 적용 V1.6")
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
        st.write("[5단원][6국01-03]_토론하기 \n 1. 아파트는 혼자 있는 곳이 아니라 사람들이 많이 이용하는 곳입니다. 그러므로 한명이 피면 다른 사람까지 간접흡연을 하게 되어 주민들이 피해를 봅니다. 그러므로 저는 아파트에서 담배 피는 것에 반대 합니다.")
        st.subheader("샘플 입력 예시 2")
        st.write("[7단원][6국03-05]_기행문_쓰기 \n  일상생활에서의 토의 주제 1.학급에서 회장과 반장을 어떻게 뽑을 것인가? 2.우리반 안전 수칙을 어떻게 정할 것인가? 학습상황에서의 토의 주제 1.도덕시간때 더 예의 있게
