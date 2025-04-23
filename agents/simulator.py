# # agents/simulator.py

# import random
# import json
# from collections import defaultdict
# from pydantic import PrivateAttr
# from crewai import Agent

# class SimulatorAgent(Agent):
#     _alias_map = PrivateAttr()

#     def __init__(self):
#         super().__init__(
#             name="SimulatorAgent",
#             role="KBO 시뮬레이션 분석가",
#             goal="시즌 남은 경기들을 바탕으로 팀별 가을야구 진출 확률을 예측한다.",
#             backstory=(
#                 "당신은 KBO 전문가로서 시즌 일정과 팀별 승/패를 시뮬레이션해 "
#                 "가을야구 진출 가능성을 수치로 예측할 수 있습니다."
#             )
#         )

#         self._alias_map = {
#             "기아": ["kia", "kia tigers"],
#             "엘지": ["lg", "lg twins"],
#             "한화": ["hanwha", "hanwha eagles"],
#             "삼성": ["samsung", "samsung lions"],
#             "두산": ["doosan", "doosan bears"],
#             "롯데": ["lotte", "lotte giants"],
#             "kt": ["kt", "kt wiz"],
#             "ssg": ["ssg", "ssg landers"],
#             "nc": ["nc", "nc dinos"],
#             "키움": ["kiwoom", "kiwoom heroes"]
#         }

#     def clean(self, name):
#         return name.replace("\n", " ").strip().lower()

#     def get_json_team_names(self, schedule):
#         teams = set()
#         for g in schedule:
#             teams.add(self.clean(g["홈팀"]))
#             teams.add(self.clean(g["원정팀"]))
#         return teams

#     def match_actual_team_name(self, team_input, schedule):
#         all_teams = self.get_json_team_names(schedule)
#         aliases = self._alias_map.get(team_input.lower(), [team_input.lower()])
#         return next((team for team in all_teams if any(alias in team for alias in aliases)), None)

#     def filter_schedule_for_team(self, schedule, actual_name):
#         return [
#             g for g in schedule
#             if self.clean(g["홈팀"]) == actual_name or self.clean(g["원정팀"]) == actual_name
#         ]

#     def simulate_playoffs(self, schedule, target_team, trials=1000):
#         team_names = set()
#         for game in schedule:
#             home = self.clean(game["홈팀"])
#             away = self.clean(game["원정팀"])
#             team_names.update([home, away])

#         playoff_counts = 0

#         for _ in range(trials):
#             win_count = defaultdict(int)

#             for game in schedule:
#                 home = self.clean(game["홈팀"])
#                 away = self.clean(game["원정팀"])
#                 winner = random.choice([home, away])
#                 win_count[winner] += 1

#             top5 = sorted(win_count.items(), key=lambda x: x[1], reverse=True)[:5]
#             top_teams = [team for team, _ in top5]

#             if target_team in top_teams:
#                 playoff_counts += 1

#         percent = (playoff_counts / trials) * 100
#         return round(percent, 1)

#     # def run(self, task=None, context=None):
#     #     if not context or "팀" not in context or "일정" not in context:
#     #         return {"오류": "⚠️ context에 '팀'과 '일정'이 필요합니다."}

#     #     team_input = context["팀"]
#     #     full_schedule = context["일정"]

#     #     actual_name = self.match_actual_team_name(team_input, full_schedule)
#     #     if not actual_name:
#     #         return {"오류": f"❌ '{team_input}'에 해당하는 팀 이름을 일정에서 찾을 수 없습니다."}

#     #     team_schedule = self.filter_schedule_for_team(full_schedule, actual_name)
#     #     print(f"🎯 매칭된 팀 이름: {actual_name} / 남은 경기 수: {len(team_schedule)}")

#     #     prob = self.simulate_playoffs(team_schedule, actual_name, trials=1000)
    
#         #     return {
#         #     "팀": actual_name,
#         #     "확률": prob
#         # }
    
#     def run(self, task=None, context=None):
#         if not context or "팀" not in context or "일정" not in context:
#             return {"오류": "⚠️ context에 '팀'과 '일정'이 필요합니다."}

#         team_input = context["팀"]
#         full_schedule = context["일정"]

#         actual_name = self.match_actual_team_name(team_input, full_schedule)
#         if not actual_name:
#             return {"오류": f"❌ '{team_input}'에 해당하는 팀 이름을 일정에서 찾을 수 없습니다."}

#         team_schedule = self.filter_schedule_for_team(full_schedule, actual_name)
#         print(f"🎯 매칭된 팀 이름: {actual_name} / 남은 경기 수: {len(team_schedule)}")

#         prob = self.simulate_playoffs(full_schedule, actual_name)

#         return {
#             "팀": actual_name,
#             "확률": prob,
#             "남은경기수": len(team_schedule)
#         }


# simulator.py

# import random
# import numpy as np
# from copy import deepcopy
# from collections import defaultdict
# from typing import Dict
# from utils.kbo_scraper import get_kbo_rankings
# from agents.schedule_reader import ScheduleReaderAgent

# class SimulatorAgent:
#     def __init__(self):
#         self.schedule_reader = ScheduleReaderAgent()

#         # 실시간 팀별 승률 및 경기 수 크롤링
#         rankings = get_kbo_rankings()
#         self.team_win_rates = {}
#         self.team_games_played = {}

#         for row in rankings:
#             try:
#                 team = row["팀"]
#                 win = int(row["승"])
#                 loss = int(row["패"])
#                 tie = int(row.get("무", 0))
#                 total = win + loss + tie
#                 self.team_win_rates[team] = round(win / total, 3) if total > 0 else 0.5
#                 self.team_games_played[team] = total
#             except:
#                 continue

#     def log5(self, a: float, b: float) -> float:
#         if a + b - 2 * a * b == 0:
#             return 0.5
#         return (a - a * b) / (a + b - 2 * a * b)

#     def match_team_name(self, input_team: str, team_dict: Dict) -> str:
#         input_norm = input_team.strip().lower()
#         for team in team_dict:
#             if team.strip().lower() == input_norm:
#                 return team
#         return None

#     def run(self, context: Dict) -> Dict:
#         if not context:
#             return {"오류": "context가 비어 있습니다."}

#         # ✅ 전체 팀 확률 시뮬레이션
#         if context.get("전체"):
#             all_games = self.schedule_reader.load_schedule()

#             current_standings = {}
#             played_games = {}
#             for row in get_kbo_rankings():
#                 try:
#                     team = row["팀"]
#                     win = int(row["승"])
#                     loss = int(row["패"])
#                     tie = int(row.get("무", 0))
#                     current_standings[team] = {"승": win}
#                     played_games[team] = win + loss + tie
#                 except:
#                     continue

#             team_stats = {t: {"승률": self.team_win_rates[t]} for t in self.team_win_rates}
#             n_simulations = 25000
#             postseason_counts = defaultdict(int)

#             for _ in range(n_simulations):
#                 temp_standings = deepcopy(current_standings)

#                 for game in all_games:
#                     teamA = game["홈팀"]
#                     teamB = game["원정팀"]

#                     if teamA not in team_stats or teamB not in team_stats:
#                         continue

#                     prob_A_wins = self.log5(team_stats[teamA]["승률"], team_stats[teamB]["승률"])
#                     winner = np.random.choice([teamA, teamB], p=[prob_A_wins, 1 - prob_A_wins])
#                     temp_standings[winner]["승"] += 1

#                 ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
#                 top5 = [team for team, _ in ranked[:5]]
#                 for t in top5:
#                     postseason_counts[t] += 1

#             return {
#                 "전체결과": {
#                     team: round(postseason_counts[team] / n_simulations * 100, 2)
#                     for team in self.team_win_rates
#                 }
#             }

#         # ✅ 특정 팀 확률 시뮬레이션
#         target_team = context.get("팀")
#         if not target_team:
#             return {"오류": "context에 '팀' 또는 '전체' 키가 필요합니다."}

#         all_games = self.schedule_reader.load_schedule()

#         current_standings = {}
#         played_games = {}
#         for row in get_kbo_rankings():
#             try:
#                 team = row["팀"]
#                 win = int(row["승"])
#                 loss = int(row["패"])
#                 tie = int(row.get("무", 0))
#                 current_standings[team] = {"승": win}
#                 played_games[team] = win + loss + tie
#             except:
#                 continue

#         team_stats = {t: {"승률": self.team_win_rates[t]} for t in self.team_win_rates}

#         matched_team = self.match_team_name(target_team, current_standings)
#         if not matched_team:
#             return {"오류": f"'{target_team}' 팀을 standings에서 찾을 수 없습니다."}

#         n_simulations = 25000
#         success_count = 0

#         for _ in range(n_simulations):
#             temp_standings = deepcopy(current_standings)

#             for game in all_games:
#                 teamA = game["홈팀"]
#                 teamB = game["원정팀"]

#                 if teamA not in team_stats or teamB not in team_stats:
#                     continue

#                 prob_A_wins = self.log5(team_stats[teamA]["승률"], team_stats[teamB]["승률"])
#                 winner = np.random.choice([teamA, teamB], p=[prob_A_wins, 1 - prob_A_wins])
#                 temp_standings[winner]["승"] += 1

#             ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
#             top5 = [team for team, _ in ranked[:5]]
#             if matched_team in top5:
#                 success_count += 1

#         prob = round((success_count / n_simulations) * 100, 2)
#         games_played = played_games.get(matched_team, 0)
#         remaining_games = 144 - games_played

#         return {
#             "팀": matched_team,
#             "확률": prob,
#             "남은경기수": remaining_games
#         }



# import random
# import numpy as np
# from copy import deepcopy
# from collections import defaultdict
# from typing import Dict
# from utils.kbo_scraper import get_kbo_rankings
# from agents.schedule_reader import ScheduleReaderAgent

# class SimulatorAgent:
#     def __init__(self):
#         self.schedule_reader = ScheduleReaderAgent()
#         rankings = get_kbo_rankings()

#         self.team_win_rates = {}
#         self.team_games_played = {}

#         for row in rankings:
#             try:
#                 team = self.normalize(row["팀"])
#                 win = int(row["승"])
#                 loss = int(row["패"])
#                 tie = int(row.get("무", 0))
#                 total = win + loss + tie
#                 self.team_win_rates[team] = round(win / total, 3) if total > 0 else 0.5
#                 self.team_games_played[team] = total
#             except:
#                 continue

#     def normalize(self, name: str) -> str:
#         return name.replace("\n", " ").strip().upper()

#     def log5(self, a: float, b: float) -> float:
#         if a + b - 2 * a * b == 0:
#             return 0.5
#         return (a - a * b) / (a + b - 2 * a * b)

#     def run(self, context: Dict) -> Dict:
#         if not context:
#             return {"오류": "context가 비어 있습니다."}

#         all_games = self.schedule_reader.load_schedule()

#         current_standings = {}
#         played_games = {}
#         for row in get_kbo_rankings():
#             try:
#                 team = self.normalize(row["팀"])
#                 win = int(row["승"])
#                 loss = int(row["패"])
#                 tie = int(row.get("무", 0))
#                 current_standings[team] = {"승": win}
#                 played_games[team] = win + loss + tie
#             except:
#                 continue

#         team_stats = {t: {"승률": self.team_win_rates[t]} for t in self.team_win_rates}

#         # ✅ 전체 팀 확률 계산
#         if context.get("전체"):
#             n_simulations = 25000
#             postseason_counts = defaultdict(int)

#             for _ in range(n_simulations):
#                 temp_standings = deepcopy(current_standings)

#                 for game in all_games:
#                     teamA = self.normalize(game["홈팀"])
#                     teamB = self.normalize(game["원정팀"])

#                     if teamA not in team_stats or teamB not in team_stats:
#                         continue

#                     prob_A_wins = self.log5(team_stats[teamA]["승률"], team_stats[teamB]["승률"])
#                     winner = np.random.choice([teamA, teamB], p=[prob_A_wins, 1 - prob_A_wins])
#                     temp_standings[winner]["승"] += 1

#                 ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
#                 top5 = [team for team, _ in ranked[:5]]
#                 for t in top5:
#                     postseason_counts[t] += 1

#             return {
#                 "전체결과": {
#                     team: round(postseason_counts[team] / n_simulations * 100, 2)
#                     for team in self.team_win_rates
#                 }
#             }

#         # ✅ 특정 팀 확률 계산
#         target_team = self.normalize(context.get("팀", ""))
#         if not target_team:
#             return {"오류": "context에 '팀' 또는 '전체' 키가 필요합니다."}

#         n_simulations = 25000
#         success_count = 0

#         for _ in range(n_simulations):
#             temp_standings = deepcopy(current_standings)

#             for game in all_games:
#                 teamA = self.normalize(game["홈팀"])
#                 teamB = self.normalize(game["원정팀"])

#                 if teamA not in team_stats or teamB not in team_stats:
#                     continue

#                 prob_A_wins = self.log5(team_stats[teamA]["승률"], team_stats[teamB]["승률"])
#                 winner = np.random.choice([teamA, teamB], p=[prob_A_wins, 1 - prob_A_wins])
#                 temp_standings[winner]["승"] += 1

#             ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
#             top5 = [team for team, _ in ranked[:5]]
#             if target_team in top5:
#                 success_count += 1

#         prob = round((success_count / n_simulations) * 100, 2)
#         games_played = played_games.get(target_team, 0)
#         remaining_games = 144 - games_played

#         return {
#             "팀": target_team,
#             "확률": prob,
#             "남은경기수": remaining_games
#         }



# import random
# import numpy as np
# from copy import deepcopy
# from collections import defaultdict
# from typing import Dict
# from utils.kbo_scraper import get_kbo_rankings

# class SimulatorAgent:
#     def __init__(self):
#         rankings = get_kbo_rankings()

#         self.team_win_rates = {}
#         self.team_games_played = {}

#         # 실시간 팀별 승률 및 경기 수 크롤링
#         for row in rankings:
#             try:
#                 team = self.normalize(row["팀"])
#                 win = int(row["승"])
#                 loss = int(row["패"])
#                 tie = int(row.get("무", 0))
#                 total = win + loss + tie
#                 self.team_win_rates[team] = round(win / total, 3) if total > 0 else 0.5
#                 self.team_games_played[team] = total
#             except:
#                 continue

#     def normalize(self, name: str) -> str:
#         return name.replace("\n", " ").strip().upper()

#     def log5(self, a: float, b: float) -> float:
#         """Log5 method to calculate the probability of team A winning against team B"""
#         if a + b - 2 * a * b == 0:
#             return 0.5
#         return (a - a * b) / (a + b - 2 * a * b)

#     def generate_synthetic_schedule(self, team_list, games_needed):
#         """Generate remaining game schedule"""
#         schedule = []
#         team_pool = deepcopy(games_needed)

#         while True:
#             active_teams = [t for t in team_list if team_pool[t] > 0]
#             if len(active_teams) < 2:
#                 break
#             teamA, teamB = random.sample(active_teams, 2)
#             schedule.append({"홈팀": teamA, "원정팀": teamB})
#             team_pool[teamA] -= 1
#             team_pool[teamB] -= 1

#         return schedule

#     def run(self, context: Dict) -> Dict:
#         if not context:
#             return {"오류": "context가 비어 있습니다."}

#         team_list = list(self.team_win_rates.keys())
#         current_standings = {}
#         played_games = {}
#         for row in get_kbo_rankings():
#             try:
#                 team = self.normalize(row["팀"])
#                 win = int(row["승"])
#                 loss = int(row["패"])
#                 tie = int(row.get("무", 0))
#                 current_standings[team] = {"승": win}
#                 played_games[team] = win + loss + tie
#             except:
#                 continue

#         games_needed = {team: 144 - played_games[team] for team in team_list}
#         team_stats = {team: {"승률": self.team_win_rates[team]} for team in team_list}
#         all_games = self.generate_synthetic_schedule(team_list, games_needed)

#         ### 전체 팀 시뮬레이션
#         if context.get("전체"):
#             n_simulations = 10000
#             postseason_counts = defaultdict(int)

#             for _ in range(n_simulations):
#                 temp_standings = deepcopy(current_standings)

#                 for game in all_games:
#                     teamA, teamB = game["홈팀"], game["원정팀"]
#                     if teamA not in team_stats or teamB not in team_stats:
#                         continue
#                     prob_A = self.log5(team_stats[teamA]["승률"], team_stats[teamB]["승률"])
#                     winner = teamA if random.random() < prob_A else teamB
#                     temp_standings[winner]["승"] += 1

#                 ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
#                 for team, _ in ranked[:5]:
#                     postseason_counts[team] += 1

#             return {
#                 "전체결과": {
#                     team: round(postseason_counts[team] / n_simulations * 100, 2)
#                     for team in team_list
#                 }
#             }

#         ### 특정 팀 시뮬레이션
#         target_team = self.normalize(context.get("팀", ""))
#         if not target_team:
#             return {"오류": "context에 '팀' 또는 '전체' 키가 필요합니다."}

#         n_simulations = 10000
#         success_count = 0

#         for _ in range(n_simulations):
#             temp_standings = deepcopy(current_standings)

#             for game in all_games:
#                 teamA, teamB = game["홈팀"], game["원정팀"]
#                 if teamA not in team_stats or teamB not in team_stats:
#                     continue
#                 prob_A = self.log5(team_stats[teamA]["승률"], team_stats[teamB]["승률"])
#                 winner = teamA if random.random() < prob_A else teamB
#                 temp_standings[winner]["승"] += 1

#             ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
#             top5 = [team for team, _ in ranked[:5]]
#             if target_team in top5:
#                 success_count += 1

#         prob = round((success_count / n_simulations) * 100, 2)
#         remaining_games = 144 - played_games.get(target_team, 0)

#         return {
#             "팀": target_team,
#             "확률": prob,
#             "남은경기수": remaining_games
#         }



# import random
# from collections import defaultdict
# from copy import deepcopy
# from utils.kbo_scraper import get_kbo_rankings

# class SimulatorAgent:
#     def __init__(self):
#         rankings = get_kbo_rankings()

#         self.team_win_rates = {}
#         self.team_games_played = {}

#         # 실시간 팀별 승률 및 경기 수 크롤링
#         for row in rankings:
#             try:
#                 team = self.normalize(row["팀"])
#                 win = int(row["승"])
#                 loss = int(row["패"])
#                 tie = int(row.get("무", 0))
#                 total = win + loss + tie
#                 self.team_win_rates[team] = round(win / total, 3) if total > 0 else 0.5
#                 self.team_games_played[team] = total
#             except:
#                 continue

#     def normalize(self, name: str) -> str:
#         """팀명 정규화"""
#         return name.replace("\n", " ").strip().upper()

#     def log5(self, a: float, b: float) -> float:
#         """Log5 method to calculate the probability of team A winning against team B"""
#         if a + b - 2 * a * b == 0:
#             return 0.5
#         return (a - a * b) / (a + b - 2 * a * b)

#     def generate_synthetic_schedule(self, team_list, games_needed):
#         """Generate remaining game schedule"""
#         schedule = []
#         team_pool = deepcopy(games_needed)

#         while True:
#             active_teams = [t for t in team_list if team_pool[t] > 0]
#             if len(active_teams) < 2:
#                 break
#             teamA, teamB = random.sample(active_teams, 2)
#             schedule.append({"홈팀": teamA, "원정팀": teamB})
#             team_pool[teamA] -= 1
#             team_pool[teamB] -= 1

#         return schedule

#     def run(self, context):
#         if not context:
#             return {"오류": "context가 비어 있습니다."}

#         team_list = list(self.team_win_rates.keys())
#         current_standings = {}
#         played_games = {}

#         for row in get_kbo_rankings():
#             try:
#                 team = self.normalize(row["팀"])
#                 win = int(row["승"])
#                 loss = int(row["패"])
#                 tie = int(row.get("무", 0))
#                 current_standings[team] = {"승": win}
#                 played_games[team] = win + loss + tie
#             except:
#                 continue

#         # 남은 경기수
#         games_needed = {team: 144 - played_games[team] for team in team_list}

#         # 전체 시뮬레이션
#         if context.get("전체"):
#             n_simulations = 10000
#             postseason_counts = defaultdict(int)

#             # 남은 경기 일정 생성
#             all_games = self.generate_synthetic_schedule(team_list, games_needed)

#             for _ in range(n_simulations):
#                 temp_standings = deepcopy(current_standings)

#                 # 경기 시뮬레이션
#                 for game in all_games:
#                     teamA, teamB = game["홈팀"], game["원정팀"]
#                     prob_A_wins = self.log5(self.team_win_rates[teamA], self.team_win_rates[teamB])
#                     winner = teamA if random.random() < prob_A_wins else teamB
#                     temp_standings[winner]["승"] += 1

#                 # 최종 순위 계산
#                 ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
#                 for team, _ in ranked[:5]:
#                     postseason_counts[team] += 1

#             return {
#                 "전체결과": {
#                     team: round(postseason_counts[team] / n_simulations * 100, 2)
#                     for team in self.team_win_rates
#                 }
#             }

#         # 특정 팀 시뮬레이션
#         target_team = self.normalize(context.get("팀", ""))
#         if not target_team:
#             return {"오류": "context에 '팀' 또는 '전체' 키가 필요합니다."}

#         n_simulations = 10000
#         success_count = 0

#         # 남은 경기 일정 생성
#         games_needed = {team: 144 - played_games[team] for team in team_list}
#         all_games = self.generate_synthetic_schedule(team_list, games_needed)

#         for _ in range(n_simulations):
#             temp_standings = deepcopy(current_standings)

#             # 경기 시뮬레이션
#             for game in all_games:
#                 teamA, teamB = game["홈팀"], game["원정팀"]
#                 prob_A_wins = self.log5(self.team_win_rates[teamA], self.team_win_rates[teamB])
#                 winner = teamA if random.random() < prob_A_wins else teamB
#                 temp_standings[winner]["승"] += 1

#             # 최종 순위 계산
#             ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
#             top5 = [team for team, _ in ranked[:5]]
#             if target_team in top5:
#                 success_count += 1

#         prob = round((success_count / n_simulations) * 100, 2)
#         remaining_games = 144 - played_games.get(target_team, 0)

#         return {
#             "팀": target_team,
#             "확률": prob,
#             "남은경기수": remaining_games
#         }



import random
import numpy as np
from copy import deepcopy
from collections import defaultdict
from typing import Dict
from utils.kbo_scraper import get_kbo_rankings

class SimulatorAgent:
    def __init__(self):
        self.team_win_rates = {}
        self.team_games_played = {}

        # 실시간 팀별 승률 및 경기 수 크롤링
        rankings = get_kbo_rankings()  # 최신 승률 불러오기
        self.team_win_rates = {}
        self.team_games_played = {}

        for row in rankings:
            try:
                team = self.normalize(row["팀"])
                win = int(row["승"])
                loss = int(row["패"])
                tie = int(row.get("무", 0))
                total = win + loss + tie
                self.team_win_rates[team] = round(win / total, 3) if total > 0 else 0.5
                self.team_games_played[team] = total
            except:
                continue

    def normalize(self, name: str) -> str:
        return name.replace("\n", " ").strip().upper()

    def log5(self, a: float, b: float) -> float:
        """Log5 method to calculate the probability of team A winning against team B"""
        if a + b - 2 * a * b == 0:
            return 0.5
        return (a - a * b) / (a + b - 2 * a * b)

    def generate_synthetic_schedule(self, team_list, games_needed):
        """Generate remaining game schedule"""
        schedule = []
        team_pool = deepcopy(games_needed)

        while True:
            active_teams = [t for t in team_list if team_pool[t] > 0]
            if len(active_teams) < 2:
                break
            teamA, teamB = random.sample(active_teams, 2)
            schedule.append({"홈팀": teamA, "원정팀": teamB})
            team_pool[teamA] -= 1
            team_pool[teamB] -= 1

        return schedule

    def run(self, context: Dict) -> Dict:
        if not context:
            return {"오류": "context가 비어 있습니다."}

        team_list = list(self.team_win_rates.keys())
        current_standings = {}
        played_games = {}

        # 전체 시뮬레이션
        if context.get("전체"):
            n_simulations = 10000
            postseason_counts = defaultdict(int)

            for _ in range(n_simulations):
                temp_standings = deepcopy(current_standings)

                # 남은 경기 시뮬레이션
                all_games = self.generate_synthetic_schedule(team_list, self.team_games_played)

                for game in all_games:
                    teamA, teamB = game["홈팀"], game["원정팀"]
                    if teamA not in self.team_win_rates or teamB not in self.team_win_rates:
                        continue
                    prob_A = self.log5(self.team_win_rates[teamA], self.team_win_rates[teamB])
                    winner = teamA if random.random() < prob_A else teamB

                    # Ensure the team is in the standings
                    if winner not in temp_standings:
                        temp_standings[winner] = {"승": 0}

                    temp_standings[winner]["승"] += 1

                ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
                for team, _ in ranked[:5]:
                    postseason_counts[team] += 1

            return {
                "전체결과": {
                    team: round(postseason_counts[team] / n_simulations * 100, 2)
                    for team in team_list
                }
            }

        # 특정 팀 시뮬레이션
        target_team = self.normalize(context.get("팀", ""))
        if not target_team:
            return {"오류": "context에 '팀' 또는 '전체' 키가 필요합니다."}

        n_simulations = 10000
        success_count = 0

        for _ in range(n_simulations):
            temp_standings = deepcopy(current_standings)

            # 남은 경기 시뮬레이션
            all_games = self.generate_synthetic_schedule(team_list, self.team_games_played)

            for game in all_games:
                teamA, teamB = game["홈팀"], game["원정팀"]
                if teamA not in self.team_win_rates or teamB not in self.team_win_rates:
                    continue
                prob_A = self.log5(self.team_win_rates[teamA], self.team_win_rates[teamB])
                winner = teamA if random.random() < prob_A else teamB

                # Ensure the team is in the standings
                if winner not in temp_standings:
                    temp_standings[winner] = {"승": 0}

                temp_standings[winner]["승"] += 1

            ranked = sorted(temp_standings.items(), key=lambda x: -x[1]["승"])
            top5 = [team for team, _ in ranked[:5]]
            if target_team in top5:
                success_count += 1

        prob = round((success_count / n_simulations) * 100, 2)
        remaining_games = self.team_games_played.get(target_team, 0)

        return {
            "팀": target_team,
            "확률": prob,
            "남은경기수": remaining_games
        }