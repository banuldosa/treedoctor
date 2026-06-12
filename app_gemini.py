import streamlit as st
from google import genai
from PIL import Image

# 1. UI 설정 (인코딩 충돌을 방지하기 위해 심플한 텍스트와 이모지로 구성)
st.set_page_config(page_title="Gemini AI Tree Doctor", page_icon="🌲")
st.title("🌲 AI Tree Doctor (MVP)")
st.markdown("### 📷 Take a photo or upload an image to diagnose tree diseases.")

# 2. Secrets로부터 API Key 로드 및 정제
raw_api_key = st.secrets.get("GEMINI_API_KEY", "")
GOOGLE_API_KEY = raw_api_key.strip() if raw_api_key else ""

if not GOOGLE_API_KEY:
    st.error("⚠️ API Key가 설정되지 않았습니다. Streamlit Advanced settings를 확인해주세요.")
else:
    # 3. 이미지 업로더 가동
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Target Image", use_container_width=True)
        
        st.warning("🔄 Analyzing... Please wait a moment.")

        # 🌟 [입력 위치] 여기에 정교한 영문 지시문(Prompt)이 들어갑니다.
        # AI에게 한국산림청 및 수목보호학적 기준을 따르되, 답변은 한국어로 하도록 강제하는 설정입니다.
        prompt_text = (
            "You are a strict and highly accurate Tree Doctor certified by the Korea Forest Service. "
            "Analyze the provided high-resolution image of the tree disease or pest very carefully. "
            "Look for microscopic signs such as mycelium, spores, lesions, frass, or specific discoloration pattern. "
            "CRITICAL: You must write the entire response in Korean. "
            "Format the output strictly in Markdown with the following 4 sections:\n\n"
            "1. [정확한 진단명]: Provide the exact common Korean name and scientific name of the disease/pest.\n"
            "2. [수목보호학적 진단 근거]: Explain why you diagnosed this based on the visual symptoms (e.g., color of spores, shape of canker) in the photo.\n"
            "3. [산림청 기준 방제법]: Suggest exact chemical treatments (pesticide names approved in Korea) and cultural/mechanical control methods.\n"
            "4. [수목 관리 주의사항]: Note precautions regarding pesticide resistance, timing of application, and environment factors."
        )
        
        try:
            # 안전하게 세탁된 API Key로 클라이언트 생성
            client = genai.Client(api_key=GOOGLE_API_KEY)
            
            # 🌟 [모델 변경] 기존 'gemini-2.5-flash'에서 고성능 추론 모델인 'gemini-2.5-pro'로 교체했습니다.
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt_text]
            )
            
            st.markdown("---")
            st.markdown("### 📋 AI Tree Doctor Diagnosis")
            if response.text:
                st.markdown(response.text)
            else:
                st.error("No text response generated.")
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"⚠️ Connection Error: {error_msg}")
            if "ascii" in error_msg.lower():
                st.info("💡 Tip: 구글 AI 스튜디오에서 API 키를 새로 발급받아 Secrets에 다시 붙여넣어 보세요.")
