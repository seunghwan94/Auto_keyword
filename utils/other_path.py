# utils/other_path.py

import os
import sys

def resolve_path(relative_path):
    """
    PyInstaller로 빌드된 실행파일(exe)에서도 동작할 수 있게
    상대 경로를 처리해주는 함수
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # PyInstaller 환경
    else:
        base_path = os.getcwd()   # 일반 실행 환경
    return os.path.join(base_path, relative_path)
