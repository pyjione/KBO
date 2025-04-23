# from crewai import Agent
# import litellm
# from pydantic import PrivateAttr
# import google.generativeai as genai

# genai.configure(api_key="key")

# class QnAResponderAgent(Agent):
#     _alias_map: dict = PrivateAttr()

#     def __init__(self):
#         super().__init__(
#             name="QnAResponderAgent",
#             role="KBO 질문 응답자",
#             goal="사용자의 질문에서 팀명을 인식하고, 시뮬레이션 결과를 자연어로 응답한다.",
#             backstory="KBO 분석과 팬 커뮤니케이션에 특화된 응답 AI입니다."
#         )
#         self._alias_map = {
#             "기아": ["kia", "kia tigers", "kia\n  tigers"],
#             "롯데": ["lotte", "lotte giants", "lotte\n  giants"],
#             "삼성": ["samsung", "samsung lions", "samsung\n  lions"],
#             "엘지": ["lg", "lg twins", "lg\n  twins"],
#             "두산": ["doosan", "doosan bears", "doosan\n  bears"],
#             "한화": ["hanwha", "hanwha eagles", "hanwha\n  eagles"],
#             "키움": ["kiwoom", "kiwoom heroes", "kiwoom\n  heroes"],
#             "KT": ["kt", "kt wiz", "kt\n  wiz"],
#             "SSG": ["ssg", "ssg landers", "ssg\n  landers"],
#             "NC": ["nc", "nc dinos", "nc\n  dinos"]
#         }

#     def extract_team_name(self, question):
#         lower_q = question.lower()
#         for key, aliases in self._alias_map.items():
#             if key.lower() in lower_q:  # 키워드도 직접 확인!
#                 return key
#             for alias in aliases:
#                 if alias.lower() in lower_q:
#                     return key
#         return None

#     def is_baseball_related(self, question):
#         # KBO 관련 키워드 포함
#         keywords = [
#             "야구", "kbo", "기아", "kia", "타이거즈", "롯데", "lotte", "삼성", "samsung", "라이온스", "엘지", "lg", "트윈스",
#             "두산", "doosan", "베어스", "한화", "hanwha", "이글스", "키움", "kiwoom", "히어로즈", "kt", "ssg", "랜더스", "nc", "다이노스",
#             "twins", "bears", "eagles", "heroes", "dinos", "landers", "위즈", "자이언츠", "감독", "선수", "구단"
#         ]
#         return any(k in question.lower() for k in keywords)

#     def run(self, task=None, context=None):
#         question = context.get("질문", "")
    
#         if not self.is_baseball_related(question):
#             return "⚠️ 이 서비스는 KBO 야구 관련 질문만 응답할 수 있어요!"

#         team = self.extract_team_name(question)
#         if not team:
#             return "⚠️ 질문에서 팀 이름을 인식할 수 없습니다."

#         try:
#             # 팀 정보 에이전트 연결 (외부에서 주입해야 함)
#             from agents.team_info import TeamInfoAgent
#             info_agent = TeamInfoAgent()
#             static_info = info_agent.get_info(team)

#             # 추가적으로 감독이나 선수에 대한 정보가 포함된 질문에 대해서 처리
#             if "감독" in question or "감독님" in question:
#                 # 예시로, 각 팀 감독에 대한 정보를 제공하는 추가 데이터 로직 구현
#                 # 실제로 이 데이터는 크롤링된 데이터나 특정 API에서 가져올 수 있어야 합니다.
#                 return f"⚾️ {team}의 감독은 최근 {team}의 감독 정보를 기반으로 알려드릴 수 있습니다."

#             model = genai.GenerativeModel("models/gemini-1.5-pro")
#             prompt = f"""
#             너는 KBO 전문가야. 아래는 팀에 대한 기본 정보야:

#            {static_info}

#             그리고 팬이 이런 질문을 했어:
#             "{question}"

#             이 정보를 바탕으로 팬에게 친절하고 자연스럽게 설명해줘.
#             """
#             response = model.generate_content(prompt)
#             return response.text
#         except Exception as e:
#             return f"❌ Gemini 처리 중 오류: {e}"


import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from crewai import Agent
from pydantic import PrivateAttr

# Gemini API 설정
genai.configure(api_key="***")


class QnAResponderAgent(Agent):
    _alias_map: dict = PrivateAttr()

    def __init__(self):
        super().__init__(
            name="QnAResponderAgent",
            role="KBO 질문 응답자",
            goal="사용자의 질문에서 팀명을 인식하고, 시뮬레이션 결과를 자연어로 응답한다.",
            backstory="KBO 분석과 팬 커뮤니케이션에 특화된 응답 AI입니다."
        )
        self._alias_map = {
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

    def extract_team_name(self, question):
        lower_q = question.lower()
        for key, aliases in self._alias_map.items():
            if key.lower() in lower_q:  # 키워드도 직접 확인!
                return key
            for alias in aliases:
                if alias.lower() in lower_q:
                    return key
        return None

    def is_baseball_related(self, question):
        keywords = [
            "야구", "kbo", "기아", "kia", "타이거즈", "롯데", "lotte", "삼성", "samsung", "라이온스", "엘지", "lg", "트윈스",
            "두산", "doosan", "베어스", "한화", "hanwha", "이글스", "키움", "kiwoom", "히어로즈", "kt", "ssg", "랜더스", "nc", "다이노스",
            "twins", "bears", "eagles", "heroes", "dinos", "landers", "위즈", "자이언츠", "감독", "선수", "구단", "야구 룰", "포수", "야수", "투수"
        ]
        return any(k in question.lower() for k in keywords)

    def fetch_search_results(self, query):
        """구글에서 검색하고 결과를 얻어오는 함수"""
        search_url = f"https://www.google.com/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            result_divs = soup.find_all("div", {"class": "BNeawe iBp4i AP7Wnd"})
            if result_divs:
                return result_divs[0].text  # 첫 번째 검색 결과를 반환
        return None

    def run(self, task=None, context=None):
        question = context.get("질문", "")
    
        if not self.is_baseball_related(question):
            return "⚠️ 이 서비스는 KBO 야구 관련 질문만 응답할 수 있어요!"

        team = self.extract_team_name(question)
        if not team:
            return "⚠️ 질문에서 팀 이름을 인식할 수 없습니다."

        try:
            # 감독, 선수, 코치, 포수, 투수 등 추가 정보 처리
            info_types = ["감독", "선수", "코치", "야수", "포수", "투수", "야구 룰"]
            for info_type in info_types:
                if info_type in question:
                    player_info = self.fetch_search_results(f"{team} {info_type}")
                    if player_info:
                        return f"⚾️ {team}의 {info_type}: {player_info}"
                    else:
                        return f"⚾️ {team}의 {info_type}에 대한 정보를 찾을 수 없습니다."

            # Gemini API와 함께 RAG 방식으로 텍스트 생성
            model = genai.GenerativeModel("models/gemini-1.5-pro")
            prompt = f"""
            너는 KBO 전문가야. 아래는 팀에 대한 기본 정보야:

            팀: {team}

            팬이 이런 질문을 했어:
            "{question}"

            이 정보를 바탕으로 팬에게 친절하고 자연스럽게 설명해줘.
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Gemini 처리 중 오류: {e}"