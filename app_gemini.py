import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# 1. 웹앱 기본 레이아웃 설정
st.set_page_config(page_title="Gemini AI Tree Doctor", page_icon="🌲")
st.title("🌲 AI Tree Doctor (MVP)")
st.markdown("### 📷 Take a photo or upload an image to diagnose tree diseases.")

# 2. Streamlit Cloud Secrets로부터 API Key 안전하게 로드
GOOGLE_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not GOOGLE_API_KEY:
    st.warning("👈 Please set GEMINI_API_KEY in Streamlit advanced settings.")
else:
    # 구글 GenAI 클라이언트 가동
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    # 통합 이미지 업로더 가동
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # 이미지 열기 및 화면 출력
        image = Image.open(uploaded_file)
        st.image(image, caption="Target Image", use_container_width=True)
        
        st.warning("🔄 Analyzing... Please wait a moment.")

        # 🌟 Pydantic 검증 에러를 해결하기 위해 이미지를 바이너리 바이트로 변환
        img_byte_arr = io.BytesIO()
        img_format = image.format if image.format else "JPEG"
        image.save(img_byte_arr, format=img_format)
        img_bytes = img_byte_arr.getvalue()

        # 🌟 [해결의 핵심] google-genai 라이브러리가 요구하는 공식 Part 객체 규격으로 포장
        image_part = types.Part.from_bytes(
            data=img_bytes,
            mime_type=f"image/{img_format.lower()}"
        )

        # 구글 AI 스튜디오 서버 전달용 전문 진단 프롬프트
        prompt_text = (
            "당신은 전문 나무의사입니다. 제공된 사진의 수목 병해충을 정밀 진단해 주세요. "
            "반드시 한국어로 답변해야 하며, 다음 4가지 항목을 마크다운 서식으로 출력하세요:\n\n"
            "1. [진단명]: 수목 병명 또는 해충명\n"
            "2. [판단 이유]: 관찰되는 병징 및 발생 원인\n"
            "3. [추천 방제법]: 효과적인 약제 명칭 및 방제 방법\n"
            "4. [주의사항]: 약제 살포 시 주의사항 및 향후 관리 팁"
        )
        
        try:
            # gemini-2.5-flash 모델에 공식 규격으로 포장된 데이터 송신
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image_part, prompt_text]
            )
            
            # 최종 리포트 출력 구역
            st.markdown("---")
            st.markdown("### 📋 AI Tree Doctor Diagnosis")
            if response.text:
                st.markdown(response.text)
            else:
                st.error("No text response generated.")
            
        except Exception as e:
            # 통신 에러 내용 상세 출력
            st.error(f"⚠️ Connection Error: {str(e)}")
