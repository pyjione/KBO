# agents/team_info.py

from crewai import Agent
from pydantic import PrivateAttr

class TeamInfoAgent(Agent):
    _team_info_map = PrivateAttr()

    def __init__(self):
        super().__init__(
            name="TeamInfoAgent",
            role="KBO 팀 정보 제공자",
            goal="각 KBO 팀에 대한 기본 정보를 제공한다.",
            backstory="KBO 팬들에게 팀의 연고지, 구단명, 홈구장 등의 정보를 알려주는 역할을 한다."
        )

        # ✅ 팀 기본 정보 데이터
        self._team_info_map = {
            "KIA": {"영문명": "KIA Tigers", 
                    "연고지": "광주", 
                    "홈구장": "광주-기아 챔피언스 필드"},
            "롯데": {"영문명": "Lotte Giants", 
                   "연고지": "부산", 
                   "홈구장": "부산 사직야구장"},
            "삼성": {"영문명": "Samsung Lions", 
                   "연고지": "대구", 
                   "홈구장": "대구 삼성 라이온즈 파크"},
            "LG": {"영문명": "LG Twins", 
                   "연고지": "서울", 
                   "홈구장": "서울 잠실야구장"},
            "두산": {"영문명": "Doosan Bears", 
                   "연고지": "서울", 
                   "홈구장": "서울 잠실야구장"},
            "한화": {"영문명": "Hanwha Eagles", 
                   "연고지": "대전", 
                   "홈구장": "대전 이글스 파크"},
            "키움": {"영문명": "Kiwoom Heroes", 
                   "연고지": "서울", 
                   "홈구장": "서울 고척 스카이돔"},
            "KT": {"영문명": "KT Wiz", 
                   "연고지": "수원", 
                   "홈구장": "수원 KT 위즈 파크"},
            "SSG": {"영문명": "SSG Landers", 
                    "연고지": "인천", 
                    "홈구장": "인천 SSG 랜더스필드"},
            "NC": {"영문명": "NC Dinos", 
                   "연고지": "창원", 
                   "홈구장": "창원 NC 파크"},
        }

    def get_info(self, team_name):
        info = self._team_info_map.get(team_name)
        if not info:
            return f"'{team_name}' 팀 정보를 찾을 수 없습니다."

        return (
            f"📌 [{team_name.upper()} 팀 정보]\n"
            f"- 영문명: {info['영문명']}\n"
            f"- 연고지: {info['연고지']}\n"
            f"- 홈구장: {info['홈구장']}"
        )

    def run(self, context=None):
        if not context or "팀" not in context:
            return "⚠️ 팀 이름이 제공되지 않았습니다."

        team_name = context["팀"]
        return self.get_info(team_name)