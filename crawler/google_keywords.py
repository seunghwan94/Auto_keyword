
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def get_google_autocomplete(keyword, max_count=10):
    """
    구글 자동완성 키워드 수집 (Selenium 사용)
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")

    input_box = driver.find_element(By.NAME, "q")
    input_box.send_keys(keyword)
    time.sleep(1)
    input_box.send_keys(Keys.ARROW_DOWN)

    time.sleep(2)

    suggestions = driver.find_elements(By.CSS_SELECTOR, "ul[role='listbox'] li span")
    results = [s.text for s in suggestions if s.text.strip()]

    driver.quit()

    return results[:max_count]
