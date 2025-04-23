from agents.simulator import SimulatorAgent
import json

if __name__ == "__main__":
    with open("data/kbo_schedule_mykbo.json", "r", encoding="utf-8") as f:
        full_schedule = json.load(f)

    simulator = SimulatorAgent()
    result = simulator.run(context={"팀": "기아", "일정": full_schedule})
    print(result)