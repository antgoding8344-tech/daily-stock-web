import streamlit as st
import urllib.parse
import feedparser
from google import genai

# 웹페이지 기본 설정
st.set_page_config(page_title="나만의 주식 뉴스 AI", page_icon="📈", layout="centered")

st.title("📈 AI 주식/경제 뉴스 요약 봇")
st.write("관심 있는 종목이나 경제 키워드를 입력하면 AI가 최신 뉴스를 싹 모아서 요약해 드립니다!")

# 검색어 입력창
keyword = st.text_input("검색 키워드 (예: S&P 500, 어도비, 앱티브, 미국 금리 등)", "S&P 500 미국 증시")

# API 키 세팅 (스트림릿 웹사이트용 보안 설정)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except:
    st.error("앗! 아직 AI 열쇠(API 키)가 웹사이트에 연결되지 않았습니다. (다음 단계에서 연결할 예정입니다!)")
    st.stop()

# 뉴스 수집 함수
def fetch_stock_news(search_keyword, max_results=5):
    encoded_keyword = urllib.parse.quote(search_keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:max_results]:
        articles.append({'title': entry.title, 'link': entry.link})
    return articles

# 실행 버튼
if st.button("뉴스 요약 가져오기"):
    with st.spinner("뉴스를 읽고 AI가 분석하는 중입니다... 잠시만요!"):
        articles = fetch_stock_news(keyword)
        
        if not articles:
            st.warning("관련 뉴스를 찾지 못했습니다. 키워드를 바꿔보세요.")
        else:
            news_text = ""
            for idx, article in enumerate(articles, 1):
                news_text += f"뉴스 {idx}\n- 제목: {article['title']}\n- 링크: {article['link']}\n\n"

            prompt = f"""
            당신은 친절한 주식/경제 전문 AI 멘토입니다. 
            아래 뉴스들을 바탕으로 주식 시장 분석에 도움을 주는 요약을 작성해주세요.
            
            [뉴스 데이터]
            {news_text}
            
            [작성 가이드라인]
            1. 오늘의 증시 한 줄 요약
            2. 주요 이슈별 3줄 요약 (호재/악재 여부 포함)
            3. 어려운 경제 용어 쉬운 설명
            웹사이트에서 보기 편하도록 마크다운으로 예쁘게 정리해주세요.
            """
            
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            
            st.markdown(response.text)
