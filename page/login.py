import streamlit as st
from utils.sheet_auth import get_user_info
from utils.config import save_config, load_config

def login_page():
    config = load_config()

    st.title("KeyWordFind")

    email = st.text_input("개발자에게 보내주신 이메일을 작성하세요. [설명서 바로가기](https://fate-dart-576.notion.site/Auto-Program-1d1c49195faf8059b1f6f3424019f329)", value=config.get("email", ""))
    if st.button("로그인"):
        user = get_user_info(email)

        if user:
            if user["allowed"]:
                # ✅ 세션 상태 저장
                st.session_state["authenticated"] = True
                st.session_state["user_email"] = user["email"]
                st.session_state["user_grade"] = user["grade"]

                # ✅ config.json에도 이메일 저장
                config["email"] = user["email"]
                save_config(config)

                st.success(f"✅ 로그인 성공! [등급: {user['grade']}]")
                st.rerun()
            else:
                st.error("⚠️ 이 계정은 사용 권한이 중지되었습니다. (환불/정지 등)")
        else:
            st.error("❌ 등록되지 않은 사용자입니다.")
