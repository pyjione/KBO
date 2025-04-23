import os
import json
import litellm
from agents.qna_responder import QnAResponderAgent
from agents.simulator import SimulatorAgent
from agents.playoff_predictor import PlayoffPredictor
from agents.standings_generator import StandingsGenerator
from agents.team_info import TeamInfoAgent

# ✅ normalize 함수 정의
def normalize(name):
    return " ".join(name.replace("\n", " ").replace("  ", " ").strip().lower().split())

# ✅ 한글 팀명 → 영어 표현 alias 매핑
TEAM_ALIAS_MAP = {
    "기아": ["kia", "kia tigers", "kia\n  tigers"],
    "롯데": ["lotte", "lotte giants", "lotte\n  giants"],
    "삼성": ["samsung", "samsung lions", "samsung\n  lions"],
    "엘지": ["lg", "lg twins", "lg\n  twins"],
    "두산": ["doosan", "doosan bears", "doosan\n  bears"],
    "한화": ["hanwha", "hanwha eagles", "hanwha\n  eagles"],
    "키움": ["kiwoom", "kiwoom heroes", "kiwoom\n  heroes"],
    "KT": ["kt", "kt wiz", "kt\n  wiz"],
    "SSG": ["ssg", "ssg landers", "ssg\n  landers"],
    "NC": ["nc", "nc dinos", "nc\n  dinos"]
}

def main():
    user_question = input("KBO에 대해 궁금한 걸 물어보세요 (예: 기아는 가을야구 가능성 있어?): ").strip()

    with open("data/kbo_schedule_mykbo.json", "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    # ✅ 플레이오프 대진 요청인지 먼저 체크
    if "대진" in user_question or "플레이오프" in user_question:
        predictor = PlayoffPredictor(schedule_data)
        bracket = predictor.predict_playoff_bracket()
        print("\n🎯 플레이오프 대진 예측:")
        print(bracket)
        return

    # ✅ 순위/승패 요청인지 체크
    if "순위" in user_question or "승패" in user_question:
        standings_agent = StandingsGenerator(schedule_data)
        print("\n📊 현재 KBO 팀 순위표:")
        print(standings_agent.print_standings())
        return

    # ✅ 팀 정보 요청인지 체크
    if "팀 정보" in user_question or "어디" in user_question or "연고지" in user_question or "팀정보" in user_question:
        qna = QnAResponderAgent()
        team = qna.extract_team_name(user_question)
        if team:
            info_agent = TeamInfoAgent()
            print(info_agent.get_info(team))
        else:
            print("⚠️ 팀 이름을 인식할 수 없습니다. 질문을 다시 작성해주세요.")
        return

    # ✅ 가을야구 시뮬레이션
    qna = QnAResponderAgent()
    simulator = SimulatorAgent()

    team = qna.extract_team_name(user_question)
    if not team:
        print("⚠️ 팀 이름을 인식할 수 없습니다. 질문을 다시 작성해주세요.")
        return

    aliases = TEAM_ALIAS_MAP.get(team, [team])
    normalized_aliases = [normalize(alias) for alias in aliases]

    filtered_schedule = []
    for g in schedule_data:
        home = normalize(g["홈팀"])
        away = normalize(g["원정팀"])
        if any(alias in home or alias in away for alias in normalized_aliases):
            filtered_schedule.append(g)

    if not filtered_schedule:
        print(f"❌ {team} 팀의 남은 경기를 찾을 수 없습니다.")
        return

    sim_result = simulator.run(context={"팀": team, "일정": filtered_schedule})

    if isinstance(sim_result, dict):
        probability = sim_result.get("확률", 0.0)
    else:
        print("❌ 시뮬레이션 결과 형식이 잘못되었습니다.")
        return

    final_answer = qna.summarize_simulation(team, probability)

    print("\n🧠 최종 결과:")
    print(final_answer)

if __name__ == "__main__":
    main()