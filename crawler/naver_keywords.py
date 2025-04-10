import requests
from bs4 import BeautifulSoup
import urllib.parse

def get_naver_related_keywords(keyword, max_count=10):
    url = f"https://search.naver.com/search.naver?query={urllib.parse.quote(keyword)}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    related_keywords = []

    for div in soup.select("ul.lst_related_srch li div.tit"):
        related = div.get_text(strip=True)
        if related and related not in related_keywords:
            related_keywords.append(related)
        if len(related_keywords) >= max_count:
            break

    return related_keywords
