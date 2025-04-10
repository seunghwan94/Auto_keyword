import pandas as pd
import json as Json
import requests
import time
import hmac
import hashlib
import base64


class Signature:
    @staticmethod
    def generate(timestamp, method, uri, secret_key):
        message = "{}.{}.{}".format(timestamp, method, uri)
        hash = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
        return base64.b64encode(hash.digest()).decode("utf-8")


def get_header(method, uri, api_key, secret_key, customer_id):
    timestamp = str(round(time.time() * 1000))
    signature = Signature.generate(timestamp, method, uri, secret_key)

    return {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Timestamp': timestamp,
        'X-API-KEY': api_key,
        'X-Customer': str(customer_id),
        'X-Signature': signature
    }

def parse_search_value(value):
    try:
        return int(value)
    except:
        if isinstance(value, str) and "<" in value:
            return 5  # '< 10' → 5로 처리
        return 0  # 그 외 예외는 0으로 처리


def get_keyword_stat(config, keyword):

    if not all([config['client_id'], config['client_secret'], config['customer_id']]):
        return pd.DataFrame()

    BASE_URL = 'https://api.naver.com'
    uri = '/keywordstool'

    params = {
        'hintKeywords': ",".join(str(keyword).strip().split()),
        'showDetail': '1'
    }

    headers = get_header('GET', uri, config['client_id'], config['client_secret'], config['customer_id'])
    r = requests.get(BASE_URL + uri, params=params, headers=headers)


    if r.status_code != 200:
        print(f"[ERROR] 요청 실패: {r.status_code} - {r.text}")
        return pd.DataFrame()

    data = Json.loads(r.text)
    if 'keywordList' not in data:
        print("[ERROR] keywordList 키가 응답에 없습니다.")
        return pd.DataFrame()

    df = pd.DataFrame(data['keywordList'])

    # 숫자형 데이터 정제
    for col in ["monthlyPcQcCnt", "monthlyMobileQcCnt"]:
        df[col] = df[col].apply(parse_search_value)

    # 컬럼명 한글 변환
    rename_map = {
        'relKeyword': '연관 키워드',
        'monthlyPcQcCnt': '월간 검색수_PC',
        'monthlyMobileQcCnt': '월간 검색수_모바일',
        'monthlyAvePcClkCnt': '월평균 클릭수_PC',
        'monthlyAveMobileClkCnt': '월평균 클릭수_모바일',
        'monthlyAvePcCtr': '월평균 클릭률_PC',
        'monthlyAveMobileCtr': '월평균 클릭률_모바일',
        'plAvgDepth': '월평균 노출 광고수',
        'compIdx': '경쟁 지수'
    }
    df.rename(columns=rename_map, inplace=True)

    # 총합 검색량 컬럼 추가
    df['총 검색량'] = df['월간 검색수_PC'] + df['월간 검색수_모바일']

    # 원하는 컬럼만 추려서 반환
    df_result = df[['연관 키워드', '월간 검색수_PC', '월간 검색수_모바일', '총 검색량', '경쟁 지수']]
    return df_result.sort_values(by='총 검색량', ascending=False).reset_index(drop=True)
