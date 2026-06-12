import streamlit as st
from google import genai
from PIL import Image

# 1. UI 설정 (인코딩 충돌을 방지하기 위해 심플한 텍스트와 이모지로 구성)
st.set_page_config(page_title="Gemini AI Tree Doctor", page_icon="🌲")
st.title("🌲 AI Tree Doctor (MVP)")
st.markdown("### 📷 Take a photo or upload an image to diagnose tree diseases.")

# 2. Secrets로부터 API Key 로드 및 정제
raw_api_key = st.secrets.get("GEMINI_API_KEY", "")

# 혹시 모를 앞뒤 공백이나 유령 문자 제거
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

        # ASCII 에러를 원천 차단하기 위해 영문 프로그래밍 프롬프트로 송신
        prompt_text = (
            "You are an expert Tree Doctor. Diagnose the tree disease or pest in the provided photo. "
            "CRITICAL: You must write the entire response in Korean. "
            "Format the output strictly in Markdown with the following 4 sections:\n\n"
            "1. [진단명]: Name of the tree disease or pest\n"
            "2. [판단 이유]: Reasons for diagnosis and symptoms observed\n"
            "3. [추천 방제법]: Effective chemical/pesticide treatments and methods\n"
            "4. [주의사항]: Precautions during chemical spraying and future tree management tips"
        )
        
        try:
            # 안전하게 세탁된 API Key로 전송 직전에 클라이언트 생성
            # 만약 키 자체에 깨진 문자가 있다면 이 단계에서 캐치해냅니다.
            client = genai.Client(api_key=GOOGLE_API_KEY)
            
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
            # 에러 발생 시 키 인코딩 문제인지 식별할 수 있도록 가이드 제공
            error_msg = str(e)
            st.error(f"⚠️ Connection Error: {error_msg}")
            if "ascii" in error_msg.lower():
                st.info("💡 Tip: 구글 AI 스튜디오에서 API 키를 새로 발급받아 Secrets에 다시 붙여넣어 보세요. 키 내부에 깨진 문자가 섞여있을 가능성이 매우 높습니다.")
