import streamlit as st
from google import genai
from PIL import Image

# 1. UI 및 레이아웃 단순화 (인코딩 버그 원천 차단)
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

        # 🌟 [초핵심] 무료이면서도 정확도를 극대화하기 위한 수목보호학 가이드라인 주입
        prompt_text = (
            "You are a strict and highly accurate Tree Doctor AI certified by the Korea Forest Service. "
            "Analyze the provided high-resolution image of the tree disease or pest very carefully. "
            "Think step-by-step like a human expert taking the Tree Doctor practical exam. "
            "Examine microscopic structures: color/shape of fruiting bodies, fungal mycelium, rust spores, or insect frass.\n\n"
            
            "CRITICAL ORDER 1: You must write the entire response in Korean.\n"
            "CRITICAL ORDER 2: You MUST start your very first sentence exactly as:\n"
            "'안녕하십니까, AI 나무의사입니다. 제공해주신 소나무 질병 이미지와 세부 확대 이미지를 정밀하게 분석한 결과, 다음과 같이 진단하고 방제 계획을 수립합니다.'\n\n"
            
            "Format the rest of the output strictly in Markdown with the following 4 sections:\n\n"
            "1. [정확한 진단명]: Provide the exact common Korean name and scientific name of the disease/pest. (e.g., 소나무 혹병 Cronartium flaccidum)\n"
            "2. [수목보호학적 진단 근거]: Detail the specific visual symptoms and signs shown in the photo supporting your diagnosis.\n"
            "3. [산림청 기준 방제법]: Suggest exact approved chemical pesticide names in Korea and mechanical/cultural control methods.\n"
            "4. [수목 관리 주의사항]: Precautions for chemical toxicity, environment factors, and preventing recurrence."
        )
        
        try:
            # 안전하게 세탁된 API Key로 클라이언트 생성
            client = genai.Client(api_key=GOOGLE_API_KEY)
            
            # 🌟 [해결책] 무료 제한이 거의 없고 서버가 상시 대기 중인 'gemini-2.5-flash'로 롤백하여 에러를 원천 차단합니다.
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
            st.error(f"⚠️ Connection Error: {str(e)}")
