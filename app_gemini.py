import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import sys

# 1. 시스템 입출력 UTF-8 강제 변환
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
except Exception:
    pass

# 2. 웹앱 메인 타이틀 및 레이아웃 설정 (오류 방지를 위해 메인 안내는 영어/이모지 조합 후 마크다운 처리)
st.set_page_config(page_title="Gemini AI Tree Doctor", page_icon="🌲")
st.title("🌲 AI Tree Doctor (MVP)")
st.markdown("### 📷 Take a photo or upload an image to diagnose tree diseases.")

# 3. Streamlit Cloud Secrets로부터 API Key 로드
GOOGLE_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not GOOGLE_API_KEY:
    st.warning("👈 Please set GEMINI_API_KEY in Streamlit advanced settings.")
else:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    # 🌟 파일 업로더 가동 (에러 방지를 위해 라벨을 영문으로 심플하게 처리)
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Target Image", use_container_width=True)
        
        # 🌟 시스템 UI 에러 유발 구역을 안전한 텍스트로 대체
        st.warning("🔄 Analyzing... Please wait a moment.")

        # 🌟 구글 서버로 직접 들어가는 지시문 패키지 (이 데이터는 API 통신용이라 안전합니다)
        prompt_text = (
            "당신은 전문 나무의사입니다. 제공된 사진의 수목 병해충을 정밀 진단해 주세요. "
            "반드시 한국어로 답변해야 하며, 다음 4가지 항목을 마크다운 서식으로 출력하세요:\n\n"
            "1. [진단명]: 수목 병명 또는 해충명\n"
            "2. [판단 이유]: 관찰되는 병징 및 발생 원인\n"
            "3. [추천 방제법]: 효과적인 약제 명칭 및 방제 방법\n"
            "4. [주의사항]: 약제 살포 시 주의사항 및 향후 관리 팁"
        )
        
        try:
            # 안전한 Content 객체 래핑 방식으로 송신
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    image,
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt_text)]
                    )
                ]
            )
            
            # 최종 리포트 출력 구역
            st.markdown("---")
            st.markdown("### 📋 AI Tree Doctor Diagnosis")
            if response.text:
                st.markdown(response.text)
            else:
                st.error("No text response generated.")
            
        except Exception as e:
            # 에러 메시지 자체 출력 시 깨짐 현상 완벽 방어
            st.error("⚠️ Connection Error. Please try again.")
