
def load_stopwords(path="assets/stopwords.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def remove_stopwords(words, stopwords):
    """
    불용어 리스트를 기반으로 단어 필터링
    """
    return [word for word in words if word not in stopwords]
