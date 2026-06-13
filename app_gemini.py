import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="스마트 나무의사", layout="centered", page_icon="🌲")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.markdown("### 1. 수목 피해 사진 등록")
uploaded_files = st.file_uploader("사진을 필요한 만큼 업로드하세요.", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 AI 종합 분석 시작"):
        with st.spinner("AI 분석 중..."):
            try:
                parts = []
                for f in uploaded_files:
                    img = Image.open(f)
                    img.thumbnail((512, 512))
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                parts.append(types.Part.from_text(text="이 사진들을 종합하여 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                
                # 오류 해결: 최신 모델인 gemini-3.5-flash 사용
                response = client.models.generate_content(
                    model='models/gemini-3.5-flash',
                    contents=parts
                )
                
                st.session_state.ai_result = response.text
                st.success(f"✅ 분석 완료: {st.session_state.ai_result}")
            except Exception as e:
                st.error(f"분석 오류: {e}")

# (GPS 및 소견 입력은 이전과 동일하게 유지하시면 됩니다)
