
import urllib.request
import urllib.parse
import json as Json
import pandas as pd
import time
import requests
import hashlib
import hmac
import base64

class NaverAPI:
    def __init__(self, client_id, client_secret, api_key, secret_key, customer_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.secret_key = secret_key
        self.customer_id = customer_id
        self.base_url = 'https://api.naver.com'

    def get_blog_post_count(self, keyword):
        encText = urllib.parse.quote(keyword)
        url = f"https://openapi.naver.com/v1/search/blog.json?query={encText}"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)
        try:
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                response_body = response.read()
                return Json.loads(response_body.decode('utf-8'))['total']
        except Exception as e:
            print(f"[ERROR] 블로그 크롤링 실패: {e}")
        return None

    def get_keyword_data(self, hint_keywords):
        uri = '/keywordstool'
        params = {'hintKeywords': hint_keywords, 'showDetail': '1'}
        headers = self._get_header('GET', uri)

        try:
            r = requests.get(self.base_url + uri, params=params, headers=headers)
            print("[DEBUG] 응답 내용:", r.text)
            return pd.DataFrame(Json.loads(r.text)['keywordList'])
        except Exception as e:
            print(f"[ERROR] 키워드 도구 호출 실패: {e}")
            return pd.DataFrame()

    def _get_header(self, method, uri):
        timestamp = str(round(time.time() * 1000))
        message = f"{timestamp}.{method}.{uri}"
        hash_digest = hmac.new(
            bytes(self.secret_key, "utf-8"),
            bytes(message, "utf-8"),
            hashlib.sha256
        ).digest()
        signature = base64.b64encode(hash_digest)
        return {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Timestamp': timestamp,
            'X-API-KEY': self.api_key,
            'X-Customer': str(self.customer_id),
            'X-Signature': signature
        }
