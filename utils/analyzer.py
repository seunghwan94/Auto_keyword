
from collections import Counter
import pandas as pd
from konlpy.tag import Okt
from utils.other_path import resolve_path

def extract_nouns(text):
    """
    텍스트에서 명사만 추출
    """
    okt = Okt()
    nouns = okt.nouns(text)
    return [noun for noun in nouns if len(noun) > 1]


def rank_keywords(words, top_n=20):
    """
    단어 리스트를 빈도 기준으로 정렬하여 TOP N 반환
    """
    counter = Counter(words)
    return counter.most_common(top_n)


def get_recommended_keywords(ranked_df, stat_df, top_n=10, naver=[], google=[]):
    keywords_ranked = list(ranked_df["키워드"])
    keywords_naver = naver
    keywords_google = google
    keywords_all = keywords_ranked + keywords_naver + keywords_google

    stat_df["총 검색량"] = stat_df["월간 검색수_PC"] + stat_df["월간 검색수_모바일"]
    stat_df["경쟁 지수"] = stat_df["경쟁 지수"].fillna("없음")

    recommended = pd.DataFrame(columns=["연관 키워드", "총 검색량", "경쟁 지수"])

    def add_candidates(keywords, already_added, max_count):
        candidates = stat_df[
            (stat_df["연관 키워드"].isin(keywords)) &
            (~stat_df["연관 키워드"].isin(already_added))
        ]
        candidates = candidates.sort_values(by="총 검색량", ascending=False)
        return candidates[["연관 키워드", "총 검색량", "경쟁 지수"]].head(max_count)

    # 🥇 1단계: ranked_df + naver + google 교집합
    intersection_keywords = set(keywords_ranked) & set(keywords_naver + keywords_google)
    step1 = add_candidates(intersection_keywords, set(), top_n)
    recommended = pd.concat([recommended, step1], ignore_index=True)

    # 🥈 2단계: ranked + (naver or google) 추가
    remaining = top_n - len(recommended)
    if remaining > 0:
        step2_keywords = set(keywords_ranked) | set(keywords_naver) | set(keywords_google)
        step2 = add_candidates(step2_keywords, set(recommended["연관 키워드"]), remaining)
        recommended = pd.concat([recommended, step2], ignore_index=True)

    # 🥉 3단계: ranked_df만 추가
    remaining = top_n - len(recommended)
    if remaining > 0:
        step3 = add_candidates(keywords_ranked, set(recommended["연관 키워드"]), remaining)
        recommended = pd.concat([recommended, step3], ignore_index=True)

    # 🏅 4단계: 경쟁 지수 중
    remaining = top_n - len(recommended)
    if remaining > 0:
        step4 = stat_df[
            (stat_df["경쟁 지수"].isin(["중", "중간"])) &
            (~stat_df["연관 키워드"].isin(set(recommended["연관 키워드"])))
        ].sort_values(by="총 검색량", ascending=False)
        step4 = step4[["연관 키워드", "총 검색량", "경쟁 지수"]].head(remaining)
        recommended = pd.concat([recommended, step4], ignore_index=True)

    return recommended.drop_duplicates(subset=["연관 키워드"]).head(top_n)


def load_stopwords(path="utils/config/stopwords.txt"):
    with open(resolve_path(path), "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def remove_stopwords(words, stopwords):
    """
    불용어 리스트를 기반으로 단어 필터링
    """
    return [word for word in words if word not in stopwords]
