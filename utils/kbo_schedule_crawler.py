from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os

def fetch_kbo_schedule_from_mykbo():
    # Selenium 브라우저 설정
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1920x1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://mykbostats.com/schedule")
    driver.implicitly_wait(5)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    games = soup.find_all("a", class_="game-line")

    data = []

    # 현재 날짜 기준 (맨 앞 날짜를 헤더로 삼음)
    current_date = ""
    for tag in soup.select("h3 time"):
        current_date = tag['title']  # ex: "April 15, 2025 at 6:30pm KST"
        break

    for game in games:
        away = game.find("div", class_="away-team").text.strip()
        home = game.find("div", class_="home-team").text.strip()
        time_tag = game.find("time")
        venue_tag = game.find("div", class_="venue")

        if not time_tag or not venue_tag:
            continue

        time_text = time_tag.text.strip()
        venue = venue_tag.text.strip()

        # 날짜는 <a>의 이전 형제 중 h3 태그의 title에서 추출
        parent = game.find_previous("h3")
        game_date = parent.find("time")["title"].split(" at")[0] if parent else current_date

        # 날짜 포맷 변환
        try:
            date_parsed = datetime.strptime(game_date, "%B %d, %Y").strftime("%Y-%m-%d")
        except:
            date_parsed = game_date

        data.append({
            "날짜": date_parsed,
            "시간": time_text,
            "원정팀": away,
            "홈팀": home,
            "구장": venue
        })

    df = pd.DataFrame(data)
    os.makedirs("data", exist_ok=True)
    df.to_json("data/kbo_schedule_mykbo.json", force_ascii=False, orient="records", indent=2)
    print("✅ MyKBO 일정 저장 완료 → data/kbo_schedule_mykbo.json")
    return df

if __name__ == "__main__":
    df = fetch_kbo_schedule_from_mykbo()
    print(df.head())