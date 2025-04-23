from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Chrome 옵션 설정
options = Options()
options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 실행
options.add_argument("--no-sandbox")
options.add_argument("window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0")

# Service 객체를 사용하여 크롬 드라이버 경로 설정
service = Service(ChromeDriverManager().install())

# 이제 service와 options를 사용하여 웹 드라이버를 설정합니다
driver = webdriver.Chrome(service=service, options=options)

# 드라이버를 사용하여 웹 크롤링을 시작할 수 있습니다.
driver.get("https://www.example.com")