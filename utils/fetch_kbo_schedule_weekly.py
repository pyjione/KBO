import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import os
import time

def fetch_schedule_with_undetected_chrome(start_date, end_date):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")  # Optional for debugging

    driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options, headless=False)  # headless=False for testing
    all_games = []

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = f"https://mykbostats.com/schedule/week_of/{date_str}"
        driver.get(url)

        try:
            # Increase waiting time to ensure the page is fully loaded
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "game-line"))
            )
        except Exception as e:
            print(f"⚠️ {date_str}: 'game-line' 요소 로딩 실패. 오류: {e}")
            current_date += timedelta(weeks=1)
            continue  # Skip this date if the elements aren't found

        soup = BeautifulSoup(driver.page_source, "html.parser")
        games = soup.find_all("a", class_="game-line")

        if not games:
            print(f"⚠️ {date_str}: game-line 요소 없음")
        else:
            print(f"📆 {date_str}: {len(games)}경기 발견")

        for game in games:
            try:
                away = game.find("div", class_="away-team").text.strip()
                home = game.find("div", class_="home-team").text.strip()
                time_tag = game.find("time")
                venue_tag = game.find("div", class_="venue")
                parent = game.find_previous("h3")
                game_date = parent.find("time")["title"].split(" at")[0] if parent else date_str

                date_parsed = datetime.strptime(game_date, "%B %d, %Y").strftime("%Y-%m-%d")

                all_games.append({
                    "날짜": date_parsed,
                    "시간": time_tag.text.strip(),
                    "원정팀": away,
                    "홈팀": home,
                    "구장": venue_tag.text.strip()
                })
            except Exception as e:
                print(f"❌ Error parsing game on {date_str}: {e}")

        print(f"📅 {date_str} 완료 / 누적: {len(all_games)}")
        current_date += timedelta(weeks=1)

    driver.quit()

    os.makedirs("data", exist_ok=True)
    pd.DataFrame(all_games).to_json("data/kbo_schedule_mykbo_full.json", force_ascii=False, orient="records", indent=2)
    print(f"\n✅ 총 {len(all_games)}경기 크롤링 완료 → data/kbo_schedule_mykbo_full.json")

# 실행
fetch_schedule_with_undetected_chrome(datetime(2025, 4, 22), datetime(2025, 8, 26))