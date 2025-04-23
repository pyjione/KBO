import streamlit as st
import json
from agents.playoff_predictor import PlayoffPredictor
from agents.qna_responder import QnAResponderAgent
from utils.kbo_scraper import get_kbo_rankings
from agents.simulator import SimulatorAgent
from agents.schedule_reader import ScheduleReaderAgent

st.set_page_config(page_title="KBO 가을야구 계산기", layout="wide")
st.title("⚾️ KBO 가을야구 계산기")

menu = st.tabs(["현재 순위", "가을야구 예상진출 확률", "플레이오프 예상 대진", "남은 경기 일정", "Q&A", "구단 정보"])

# with menu[1]:
#     st.header("가을야구 예상 진출 확률")

# with menu[0]:
#     st.header("현재 순위")

# with menu[2]:
#     st.header("플레이오프 예상 대진")

# with menu[3]:
#     st.header("일정 보기")

# with menu[4]:
#     st.header("Q&A")
    
# with menu[5]:
#     st.header("구단 정보")

import streamlit as st
import json
from agents.playoff_predictor import PlayoffPredictor
from agents.standings_generator import StandingsGenerator
from agents.simulator import SimulatorAgent
import pandas as pd

TEAM_NAME_KOR = {
    "LG Twins": "LG",
    "SSG Landers": "SSG",
    "Hanwha Eagles": "한화",
    "Kia Tigers": "KIA",
    "KT Wiz": "KT",
    "Doosan Bears": "두산",
    "Lotte Giants": "롯데",
    "Samsung Lions": "삼성",
    "NC Dinos": "NC",
    "Kiwoom Heroes": "키움"
}

def normalize_team(name):
    cleaned = " ".join(name.replace("\n", " ").split())  # 줄바꿈 제거 + 공백 하나로 압축
    return TEAM_NAME_KOR.get(cleaned, cleaned)

STADIUM_KOR = {
    "Seoul-Jamsil": "서울 잠실",
    "Seoul-Gocheok": "서울 고척",
    "Incheon-Munhak": "인천 문학",
    "Daegu": "대구",
    "Daejeon": "대전",
    "Gwangju": "광주",
    "Changwon": "창원",
    "Busan-Sajik": "부산 사직"
}

def normalize_stadium(name):
    return STADIUM_KOR.get(name.strip(), name.strip())

# 날짜 & 시간 통합
from datetime import datetime

def combine_datetime(date, time):
    try:
        date_obj = pd.to_datetime(date)
        time_obj = datetime.strptime(time.strip().lower(), "%I:%M%p").time()
        combined = datetime.combine(date_obj.date(), time_obj)
        return combined.strftime("%Y년 %m월 %d일 (%a) %H:%M")
    except:
        return f"{date} {time}"
    
    
# 간단한 전처리 예시
def preprocess_schedule(raw_schedule):
    def clean_team(name):
        return name.replace("\n", "").strip().split()[-1]  # 'LG\n Twins' → 'Twins' → 'LG'

    kor_to_short = {
        "Twins": "LG",
        "Landers": "SSG",
        "Dinos": "NC",
        "Wiz": "KT",
        "Bears": "두산",
        "Tigers": "KIA",
        "Giants": "롯데",
        "Eagles": "한화",
        "Lions": "삼성",
        "Heroes": "키움"
    }

    schedule = []
    for game in raw_schedule:
        home_raw = clean_team(game["홈팀"])
        away_raw = clean_team(game["원정팀"])
        home = kor_to_short.get(home_raw, home_raw)
        away = kor_to_short.get(away_raw, away_raw)
        schedule.append({"홈": home, "원정": away})
    return schedule


# 🧩 데이터 불러오기
try:
    with open("data/kbo_schedule_mykbo.json", "r", encoding="utf-8") as f:
        schedule = json.load(f)
except FileNotFoundError:
    st.error("❌ 스케줄 데이터를 찾을 수 없습니다.")
    schedule = []
    

import pandas as pd
from agents.standings_generator import StandingsGenerator
from agents.simulator import SimulatorAgent

# 🧠 예상 기능
with menu[0]:
    st.subheader("📈 실시간 KBO 순위")

    refresh = True  # Set refresh True by default to always fetch on page load

    if refresh:  # always fetch on first load
        try:
            data = get_kbo_rankings()
            df = pd.DataFrame(data, columns=["팀", "승", "패", "무", "승률", "승차", "기대승률"])
            df.index = df.index + 1
            df.index.name = "순위"
            from datetime import datetime
            retrieved_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M 기준")
            st.caption(f"📅 {retrieved_time} 기준 데이터입니다.")
            st.dataframe(df)
            st.markdown(
                r"""
---
### 📘 순위 지표 설명

##### ✅ 승률 (Winning Percentage)
팀이 실제 경기에서 이긴 비율입니다. KBO에서는 무승부를 제외하고 계산합니다.  
$$
\text{승률} = \frac{\text{승리 수}}{\text{승리 수} + \text{패배 수}}
$$

##### ✅ 승차 (Games Behind)
선두 팀과의 경기 수 차이를 나타냅니다.  
$$
\text{승차} = \frac{(\text{1위팀 승수} - \text{해당팀 승수}) + (\text{해당팀 패배수} - \text{1위팀 패배수})}{2}
$$

##### ✅ 기대승률 (Pythagorean Expectation)
팀의 득점과 실점을 바탕으로 실력 기반으로 예측되는 승률입니다.  
$$
\text{기대승률} = \frac{(\text{득점})^2}{(\text{득점})^2 + (\text{실점})^2}
$$
""",
                unsafe_allow_html=False,
            )
        except Exception as e:
            st.error(f"❌ 순위 데이터를 불러오는 데 실패했어요: {e}")

    if st.button("🔄 순위 새로고침"):
        st.rerun()
            
with menu[1]:
    st.subheader("📉 가을야구 진출 확률 예측")

    team_input = st.selectbox("팀을 선택하세요", [
        "LG", "SSG", "NC", "KT", "두산", "KIA", "롯데", "한화", "삼성", "키움"
    ])

    if st.button("확률 예측하기"):
        agent = SimulatorAgent()
        result_all = agent.run(context={"전체": True})

        if "전체결과" not in result_all:
            st.error(result_all.get("오류", "알 수 없는 오류가 발생했습니다."))
        else:
            all_probs = result_all["전체결과"]

            # 📌 선택한 팀 출력
            selected_prob = all_probs.get(team_input)
            if selected_prob is not None:
                st.success(f"🎯 {team_input}의 가을야구 진출 확률은 {selected_prob}% 입니다.")
                st.markdown("  \n  \n")
            else:
                st.warning(f"{team_input} 팀에 대한 확률 데이터를 찾을 수 없습니다.")

            # 📌 전체 데이터프레임 출력
            df_probs = pd.DataFrame(list(all_probs.items()), columns=["팀", "진출 확률 (%)"])
            st.markdown("#### 📊 참고 : 전체 팀의 진출 확률도 아래 표로 확인할 수 있어요.")
            df_probs = df_probs.sort_values("진출 확률 (%)", ascending=False).reset_index(drop=True)
            df_probs.index = df_probs.index + 1
            df_probs.index.name = "순위"
            st.dataframe(df_probs, use_container_width=True)

with menu[2]:
    st.header("🏟️ 플레이오프 예상 대진표")

    with open("data/kbo_schedule_mykbo.json", "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    predictor = PlayoffPredictor(schedule_data)
    bracket = predictor.run()

    st.markdown(bracket)
               
               
# with menu[3]:
#     st.subheader("📅 KBO 2025년 4월 경기 일정")

#     df_schedule = pd.DataFrame(schedule)
#     df_schedule["날짜"] = pd.to_datetime(df_schedule["날짜"], errors="coerce")
#     df_schedule = df_schedule.sort_values(by=["날짜", "시간"]).reset_index(drop=True)

#     # 팀명 & 구장 정리
#     df_schedule["홈팀"] = df_schedule["홈팀"].apply(normalize_team)
#     df_schedule["원정팀"] = df_schedule["원정팀"].apply(normalize_team)
#     df_schedule["구장"] = df_schedule["구장"].apply(normalize_stadium)

#     # 날짜+시간 합치기
#     df_schedule["일시"] = df_schedule.apply(lambda row: combine_datetime(row["날짜"], row["시간"]), axis=1)

#     # 달력 느낌으로 정렬 출력
#     grouped = df_schedule.groupby("날짜")
#     for date, group in grouped:
#         st.markdown(f"### 🗓️ {date.strftime('%Y년 %m월 %d일 (%a)')}")
#         for _, row in group.iterrows():
#             st.markdown(
#                 f"- 🕒 **{row['시간']}**: {row['홈팀']} vs {row['원정팀']} ({row['구장']})"
#             )

with menu[4]:
    st.subheader("💬 KBO Q&A AI 응답기")

    user_question = st.text_input(
        "궁금한 내용을 자유롭게 입력해보세요!",
        placeholder="예: LG는 왜 잘하나요? / 야구 경기 직관은 어떻게 하나요?"
    )

    if st.button("질문하기") and user_question.strip():
        responder = QnAResponderAgent()
        response = responder.run(context={"질문": user_question})
        st.markdown(f"🧠 {response}")
        

with menu[5]:
    st.header("📘 구단 정보")

    from agents.team_info import TeamInfoAgent

    team_agent = TeamInfoAgent()

    team_name = st.selectbox(
        "팀을 선택하세요", 
        ["LG", "SSG", "NC", "KT", "두산", "KIA", "롯데", "한화", "삼성", "키움"],
        key="team_info_selectbox"
    )

    if st.button("구단 정보 보기"):
        info = team_agent.run({"팀": team_name})
        st.markdown(info)
        
with menu[3]:
    st.header("📅 남은 경기 일정")

    team_name = st.selectbox(
        "팀을 선택하세요",
        ["KIA", "롯데", "삼성", "LG", "두산", "한화", "키움", "KT", "SSG", "NC"],
        key="schedule_team_select"  # ✅ selectbox 중복 방지용 key 필수!
    )

    if st.button("남은 경기 보기", key="view_schedule_button"):
        reader = ScheduleReaderAgent()
        games = reader.get_remaining_games(team_name)

        if not games:
            st.warning(f"❌ {team_name} 팀의 남은 경기를 찾을 수 없습니다.")
        else:
            st.success(f"✅ {team_name} 팀의 남은 경기 수: {len(games)}")

            # 팀명 및 구장 번역
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

            # 게임 일정 출력
            for g in games:
                home_team = g["홈팀"]  # 기존 home_team_ -> home_team로 수정
                away_team = g["원정팀"]

                # 한국어로 팀명 및 구장 매핑
                home_team_kor = team_translation.get(home_team, home_team)  # home_team_ -> home_team
                away_team_kor = team_translation.get(away_team, away_team)
                stadium = stadium_translation.get(g["구장"], g["구장"])

                # 출력 형식 수정
                st.markdown(f"- **{g['날짜']} {g['시간']}** | **{home_team_kor}** vs. **{away_team_kor}** 🏟️ ({stadium})")