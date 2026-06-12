import streamlit as st
from google import genai
from PIL import Image
from streamlit_cropper import st_cropper

# 1. UI 및 레이아웃 설정
st.set_page_config(page_title="Gemini AI Tree Doctor", page_icon="🌲")
st.title("🌲 AI Tree Doctor (MVP)")
st.markdown("### 📷 Upload a photo and crop the infected area for precise diagnosis.")

# 2. Secrets로부터 API Key 로드 및 정제
raw_api_key = st.secrets.get("GEMINI_API_KEY", "")
GOOGLE_API_KEY = raw_api_key.strip() if raw_api_key else ""

if not GOOGLE_API_KEY:
    st.error("⚠️ API Key가 설정되지 않았습니다. Streamlit Advanced settings를 확인해주세요.")
else:
    # 3. 통합 이미지 업로더 가동
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # 원본 이미지 로드
        img = Image.open(uploaded_file)
        
        st.markdown("#### ✂️ 사각형 조절 상자로 미세 병징 부위를 지정해 주세요:")
        
        # 🌟 [크롭 도구 엔진 가동] 
        # 사용자가 화면에서 마우스나 손가락으로 사각형을 조절하여 자를 수 있게 합니다.
        cropped_img = st_cropper(
            img, 
            realtime_update=True, 
            box_color='#FF3333', 
            aspect_ratio=None  # 자유로운 비율로 자를 수 있도록 설정
        )
        
        # 자른 이미지 미리보기 제공
        st.markdown("#### 🔍 선택된 확대 이미지 미리보기:")
        st.image(cropped_img, use_container_width=True)
        
        # 🌟 사용자가 준비 완료 후 누를 수 있는 진단 버튼 생성
        if st.button("🚀 선택 구간으로 진단 시작", type="primary"):
            st.warning("🔄 Analyzing... Please wait a moment.")

            # 정확도를 극대화하기 위한 전문 수목보호학 지시문
            prompt_text = (
                "You are a strict and highly accurate Tree Doctor AI certified by the Korea Forest Service. "
                "Analyze the provided close-up/cropped image of the tree disease or pest very carefully. "
                "Think step-by-step like a human expert taking the Tree Doctor practical exam. "
                "Examine microscopic structures shown in this cropped area: color/shape of fruiting bodies, fungal mycelium, rust spores, or insect frass.\n\n"
                
                "CRITICAL ORDER 1: You must write the entire response in Korean.\n"
                "CRITICAL ORDER 2: You MUST start your very first sentence exactly as:\n"
                "'안녕하십니까, AI 나무의사입니다. 제공해주신 소나무 질병 이미지와 세부 확대 이미지를 정밀하게 분석한 결과, 다음과 같이 진단하고 방제 계획을 수립합니다.'\n\n"
                
                "Format the rest of the output strictly in Markdown with the following 4 sections:\n\n"
                "1. [정확한 진단명]: Provide the exact common Korean name and scientific name of the disease/pest. (e.g., 소나무 혹병 Cronartium flaccidum)\n"
                "2. [수목보호학적 진단 근거]: Detail the specific visual symptoms and signs shown in the cropped photo supporting your diagnosis.\n"
                "3. [산림청 기준 방제법]: Suggest exact approved chemical pesticide names in Korea and mechanical/cultural control methods.\n"
                "4. [수목 관리 주의사항]: Precautions for chemical toxicity, environment factors, and preventing recurrence."
            )
            
            try:
                # 안전하게 세탁된 API Key로 클라이언트 생성
                client = genai.Client(api_key=GOOGLE_API_KEY)
                
                # 원본 대신 사용자가 자른 'cropped_img'를 구글 AI에게 전달
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[cropped_img, prompt_text]
                )
                
                st.markdown("---")
                st.markdown("### 📋 AI Tree Doctor Diagnosis")
                if response.text:
                    st.markdown(response.text)
                else:
                    st.error("No text response generated.")
                
            except Exception as e:
                st.error(f"⚠️ Connection Error: {str(e)}")
