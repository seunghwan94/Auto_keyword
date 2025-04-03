
import requests
from bs4 import BeautifulSoup
import time
import re
import urllib.parse
import random
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class BlogCrawler:

    def __init__(self, delay_range=(1.0, 2.5)):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }
        self.delay_range = delay_range

    def crawl_naver_blogs(self, keyword, max_posts=10):
        logging.info(f"🔎 네이버 블로그에서 '{keyword}' 검색 중...")
        search_url = f"https://search.naver.com/search.naver?where=post&query={urllib.parse.quote(keyword)}"
        response = requests.get(search_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        post_links = [
            a["href"] for a in soup.select("a.link_tit") if a.has_attr("href")
        ][:max_posts]

        logging.info(f"👉 총 {len(post_links)}개 포스트 추출됨 (네이버)")
        return [self._extract_naver_post(link) for link in post_links]

    def crawl_tistory_blogs(self, keyword, max_posts=10):
        logging.info(f"🔎 티스토리 블로그에서 '{keyword}' 검색 중...")
        search_url = f"https://search.naver.com/search.naver?where=blog&query={urllib.parse.quote(keyword + ' site:tistory.com')}"
        response = requests.get(search_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        post_links = [
            a["href"] for a in soup.select("a.link_tit") if a.has_attr("href")
        ][:max_posts]

        logging.info(f"👉 총 {len(post_links)}개 포스트 추출됨 (티스토리)")
        return [self._extract_tistory_post(link) for link in post_links]

    def _extract_naver_post(self, url):
        try:
            time.sleep(random.uniform(*self.delay_range))
            res = requests.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            title = soup.title.text.strip() if soup.title else "제목 없음"
            content = soup.get_text()
            cleaned = self._clean_text(content)
            return {"title": title, "content": cleaned, "source": "naver", "url": url}
        except Exception as e:
            logging.warning(f"❌ 네이버 포스트 파싱 실패: {e}")
            return None

    def _extract_tistory_post(self, url):
        try:
            time.sleep(random.uniform(*self.delay_range))
            res = requests.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            title = soup.title.text.strip() if soup.title else "제목 없음"
            content_area = soup.find("div", {"class": re.compile(".*entry-content.*|.*article.*|.*content.*")})
            content = content_area.get_text() if content_area else soup.get_text()
            cleaned = self._clean_text(content)
            return {"title": title, "content": cleaned, "source": "tistory", "url": url}
        except Exception as e:
            logging.warning(f"❌ 티스토리 포스트 파싱 실패: {e}")
            return None

    def _clean_text(self, text):
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[\r\n\t]", " ", text)
        text = re.sub(r"[^가-힣a-zA-Z0-9\s.,!?]", "", text)  # 한글, 영문, 숫자 외 제거
        return text.strip()

if __name__ == "__main__":
    crawler = BlogCrawler()
    keyword = "다이어트 식단"
    naver_posts = crawler.crawl_naver_blogs(keyword, max_posts=5)
    tistory_posts = crawler.crawl_tistory_blogs(keyword, max_posts=5)

    for post in (naver_posts + tistory_posts):
        if post:
            print(f"[{post['source'].upper()}] {post['title']}")
            print(post["content"][:150], "...\n")
