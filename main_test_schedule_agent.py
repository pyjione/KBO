# main_test_schedule_agent.py

from agents.schedule_reader import ScheduleReaderAgent

if __name__ == "__main__":
    print("🚀 Agent 테스트 시작!")

    try:
        reader = ScheduleReaderAgent()
        context = {"팀": "기아"}  # 또는 "KIA", "기아타이거즈"
        result = reader.run(context=context)
        print("✅ 결과:\n", result)

    except Exception as e:
        print("❌ 실행 중 에러 발생:", e)