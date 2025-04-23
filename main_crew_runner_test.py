import os
import json
import litellm
from agents.qna_responder import QnAResponderAgent
from agents.schedule_reader import ScheduleReaderAgent
from agents.simulator import SimulatorAgent
from crewai.llm import LLM
# ✅ LITELLM 환경변수 불필요, 직접 호출 방식 사용
llm = LLM(
    model="openrouter-gpt-3.5",
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

# 사용자 질문
user_question = "기아는 가을야구 가능성 있어?"

# 일정 로딩
with open("data/kbo_schedule_mykbo.json", "r", encoding="utf-8") as f:
    schedule_data = json.load(f)

# Agent 초기화
qna = QnAResponderAgent()
simulator = SimulatorAgent()

# 팀 이름 추출
team = qna.extract_team_name(user_question)
if not team:
    print("⚠️ 팀 이름을 인식할 수 없습니다.")
    exit()

# 일정 필터링
filtered_schedule = [g for g in schedule_data if team.lower() in g["홈팀"].lower() or team.lower() in g["원정팀"].lower()]

# 시뮬레이션 실행
sim_result = simulator.run(context={"팀": team, "일정": filtered_schedule})

# dict 형태인지 확인하고 확률 추출
if isinstance(sim_result, dict):
    probability = sim_result.get("확률", 0.0)
else:
    print("❌ 시뮬레이션 결과 형식이 잘못되었습니다.")
    exit()

# 자연어로 요약
final_answer = qna.summarize_simulation(team, probability)

print("🧠 최종 결과:")
print(final_answer)