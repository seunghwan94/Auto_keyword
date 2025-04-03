
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random

def get_naver_related_keywords(keyword, max_count=10):
    """
    네이버 자동완성/연관 검색어 수집
    """
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

    for a in soup.select("ul.related_keyword ul li a"):
        related = a.get_text().strip()
        if related and related not in related_keywords:
            related_keywords.append(related)
        if len(related_keywords) >= max_count:
            break

    return related_keywords
