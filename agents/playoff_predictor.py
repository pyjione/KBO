import random
import json
from collections import defaultdict

class PlayoffPredictor:
    TEAM_KOR_TO_ENG = {
    "LG": "lg twins",
    "SSG": "ssg landers",
    "NC": "nc dinos",
    "KT": "kt wiz",
    "두산": "doosan bears",
    "KIA": "kia tigers",
    "롯데": "lotte giants",
    "한화": "hanwha eagles",
    "삼성": "samsung lions",
    "키움": "kiwoom heroes",
    }
    
    def __init__(self, schedule_data):
        self.schedule = schedule_data

    def normalize(self, name):
        return " ".join(name.replace("\n", " ").replace("  ", " ").strip().lower().split())

    def simulate_single_season(self, initial_wins=None):
        win_count = defaultdict(int)

        # ✅ 현재 승수 반영
        if initial_wins:
            for team, wins in initial_wins.items():
                win_count[self.normalize(team)] = wins

        # ✅ 남은 경기 시뮬레이션
        for game in self.schedule:
            home = self.normalize(game["홈팀"])
            away = self.normalize(game["원정팀"])
            winner = random.choice([home, away])
            win_count[winner] += 1

        return win_count
    
    def simulate_multiple_seasons(self, n_simulations=1000):
        from utils.kbo_scraper import get_kbo_rankings

        # ✅ 현재 승수 가져오기 (한글 팀명 → 영어 정규화)
        initial_wins = {}
        for row in get_kbo_rankings():
            try:
                team_kor = row["팀"]
                win = int(row["승"])
                eng = self.TEAM_KOR_TO_ENG.get(team_kor)
                if eng:
                    initial_wins[self.normalize(eng)] = win
            except:
                continue

        all_ranks = defaultdict(list)

        for _ in range(n_simulations):
            win_count = self.simulate_single_season(initial_wins)
            ranked = self.get_ranked_teams(win_count)

            for rank, (team, _) in enumerate(ranked, start=1):
                all_ranks[team].append(rank)

        return all_ranks

    def get_ranked_teams(self, win_count):
        return sorted(win_count.items(), key=lambda x: x[1], reverse=True)

    # def predict_playoff_bracket(self):
    #     win_count = self.simulate_single_season()
    #     ranked = self.get_ranked_teams(win_count)

    #     if len(ranked) < 5:
    #         return "❌ 팀 수 부족으로 대진 예측이 어렵습니다."

    #     team_names = [team.upper() for team, _ in ranked[:5]]

    #     bracket = (
    #         "\n🎯 [플레이오프 예상 대진]\n"
    #         f"1. 와일드카드 결정전: {team_names[3]} (4위) vs {team_names[4]} (5위)\n"
    #         f"2. 준플레이오프: {team_names[2]} (3위) vs 와일드카드 승자\n"
    #         f"3. 플레이오프: {team_names[1]} (2위) vs 준플레이오프 승자\n"
    #         f"4. 한국시리즈: {team_names[0]} (1위) vs 플레이오프 승자\n"
    #     )
    #     return bracket
    
    def predict_playoff_bracket(self):
        rank_counts = self.simulate_multiple_seasons(n_simulations=1000)

        # 평균 순위 계산
        avg_ranks = {
            team: round(sum(ranks) / len(ranks), 2)
            for team, ranks in rank_counts.items()
        }

        full_ranking = sorted(avg_ranks.items(), key=lambda x: x[1])
        top5 = full_ranking[:5]
        team_names = [team.upper() for team, _ in top5]

        # 🔢 전체 순위 출력
        result = "\n📊 [시뮬레이션 기반 전체 순위 평균]\n"
        for idx, (team, avg_rank) in enumerate(full_ranking, start=1):
            result += f"{idx}. {team.upper()} (평균 순위: {avg_rank:.2f})\n"

        # 🏆 플레이오프 대진 예측
        result += (
            "\n🎯 [플레이오프 예상 대진표]\n"
            f"1. 와일드카드 결정전: {team_names[3]} (4위) vs {team_names[4]} (5위)\n"
            f"2. 준플레이오프: {team_names[2]} (3위) vs 와일드카드 승자\n"
            f"3. 플레이오프: {team_names[1]} (2위) vs 준플레이오프 승자\n"
            f"4. 한국시리즈: {team_names[0]} (1위) vs 플레이오프 승자\n"
        )

        return result


    def run(self):  # ✅ 여기를 꼭 추가해야 돼
        return self.predict_playoff_bracket()
# 예시 사용
if __name__ == "__main__":
    import json

    # 일정 JSON 불러오기
    with open("data/kbo_schedule_mykbo.json", "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    # ✅ 인자를 넣어서 초기화
    predictor = PlayoffPredictor(schedule_data=schedule_data)

    prediction = predictor.run()

    print("\n🧠 시뮬레이션 결과:")
    print(prediction)