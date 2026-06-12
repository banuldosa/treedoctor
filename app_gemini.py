import streamlit as st
from google import genai
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="Gemini AI 나무의사", page_icon="🌲")
st.title("🌲 구글 AI 스튜디오 기반 나무의사 (MVP)")
st.write("스마트폰으로 아픈 나무 사진을 찍어 올리면, Gemini가 즉시 진단 및 처방을 내립니다.")

# 2. 사이드바 API Key 입력창
GOOGLE_API_KEY = st.sidebar.text_input("Google API Key 입력", type="password")

if not GOOGLE_API_KEY:
    st.warning("👈 왼쪽 사이드바에 구글 AI 스튜디오에서 발급받은 API Key를 입력해 주세요.")
else:
    # 최신 규격에 맞는 클라이언트 생성
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    # 카메라 입력창
    uploaded_file = st.camera_input("📷 스마트폰 카메라로 나무 촬영하기")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="현장 촬영 이미지", use_container_width=True)
        st.info("🔄 AI 나무의사가 이미지를 분석하고 처방전을 작성 중입니다...")

        # 명령 조율
        prompt_text = (
            "이 수목 사진을 진단해 주세요. "
            "반드시 수목보호학 지식을 기반으로 하여 [진단명], [판단 이유], [추천 방제법(농약)], [주의사항]의 순서로 "
            "깔끔한 마크다운 형식을 갖추어 출력해 주세요."
        )
        
        try:
            # 가장 범용적이고 404 에러가 나지 않는 'gemini-2.5-flash' 최신 범용 모델로 지정합니다.
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt_text]
            )
            
            st.markdown("---")
            st.subheader("📋 AI 나무의사 진단 서신")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"⚠️ 진단 중 오류가 발생했습니다: {e}")