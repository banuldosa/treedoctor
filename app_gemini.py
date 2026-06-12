import streamlit as st
from google import genai
from PIL import Image

# 1. 웹앱 기본 레이아웃 설정
st.set_page_config(page_title="Gemini AI Tree Doctor", page_icon="🌲")
st.title("🌲 AI Tree Doctor (MVP)")
st.markdown("### 📷 Take a photo or upload an image to diagnose tree diseases.")

# 2. Streamlit Cloud Secrets로부터 API Key 로드
raw_api_key = st.secrets.get("GEMINI_API_KEY", "")

# 🌟 [에러 해결의 핵심] 키 앞뒤에 숨어있는 눈에 안 보이는 공백, 줄바꿈(\n), 특수문자를 완전히 제거
GOOGLE_API_KEY = raw_api_key.strip() if raw_api_key else ""

if not GOOGLE_API_KEY:
    st.warning("👈 Please set GEMINI_API_KEY in Streamlit advanced settings.")
else:
    try:
        # 공백이 싹 청소된 깨끗한 키로 구글 클라이언트 가동
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.error(f"Initialization Error: {str(e)}")
        client = None

    # 통합 이미지 업로더 가동
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None and client is not None:
        # 이미지를 PIL 객체로 로드
        image = Image.open(uploaded_file)
        st.image(image, caption="Target Image", use_container_width=True)
        
        st.warning("🔄 Analyzing... Please wait a moment.")

        # 구글 서버 전달용 전문 진단 프롬프트
        prompt_text = (
            "당신은 전문 나무의사입니다. 제공된 사진의 수목 병해충을 정밀 진단해 주세요. "
            "반드시 한국어로 답변해야 하며, 다음 4가지 항목을 마크다운 서식으로 출력하세요:\n\n"
            "1. [진단명]: 수목 병명 또는 해충명\n"
            "2. [판단 이유]: 관찰되는 병징 및 발생 원인\n"
            "3. [추천 방제법]: 효과적인 약제 명칭 및 방제 방법\n"
            "4. [주의사항]: 약제 살포 시 주의사항 및 향후 관리 팁"
        )
        
        try:
            # 순수 PIL 이미지 객체(image)와 텍스트를 리스트로 묶어 전송
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt_text]
            )
            
            # 최종 리포트 출력 구역
            st.markdown("---")
            st.markdown("### 📋 AI Tree Doctor Diagnosis")
            if response.text:
                st.markdown(response.text)
            else:
                st.error("No text response generated.")
            
        except Exception as e:
            st.error(f"⚠️ Connection Error: {str(e)}")
