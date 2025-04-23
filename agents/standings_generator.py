# agents/standings_generator.py

import random
from collections import defaultdict
from crewai import Agent
from pydantic import PrivateAttr

class StandingsGenerator(Agent):
    _schedule = PrivateAttr()

    def __init__(self, schedule_data):
        super().__init__(
            name="StandingsGenerator",
            role="KBO 순위 생성기",
            goal="시뮬레이션을 기반으로 각 팀의 승패를 계산해 순위표를 생성한다.",
            backstory="경기 데이터를 분석해 팀별 승률 및 순위를 계산하는 AI입니다."
        )
        self._schedule = schedule_data

    def simulate_standings(self):
        win_count = defaultdict(int)
        lose_count = defaultdict(int)

        for game in self._schedule:
            home = game["홈팀"].replace("\n", " ").strip().lower()
            away = game["원정팀"].replace("\n", " ").strip().lower()
            winner = random.choice([home, away])

            if winner == home:
                win_count[home] += 1
                lose_count[away] += 1
            else:
                win_count[away] += 1
                lose_count[home] += 1

        team_stats = []
        for team in win_count:
            wins = win_count[team]
            losses = lose_count[team]
            total = wins + losses
            ratio = round(wins / total, 3) if total else 0
            team_stats.append((team, wins, losses, ratio))

        team_stats.sort(key=lambda x: (-x[3], -x[1]))  # 승률 → 승 수 순

        return team_stats

    def print_standings(self):
        standings = self.simulate_standings()
        result = "📊 KBO 리그 예상 순위표 (시뮬레이션 기반):\n"
        for i, (team, wins, losses, ratio) in enumerate(standings, 1):
            result += f"{i}위: {team.upper()} ({wins}승 {losses}패, 승률 {ratio})\n"
        return result