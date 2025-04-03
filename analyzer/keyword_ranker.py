
from collections import Counter

def rank_keywords(words, top_n=20):
    """
    단어 리스트를 빈도 기준으로 정렬하여 TOP N 반환
    """
    counter = Counter(words)
    return counter.most_common(top_n)
