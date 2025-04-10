import streamlit as st
from utils.analyzer import get_recommended_keywords

def premium(df_keywords, keyword_stats_df, naver, google):
    recommended_df = get_recommended_keywords(
        ranked_df=df_keywords,
        stat_df=keyword_stats_df,
        top_n=10,
        naver=naver,
        google=google
    )
    if not recommended_df.empty:
        st.subheader("🌟 추천 키워드 (키워드 랭킹 + 네이버 키워드 + 연관검색어)")
        st.dataframe(recommended_df)
