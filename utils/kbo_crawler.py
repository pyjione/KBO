from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from bs4 import BeautifulSoup
from datetime import datetime
import os
from io import StringIO

def fetch_kbo_schedule_from_mykbo():
    # 브라우저 옵션 설정
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1920x1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    # 브라우저 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://mykbostats.com/schedule")
    time.sleep(3)  # JS 렌더링 대기

    html = driver.page_source
    driver.quit()

    # 테이블 읽기
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "table"})  # 또는 {"id": "scheduleTable"}

    if not table:
        with open("debug_mykbo.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("❗ 테이블을 여전히 찾을 수 없습니다. debug_mykbo.html로 저장합니다.")
        return pd.DataFrame()
    with open("debug_mykbo.html", "w", encoding="utf-8") as f:
        f.write(html)
    tables = pd.read_html(StringIO(str(table)))
    df = tables[0]

    print("✅ 컬럼명:", df.columns.tolist())

    df = df.rename(columns={
        'Date': '날짜',
        'Time': '시간',
        'Away': '원정팀',
        'Home': '홈팀',
        'Stadium': '구장'
    })

    df = df[['날짜', '시간', '원정팀', '홈팀', '구장']]

    def normalize_date(date_str):
        try:
            return datetime.strptime(date_str, "%b %d, %Y").strftime("%Y-%m-%d")
        except:
            return date_str

    df['날짜'] = df['날짜'].apply(normalize_date)

    os.makedirs("data", exist_ok=True)
    df.to_json("data/kbo_schedule_mykbo.json", force_ascii=False, orient="records", indent=2)
    print("✅ 일정 저장 완료 → data/kbo_schedule_mykbo.json")

    return df

if __name__ == "__main__":
    df = fetch_kbo_schedule_from_mykbo()
    print(df.head())