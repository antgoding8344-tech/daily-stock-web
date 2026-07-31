import streamlit as st
import urllib.parse
import feedparser
from google import genai

# 웹페이지 기본 설정
st.set_page_config(page_title="출근길 AI 미국증시 브리핑", page_icon="📰", layout="centered")

st.title("📰 출근길 AI 미국증시 & 경제 브리핑")
st.write("전날 미국 증시와 핵심 경제 뉴스를 팩트 위주로 확인하고 AI 해설까지 한눈에 보세요!")

# 검색어 기본값을 출근길 미국증시 브리핑용으로 설정
keyword = st.text_input("검색 키워드", "미국 증시 뉴욕증시 S&P500")

# API 키 세팅
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("API 키 설정에 오류가 있습니다.")
    st.stop()

# 뉴스 수집 함수 (발행 시각 포함, 6개 수집)
def fetch_stock_news(search_keyword, max_results=6):
    encoded_keyword = urllib.parse.quote(search_keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    articles = []
    
    for entry in feed.entries[:max_results]:
        # 보도 시각 가져오기
        published_time = getattr(entry, 'published', '시각 정보 없음')
        
        # 구글 RSS의 긴 보도 시각 표기를 읽기 쉽게 간소화
        if len(published_time) > 16:
            published_time = published_time[:22]
            
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'published': published_time
        })
    return articles

# 실행 버튼
if st.button("🚀 최신 뉴스 & AI 브리핑 가져오기", type="primary"):
    with st.spinner("뉴스를 수집하고 분석 중입니다..."):
        articles = fetch_stock_news(keyword, max_results=6)
        
        if not articles:
            st.warning("관련 뉴스를 찾지 못했습니다.")
        else:
            # -------------------------------------------------------------
            # [SECTION 1] 실제 최신 뉴스 6개 카드 배치 (시각 + 링크)
            # -------------------------------------------------------------
            st.subheader("📌 주요 최신 뉴스 (6선)")
            
            for idx, article in enumerate(articles, 1):
                # 깔끔한 상자(Container) 형태로 뉴스 카드 배치
                with st.container(border=True):
                    st.markdown(f"**{idx}. [{article['title']}]({article['link']})**")
                    st.caption(f"🕒 보도 시각: {article['published']}")
            
            st.divider()

            # -------------------------------------------------------------
            # [SECTION 2] AI 심층 종합 해설 및 전망
            # -------------------------------------------------------------
            news_text = ""
            for idx, article in enumerate(articles, 1):
                news_text += f"뉴스 {idx}: {article['title']} (시각: {article['published']})\n"

            prompt = f"""
            당신은 주식/경제 전문 AI 멘토입니다. 
            바쁜 출근길에 사용자가 핵심만 빠르게 파악할 수 있도록 전달받은 최신 뉴스 6개를 종합하여 브리핑을 작성해주세요.
            
            [뉴스 데이터]
            {news_text}
            
            [작성 가이드라인]
            1. **📊 전날 미국증시 종합 3줄 요약**
               - 시장 전체 흐름, 주요 지수 동향, 핵심 이슈를 3줄로 깔끔하게 정리.

            2. **💡 핵심 이슈별 성격 및 전망 해설**
               - 각 주요 이슈마다 아래 항목을 포함할 것:
                 - **구분**: [호재 📈] / [악재 📉] / [중립·주의 ⚠️] 중 명확히 표시
                 - **쉬운 해설**: 전날 증시에 미친 영향과 배경을 주린이도 알기 쉽게 설명
                 - **향후 전망**: 이 소식이 앞으로 시장에 미칠 영향이나 관전 포인트 1줄 요약

            가독성이 좋게 이모지와 bold체를 적절히 활용해 주세요.
            """
            
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            
            st.subheader("🤖 AI 종합 브리핑 & 호재/악재 전망")
            st.markdown(response.text)
