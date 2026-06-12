import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정 및 초기화 (반드시 맨 위에 위치해야 함)
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# API 클라이언트 초기화
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API 키를 확인하세요.")
    st.stop()

# 2. [화면 1] 사진 촬영 및 AI 동정
st.markdown("### 1. 현장 사진 촬영 및 업로드")
st.write("📷 **현장 수종 및 병반 사진 3장을 업로드하세요.**")
uploaded_files = st.file_uploader("", type=["jpg", "png"], accept_multiple_files=True)

# AI 결과 표시 및 로직
col_a, col_b = st.columns([3, 1])
with col_a:
    ai_result_input = st.text_input("AI 동정 결과", value=st.session_state.get('ai_result', ""), help="사진 분석 후 자동으로 채워집니다.")
with col_b:
    st.write("###") 
    if st.button("🚀 AI 분석", use_container_width=True):
        if uploaded_files and len(uploaded_files) == 3:
            with st.spinner("이미지 분석 중..."):
                try:
                    # 안정적인 모델 호출 및 이미지 최적화
                    parts = []
                    for f in uploaded_files:
                        img = Image.open(f)
                        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                        img.thumbnail((512, 512))
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG')
                        parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                    
                    parts.append(types.Part.from_text(text="이 사진들의 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                    
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=types.Content(role="user", parts=parts)
                    )
                    st.session_state.ai_result = response.text
                    st.rerun()
                except Exception as e:
                    st.error(f"분석 오류: {e}")
        else:
            st.warning("사진 3장을 모두 업로드해주세요.")

st.selectbox("💡 오동정 시 수종 직접 선택", ["선택하세요", "잣나무", "소나무", "느티나무", "은행나무", "기타"])

# 3. [화면 2] GPS 자동 특정
st.markdown("---")
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
loc_data = streamlit_geolocation()
lat = loc_data.get('latitude') if isinstance(loc_data, dict) else None
lon = loc_data.get('longitude') if isinstance(loc_data, dict) else None
addr = f"위도:{lat:.4f}, 경도:{lon:.4f}" if lat else "GPS 확인 중..."

c1, c2 = st.columns([3, 1])
with c1: st.text_input("현장 주소", value=addr)
with c2: 
    st.write("###")
    st.button("📍 갱신")

# 4. [화면 3] 전문가 소견
st.markdown("---")
st.markdown("### 3. 전문가 관찰 소견")
s1, s2, s3 = st.checkbox("복토(심식)"), st.checkbox("답압"), st.checkbox("배수 불량")
st.text_area("전문가 종합 메모", height=100, placeholder="예: 수관 상단부 변색 관찰됨.")

if st.button("📄 최종 기술의견서 및 처방전 발행", type="primary", use_container_width=True):
    st.success("데이터 취합 완료!")
