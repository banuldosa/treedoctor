import streamlit as st
import io
from google import genai
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. API 설정
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# 2. [사진 촬영 및 AI 동정]
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("AI가 사진 3장을 종합 분석 중입니다..."):
            try:
                # 이미지를 바이트 데이터로 변환하여 리스트 생성
                contents = []
                for f in uploaded_files:
                    img = Image.open(f)
                    # PIL 이미지를 바이트 배열로 변환 (API가 가장 선호하는 방식)
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format=img.format if img.format else 'JPEG')
                    contents.append(img_byte_arr.getvalue())
                
                # 마지막에 프롬프트 추가
                contents.append("이 3장의 사진을 종합하여 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘.")
                
                # 모델 호출
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=contents
                )
                
                st.session_state.ai_result = response.text
                st.success(f"👉 AI 분석 완료: {st.session_state.ai_result}")
            except Exception as e:
                st.error(f"분석 중 오류 발생: {str(e)}")

st.markdown("---")
# ... (이하 GPS, 소견 입력 및 발행 버튼은 동일)
