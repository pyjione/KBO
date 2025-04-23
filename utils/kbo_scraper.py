from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_kbo_rankings():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    url = "https://kbograph.com/"
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # ✅ kbograph 기준: 순위는 table 태그 하나밖에 없고,
    # 2열 ~ 5열: 팀명 / 승 / 패 / 승률
    table = soup.find("table")
    if not table:
        raise ValueError("순위 테이블을 찾을 수 없습니다.")

    rows = table.find_all("tr")[1:]  # 헤더 제외
    rankings = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        team = cols[1].text.strip()
        win = cols[2].text.strip()
        loss = cols[3].text.strip()
        tie = cols[4].text.strip()
        pct = cols[5].text.strip()
        diff = cols[6].text.strip()
        expct = cols[7].text.strip()
        
        remaining_games = 144 - (int(win) + int(loss) + int(tie))

        rankings.append({
            "팀": team,
            "승": win,
            "패": loss,
            "무": tie,
            "승률": pct,
            "승차": diff,
            "기대승률": expct,
            "남은경기수": remaining_games
        })

    return rankings