
from konlpy.tag import Okt

okt = Okt()

def extract_nouns(text):
    """
    텍스트에서 명사만 추출
    """
    nouns = okt.nouns(text)
    return [noun for noun in nouns if len(noun) > 1]
