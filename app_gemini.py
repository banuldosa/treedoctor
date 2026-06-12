import streamlit as st
from google import genai
from PIL import Image

# 1. 웹앱 기본 레이아웃 설정 (모든 UI를 영문/이모지로 단순화하여 인코딩 유발 차단)
st.set_page_config(page_title="Gemini AI Tree Doctor", page_icon="🌲")
st.title("🌲 AI Tree Doctor (MVP)")
st.markdown("### 📷 Take a photo or upload an image to diagnose tree diseases.")

# 2. Streamlit Cloud Secrets로부터 API Key 로드
raw_api_key = st.secrets.get("GEMINI_API_KEY", "")
GOOGLE_API_KEY = raw_api_key.strip() if raw_api_key else ""

if not GOOGLE_API_KEY:
    st.warning("👈 Please set GEMINI_API_KEY in Streamlit advanced settings.")
else:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.error(f"Initialization Error: {str(e)}")
        client = None

    # 통합 이미지 업로더 가동
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None and client is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Target Image", use_container_width=True)
        
        st.warning("🔄 Analyzing... Please wait a moment.")

        # 🌟 [에러 해결의 핵심] 지시문을 완벽한 영어로 작성하여 ASCII 인코딩 에러를 원천 차단합니다.
        # 단, 마지막에 "반드시 한국어로 출력하라"는 강력한 지항(Output in Korean)을 포함했습니다.
        prompt_text = (
            "You are an expert Tree Doctor. Diagnose the tree disease or pest in the provided photo. "
            "CRITICAL: You must write the entire response in Korean. "
            "Format the output strictly in Markdown with the following 4 sections:\n\n"
            "1. [진단명]: Name of the tree disease or pest\n"
            "2. [판단 이유]: Reasons for diagnosis and symptoms observed\n"
            "3. [추천 방제법]: Effective chemical/pesticide treatments and methods based on official guidelines\n"
            "4. [주의사항]: Precautions during chemical spraying and future tree management tips"
        )
        
        try:
            # 순수 이미지 객체와 영문 지시문을 리스트로 안전하게 결합하여 송신
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
