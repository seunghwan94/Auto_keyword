import streamlit as st
from crawler.naver_ads import get_keyword_stat
from utils.config import save_config, load_config

def deluxe_mune():
    st.sidebar.title("🔑 DELUXE 플랜 설정")
    config = load_config()

    email = st.sidebar.subheader("[네이버 광고 API 바로가기](https://manage.searchad.naver.com/customers/3022005/campaigns)")
    customer_id = st.sidebar.text_input("CUSTOMER_ID", value=config.get("customer_id", ""))
    client_id = st.sidebar.text_input("엑세스라이선스", value=config.get("client_id", ""))
    client_secret = st.sidebar.text_input("비밀키", type="password", value=config.get("client_secret", ""))

    if st.sidebar.button("저장"):
        config_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "customer_id": customer_id,
            # ✅ 기존 이메일 유지
            "email": config.get("email", "")
        }

        save_config(config_data)
        st.sidebar.success("✅ 설정이 저장되었습니다.")


# 네이버 통계 출력
def deluxe_main(keyword):
    config = load_config()
    keyword_stats_df = get_keyword_stat(config, keyword)

    if not keyword_stats_df.empty:
        st.subheader("📈 네이버 키워드 통계")
        st.dataframe(keyword_stats_df)
    else:
        st.warning("네이버 키워드 통계를 불러올 수 없습니다.")

    return keyword_stats_df