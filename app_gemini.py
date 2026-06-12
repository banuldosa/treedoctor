import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정 (가장 먼저 실행되어야 함)
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# 2. API 클라이언트 설정
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. 사진 분석 영역
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("AI 분석 중..."):
            try:
                parts = []
                for f in uploaded_files:
                    img = Image.open(f)
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                parts.append(types.Part.from_text(text="이 사진들의 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=types.Content(role="user", parts=parts)
                )
                st.session_state.ai_result = response.text
                st.success(f"결과: {st.session_state.ai_result}")
            except Exception as e:
                st.error(f"분석 오류: {e}")

# 4. GPS 영역
st.markdown("### 2. 조사 위치 (GPS)")
loc_data = streamlit_geolocation()
lat = loc_data.get('latitude') if isinstance(loc_data, dict) else None
lon = loc_data.get('longitude') if isinstance(loc_data, dict) else None
addr = f"위도:{lat:.4f}, 경도:{lon:.4f}" if lat else "GPS 확인 중..."
st.text_input("현장 주소", value=addr)

# 5. 소견 영역
st.markdown("### 3. 전문가 소견")
col1, col2 = st.columns(2)
with col1:
    s1 = st.checkbox("복토(심식)")
    s2 = st.checkbox("배수 불량")
with col2:
    s3 = st.checkbox("답압")
    s4 = st.checkbox("복토 가해 흔적")
memo = st.text_area("상세 메모", placeholder="예: 송진 유출 흔적 관찰됨.")

if st.button("📄 처방전 발행"):
    st.info("처방전 생성 프로세스 실행 중...")
