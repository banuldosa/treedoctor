import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# 2. API 설정 (secrets.toml에서 관리)
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API 키 설정이 필요합니다. Streamlit Secrets 설정을 확인하세요.")
    st.stop()

# 3. [사진 촬영 및 AI 동정]
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("이미지 최적화 및 AI 분석 중..."):
            try:
                parts = []
                for f in uploaded_files:
                    # 이미지 리사이징으로 토큰 소모량 80% 절감
                    img = Image.open(f)
                    img.thumbnail((512, 512)) 
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                parts.append(types.Part.from_text(text="이 3장의 사진을 종합하여 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                
                # 안정적인 모델 호출 (gemini-1.5-flash)
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=types.Content(role="user", parts=parts)
                )
                
                st.session_state.ai_result = response.text
                st.success(f"👉 AI 분석 완료: {st.session_state.ai_result}")
            except Exception as e:
                st.error(f"분석 오류 발생: {e}")

st.markdown("---")

# 4. [조사 위치 - GPS 자동 특정]
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
loc_data = streamlit_geolocation()
lat = loc_data.get('latitude') if isinstance(loc_data, dict) else None
lon = loc_data.get('longitude') if isinstance(loc_data, dict) else None
addr = f"위도:{lat:.4f}, 경도:{lon:.4f}" if lat else "GPS 확인 중..."
st.text_input("현장 주소", value=addr)
st.button("📍 위치 재검색")

st.markdown("---")

# 5. [전문가 추가 관찰 소견]
st.markdown("### 3. 전문가 추가 관찰 소견")
col1, col2 = st.columns(2)
with col1:
    s1, s2 = st.checkbox("복토(심식)"), st.checkbox("배수 불량")
with col2:
    s3, s4 = st.checkbox("답압"), st.checkbox("복토 가해 흔적")
memo = st.text_area("상세 특이사항", height=100, placeholder="예: 수관 상단부 변색 관찰됨.")

# 6. [결과 발행]
if st.button("📄 최종 기술의견서 및 처방전 발행", type="primary", use_container_width=True):
    st.success("데이터가 취합되었습니다. 이제 PDF 발행 모듈을 연결할 수 있습니다.")
