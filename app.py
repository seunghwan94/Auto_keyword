import streamlit as st
import pandas as pd
import os

from page.login import login_page
from crawler.blog_crawler import BlogCrawler
from crawler.naver_keywords import get_naver_related_keywords
from crawler.google_keywords import get_google_autocomplete
from utils.analyzer import extract_nouns, load_stopwords, remove_stopwords, rank_keywords

from page.deluxe import deluxe_mune, deluxe_main
from page.premium import premium

st.set_page_config(page_title="SEO 키워드 분석기", layout="wide")

# 로그인 처리
if "authenticated" not in st.session_state:
    login_page()
    st.stop()

# 등급 플랜 표시
plan_grade = st.session_state.get("user_grade", 1)
plan_name = {1: "🟢 STANDARD", 2: "🔵 DELUXE", 3: "🟣 PREMIUM"}.get(plan_grade, "🟢 STANDARD")
st.sidebar.success(f"로그인됨: {st.session_state['user_email']}\n등급: {plan_name}")

# DELUXE 플랜 설정 입력
if plan_grade in [2, 3]:
    deluxe_mune()

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

    # 명사 추출 및 랭킹
    total_text = full_text + " " + related_text
    nouns = extract_nouns(total_text)
    stopwords = load_stopwords()
    filtered = remove_stopwords(nouns, stopwords)
    ranked_keywords = rank_keywords(filtered, top_n=30)

    # 📊 키워드 랭킹
    df_keywords = pd.DataFrame(ranked_keywords, columns=["키워드", "빈도수"])
    st.subheader("📊 키워드 랭킹 TOP 30")
    st.table(df_keywords)

    # DELUXE 이상: 네이버 통계 출력
    keyword_stats_df = pd.DataFrame()

    if plan_grade >= 2:
        keyword_stats_df = deluxe_main(keyword)
    else:
        st.warning("🔒 Deluxe, Premium 검색량/경쟁도 분석 기능을 이용할 수 있습니다.")

    # 부가 정보 (연관검색어 & 블로그 미리보기)
    with st.expander("🧩 연관검색어"):
        st.markdown("**네이버:**")
        st.write(", ".join(related_naver))
        st.markdown("**구글:**")
        st.write(", ".join(related_google))

    # PREMIUM: 추천 키워드
    if plan_grade == 3 and not df_keywords.empty and not keyword_stats_df.empty:
        premium(df_keywords, keyword_stats_df, related_naver, related_google)


    with st.expander("📰 블로그 본문 미리보기"):
        for post in all_posts:
            st.markdown(f"**[{post['source'].upper()}] {post['title']}**")
            st.caption(post["url"])
            st.write(post["content"][:300] + "...")
else:
    st.warning("분석할 키워드를 입력해주세요.")
