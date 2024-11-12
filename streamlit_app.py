import openai
import streamlit as st

# 유저 데이터 (아이디, 비밀번호, 이름)
USER_DATA = {
    "supered1": {"password": "supered1!", "name": "백남정"},
    "supered": {"password": "supered2!", "name": "백동재관리자"},
    "supered2": {"password": "supered2!", "name": "박정"},
    "ksj8639": {"password": "test12", "name": "강신조"}
}

# 페이지 초기화
st.title("AI 서술형 평가 자동 채점 서비스")

# 로그인 상태를 추적하기 위한 세션 상태 설정
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""

# 로그인 기능
def login(username, password):
    if username in USER_DATA and USER_DATA[username]["password"] == password:
        st.session_state.logged_in = True
        st.session_state.user_name = USER_DATA[username]["name"]
        return True
    else:
        return False

# 로그아웃 기능
def logout():
    st.session_state.logged_in = False
    st.session_state.user_name = ""

# 로그인 화면
if not st.session_state.logged_in:
    st.subheader("로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    
    if st.button("로그인"):
        if login(username, password):
            st.success(f"환영합니다, {st.session_state.user_name}님!")
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
else:
    # 로그인 후 메인 페이지 표시
    st.subheader(f"환영합니다, {st.session_state.user_name}님!")
    
    # 입력 섹션
    st.write("서술형 평가 문항을 입력하세요.")
    input_text = st.text_area("입력 예시", 
                              "[5단원][6국01-03]_토론하기\n"
                              "아파트는 혼자 있는 곳이 아니라 사람들이 많이 이용하는 곳입니다. "
                              "그러므로 한명이 피면 다른 사람까지 간접흡연을 하게 되어 주민들이 피해를 봅니다. "
                              "그러므로 저는 아파트에서 담배 피는 것에 반대 합니다.")
    
    # 챗GPT와 연결하여 자동 채점 예시 응답 가져오기
    if st.button("채점 요청"):
        # OpenAI API 설정
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        ASSISTANT_ID = st.secrets["ASSISTANT_ID"]
        
        # 챗GPT API를 통해 응답 가져오기
        response = get_response_from_gpt(ASSISTANT_ID, input_text)
        
        # 응답 출력
        if response:
            st.write("### 자동 채점 결과")
            st.write(response)
        else:
            st.error("채점 응답을 가져오는 데 실패했습니다.")

    # 로그아웃 버튼
    if st.button("로그아웃"):
        logout()
        st.success("로그아웃 되었습니다.")

# 챗GPT와 연결하여 응답 가져오는 함수
def get_response_from_gpt(assistant_id, text):
    # OpenAI API를 사용하여 assistant_id와 텍스트로 응답 생성
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 모델명 설정
            messages=[{"role": "user", "content": text}],
            assistant_id=assistant_id
        )
        # 응답 텍스트 반환
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"API 요청 중 오류가 발생했습니다: {e}")
        return None
