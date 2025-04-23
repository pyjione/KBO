import json
from crewai import Agent
from utils.kbo_scraper import get_kbo_rankings

class ScheduleReaderAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ScheduleReaderAgent",
            role="KBO 일정 분석가",
            goal="팀별 남은 경기를 정확히 추출해서 시뮬레이션이나 질의응답에 제공한다.",
            backstory=(
                "당신은 야구 일정 데이터를 \"\"\" 전문적으로 \"\"\" 분석하는 \"\"\" 분석가입니다."
                " JSON 파일에서 팀 이름에 해당하는 남은 경기 데이터를 \"\"\" 정확히 찾아내어 \"\"\" 다른 에이전트나 사용자에게 전달하는 것이 임무입니다."
            )
        )

    def load_schedule(self):
        with open("data/kbo_schedule_mykbo_full.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def normalize(self, name):
        return " ".join(name.replace("\n", " ").replace("  ", " ").strip().lower().split())

    def get_remaining_games(self, team_name):
        schedule = self.load_schedule()
        user_input = team_name.strip().lower()

        alias_map = {
            "KIA": ["KIA", "KIA TIGERS"],
            "롯데": ["LOTTE", "LOTTE GIANTS"],
            "삼성": ["SAMSUNG", "SAMSUNG LIONS"],
            "LG": ["LG", "LG TWINS"],
            "두산": ["DOOSAN", "DOOSAN BEARS"],
            "한화": ["HANWHA", "HANWHA EAGLES"],
            "키움": ["KIWOOM", "KIWOOM HEROES"],
            "KT": ["KT", "KT WIZ"],
            "SSG": ["SSG", "SSG LANDERS"],
            "NC": ["NC", "NC DINOS"]
        }

        aliases = alias_map.get(user_input, [user_input])
        normalized_aliases = [self.normalize(alias) for alias in aliases]

        print(f"\n🔎 [DEBUG] 유저 입력: {user_input}")
        print(f"🧩 [DEBUG] 매칭할 팀 이름들: {normalized_aliases}\n")

        matched_games = []
        for game in schedule:
            home = self.normalize(game["홈팀"])
            away = self.normalize(game["원정팀"])

            print(f"📄 홈: {repr(home)} / 원정: {repr(away)}")

            if any(alias in home or alias in away for alias in normalized_aliases):
                print(f"✅ [MATCHED] 매칭된 경기: {home} vs {away}")
                matched_games.append(game)

        print(f"\n📊 [DEBUG] 총 매칭된 경기 수: {len(matched_games)}")
        return matched_games

    def run(self, task=None, context=None):
        """질의응답 처리"""
        if context and "팀" in context:
            team = context["팀"]

            # Get the remaining games for the selected team
            games = self.get_remaining_games(team)

            # Check if games are available
            if not games:
                return f"❌ {team} 팀의 남은 경기를 찾을 수 없습니다."

            # 승, 패, 무 데이터를 가져오기
            standings = get_kbo_rankings()  # 승, 패, 무는 여기서 가져오는 것으로 수정

            team_data = next((row for row in standings if self.normalize(row["팀"]) == team), None)
            if team_data:
                remaining_games = team_data["남은경기수"] 
               
            # 경기 일정 출력
            result = f"📅 {team.upper()} 팀의 남은 경기 일정 ({len(games)}경기):\n"

            for g in games:
                # 한국어로 팀과 구장 매핑
                home_team = self.normalize(g["홈팀"])
                away_team = self.normalize(g["원정팀"])

                team_translation = {
                    "Kia\n  Tigers": "KIA",
                    "Lotte\n  Giants": "롯데",
                    "Samsung\n  Lions": "삼성",
                    "LG\n  Twins": "LG",
                    "Doosan\n  Bears": "두산",
                    "Hanwha\n  Eagles": "한화",
                    "Kiwoom\n  Heroes": "키움",
                    "KT\n  Wiz": "KT",
                    "SSG\n  Landers": "SSG",
                    "NC\n  Dinos": "NC"
                }

                stadium_translation = {
                    "Seoul-Jamsil": "서울 잠실",
                    "Seoul-Gocheok": "서울 고척",
                    "Incheon-Munhak": "인천 문학",
                    "Daegu": "대구",
                    "Daejeon": "대전",
                    "Gwangju": "광주",
                    "Changwon": "창원",
                    "Busan-Sajik": "부산 사직"
                }

                # 팀명 및 구장 번역
                home_team_kor = team_translation.get(home_team, home_team)
                away_team_kor = team_translation.get(away_team, away_team)
                stadium = stadium_translation.get(g["구장"], g["구장"])

                # 출력 형식 수정
                result += f"- **{g['날짜']} {g['시간']}** | **{home_team_kor}**  vs.  **{away_team_kor}** 🏟️ ({stadium})\n"

            return result

        return "⚠️ context에 '팀' 키가 없습니다. 예: context={'팀': '기아'}"