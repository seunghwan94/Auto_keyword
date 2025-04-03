
import streamlit as st
from utils.sheet_auth import get_user_info

def login_page():
    st.title("🔐 로그인")

    email = st.text_input("이메일을 입력하세요:")
    if st.button("로그인"):
        user = get_user_info(email)

        if user:
            if user["allowed"]:
                st.session_state["authenticated"] = True
                st.session_state["user_email"] = user["email"]
                st.session_state["user_grade"] = user["grade"]  # 1: standard, 2: deluxe, 3: premium
                st.success(f"✅ 로그인 성공! [등급: {user['grade']}]")
                st.rerun()
            else:
                st.error("⚠️ 이 계정은 사용 권한이 중지되었습니다. (환불/정지 등)")
        else:
            st.error("❌ 등록되지 않은 사용자입니다.")
