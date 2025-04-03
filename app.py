
import streamlit as st
import pandas as pd
import os
import json

from login import login_page
from crawler.blog_crawler import BlogCrawler
from crawler.naver_keywords import get_naver_related_keywords
from crawler.google_keywords import get_google_autocomplete
from keyword_stat.naver_api import NaverAPI
from analyzer.noun_extractor import extract_nouns
from analyzer.stopword_cleaner import load_stopwords, remove_stopwords
from analyzer.keyword_ranker import rank_keywords
import pandas as pd

CONFIG_PATH = "config/deluxe_config.json"

def load_naver_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config["client_id"], config["client_secret"], config["customer_id"]
    except Exception as e:
        print(f"[ERROR] 설정 파일 로드 실패: {e}")
        return None, None, None

def get_keyword_stat(keyword):
    client_id, client_secret, customer_id = load_naver_config()
    if not all([client_id, client_secret, customer_id]):
        return None

    # 실제 API 키는 별도로 안전하게 로드해야 함 (예시 값 사용)
    API_KEY = client_id
    SECRET_KEY = client_secret
    CUSTOMER_ID = customer_id

    api = NaverAPI(client_id, client_secret, API_KEY, SECRET_KEY, CUSTOMER_ID)
    df = api.get_keyword_data(keyword)

    if df.empty:
        return None

    stat_row = df[df["relKeyword"] == keyword]
    if stat_row.empty:
        stat_row = df.iloc[[0]]  # 없으면 첫 번째 결과라도 반환

    return stat_row.iloc[0].to_dict()




st.set_page_config(page_title="SEO 키워드 분석기", layout="wide")

# 로그인 처리
if "authenticated" not in st.session_state:
    login_page()
    st.stop()

# 등급 플랜 표시
plan_grade = st.session_state.get("user_grade", 1)
plan_name = {1: "🟢 STANDARD", 2: "🔵 DELUXE", 3: "🟣 PREMIUM"}.get(plan_grade, "🟢 STANDARD")
st.sidebar.success(f"로그인됨: {st.session_state['user_email']}\n등급: {plan_name}")

# DELUXE 플랜 입력 UI
if plan_grade in [2, 3]:  # DELUXE와 PREMIUM 플랜 모두 가능
    st.sidebar.title("🔑 DELUXE 플랜 설정")
    client_id = st.sidebar.text_input("네이버 Client ID")
    client_secret = st.sidebar.text_input("네이버 Client Secret", type="password")
    customer_id = st.sidebar.text_input("네이버 Customer ID")
    
    if st.sidebar.button("저장"):
        config_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "customer_id": customer_id
        }
        with open("config/deluxe_config.json", "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        st.sidebar.success("✅ 설정이 저장되었습니다.")

# PREMIUM 플랜 엑셀 다운로드 설정
if plan_grade == 3:
    st.sidebar.title("📥 PREMIUM 플랜 엑셀 다운로드 설정")
    if st.sidebar.button("엑셀로 다운로드"):
        # 엑셀 파일로 랭킹 저장
        df_keywords = pd.DataFrame(ranked_keywords, columns=["키워드", "빈도수"])
        file_path = "ranked_keywords.xlsx"
        df_keywords.to_excel(file_path, index=False)
        st.sidebar.success(f"✅ 엑셀 파일이 생성되었습니다: {file_path}")
        st.download_button("엑셀 다운로드", file_path)

# 분석 키워드 입력
st.title(f"{plan_name} 키워드 분석기")
keyword = st.text_input("분석할 주제 키워드를 입력하세요 (예: 다이어트 식단):", "")

if keyword:
    st.info(f"'{keyword}' 관련 블로그 본문과 연관검색어를 분석합니다.")

    with st.spinner("📦 데이터 수집 중..."):
        crawler = BlogCrawler()
        naver_posts = crawler.crawl_naver_blogs(keyword, max_posts=5)
        tistory_posts = crawler.crawl_tistory_blogs(keyword, max_posts=5)
        all_posts = [p for p in (naver_posts + tistory_posts) if p]
        full_text = "\n".join([p["content"] for p in all_posts])

        related_naver = get_naver_related_keywords(keyword)
        related_google = get_google_autocomplete(keyword)
        related_text = " ".join(related_naver + related_google)

    total_text = full_text + " " + related_text
    nouns = extract_nouns(total_text)
    stopwords = load_stopwords("assets/stopwords.txt")
    filtered = remove_stopwords(nouns, stopwords)
    ranked_keywords = rank_keywords(filtered, top_n=30)

    # 📊 키워드 랭킹
    df_keywords = pd.DataFrame(ranked_keywords, columns=["키워드", "빈도수"])
    st.subheader("📊 키워드 랭킹 TOP 30")
    st.table(df_keywords)

    # DELUXE 이상일 때 검색량 출력
    if plan_grade >= 2:
        get_keyword_stat(get_keyword_stat)
    else:
        st.warning("🔒 Deluxe 플랜부터 검색량/경쟁도 분석 기능을 이용할 수 있습니다.")

    # PREMIUM 전용 기능 (엑셀 다운로드)
    if plan_grade >= 3:
        st.success("📥 프리미엄 사용자: 엑셀 다운로드 기능을 사용할 수 있습니다.")

    with st.expander("🧩 연관검색어"):
        st.markdown("**네이버:**")
        st.write(", ".join(related_naver))
        st.markdown("**구글:**")
        st.write(", ".join(related_google))

    with st.expander("📰 블로그 본문 미리보기"):
        for post in all_posts:
            st.markdown(f"**[{post['source'].upper()}] {post['title']}**")
            st.caption(post["url"])
            st.write(post["content"][:300] + "...")
else:
    st.warning("분석할 키워드를 입력해주세요.")


