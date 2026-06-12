import streamlit as st
from google import genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="Gemini AI 나무의사", page_icon="🌲")
st.title("🌲 구글 AI 스튜디오 기반 나무의사 (MVP)")
st.write("스마트폰으로 아픈 나무 사진을 찍어 올리면, Gemini가 즉시 진단 및 처방을 내립니다.")

# 2. API Key 자동 가져오기 설정 (Streamlit Cloud Secrets 및 로컬 환경 대응)
GOOGLE_API_KEY = ""

# 우선 Streamlit Secrets에 저장된 키가 있는지 확인
if "GEMINI_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
# 만약 없다면 사이드바에서 수동으로 입력받기
else:
    GOOGLE_API_KEY = st.sidebar.text_input("Google API Key 입력", type="password")

# 3. 로그인 검증 및 앱 구동
if not GOOGLE_API_KEY:
    st.warning("👈 왼쪽 사이드바에 구글 AI 스튜디오에서 발급받은 API Key를 입력해 주세요.")
else:
    # 획득한 키로 구글 클라이언트 연결
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    # 스마트폰 전용 카메라 입력창
    uploaded_file = st.file_uploader("📷 아픈 나무 사진 촬영 또는 선택하기", type=["jpg", "jpeg", "png"])uploaded_file = st.file_uploader("📷 아픈 나무 사진 촬영 또는 선택하기", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        from PIL import Image
        image = Image.open(uploaded_file)
        st.image(image, caption="현장 촬영 이미지", use_container_width=True)
        st.info("🔄 구글 인공지능이 이미지를 분석하고 처방전을 작성 중입니다...")

        # 진단 프롬프트
        prompt_text = (
            "이 수목 사진을 진단해 주세요. "
            "반드시 수목보호학 지식을 기반으로 하여 [진단명], [판단 이유], [추천 방제법(농약)], [주의사항]의 순서로 "
            "깔끔하고 가독성이 좋은 마크다운 형식을 갖추어 출력해 주세요."
        )
        
        try:
            # 404 에러 없는 최신 범용 모델 사용
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt_text]
            )
            
            st.markdown("---")
            st.subheader("📋 AI 나무의사 진단 서신")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"⚠️ 진단 중 오류가 발생했습니다: {e}")
