import os
import json

CONFIG_PATH = "config.json"

def save_config(config_data):
    dir_path = os.path.dirname(CONFIG_PATH)
    if dir_path:  # 경로가 있을 때만 디렉토리 생성
        os.makedirs(dir_path, exist_ok=True)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            return config_data
    except Exception as e:
        print(f"[ERROR] 설정 파일 로드 실패: {e}")
        return {}  # 기본값으로 빈 dict 반환