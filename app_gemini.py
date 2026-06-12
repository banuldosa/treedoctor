import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 2. [단계 1] 현장 사진 촬영 및 AI 자동 수종 동정
st.markdown("### 1. 현장 사진 촬영 및 업로드")
uploaded_files = st.file_uploader("현장 사진 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

col_a, col_b = st.columns([3, 1])
with col_a:
    ai_result_input = st.text_input("AI 동정 결과", value=st.session_state.get('ai_result', ""))
with col_b:
    st.write("###")
    if st.button("🚀 AI 분석 시작", use_container_width=True):
        if uploaded_files and len(uploaded_files) == 3:
            with st.spinner("이미지 분석 중..."):
                try:
                    # [핵심 수정] 서버에서 지원하는 모델 목록을 직접 확인하여 404 방지
                    available_models = [m.name for m in client.models.list()]
                    # 목록에서 1.5-flash 계열이 있으면 사용하고, 없으면 목록의 첫 번째 모델 사용
                    model_to_use = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
                    
                    parts = []
                    for f in uploaded_files:
                        img = Image.open(f)
                        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                        img.thumbnail((512, 512))
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG')
                        parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                    
                    parts.append(types.Part.from_text(text="수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                    
                    # [핵심 수정] 확인된 모델 이름으로 호출
                    response = client.models.generate_content(
                        model=model_to_use, 
                        contents=types.Content(role="user", parts=parts)
                    )
                    st.session_state.ai_result = response.text
                    st.rerun()
                except Exception as e:
                    st.error(f"분석 오류: {e}")
                    st.write("현재 사용 가능한 모델 목록:", [m for m in available_models])
        else:
            st.warning("사진 3장을 업로드해주세요.")

st.selectbox("💡 오동정 시 수종 직접 선택", ["선택하세요", "잣나무", "소나무", "느티나무", "기타"])

# 3. [단계 2] GPS 기반 위치 자동 특정
st.markdown("---")
st.markdown("### 2. 조사 위치 (GPS)")
loc_data = streamlit_geolocation()
lat = loc_data.get('latitude') if isinstance(loc_data, dict) else None
addr = f"위도:{lat:.4f}, 경도:{loc_data.get('longitude'):.4f}" if lat else "위치 확인 중..."
st.text_input("현장 주소", value=addr)

# 4. [단계 3] 전문가 관찰 소견
st.markdown("---")
st.markdown("### 3. 전문가 관찰 소견")
c1, c2 = st.columns(2)
with c1:
    s1 = st.checkbox("복토(심식)")
    s2 = st.checkbox("답압")
    s3 = st.checkbox("배수 불량")
with c2:
    s4 = st.checkbox("복토 가해 흔적")
    s5 = st.checkbox("주변 공사")
    s6 = st.checkbox("동시 발병")

st.text_area("전문가 종합 메모", height=100)

if st.button("📄 최종 기술의견서 및 처방전 발행", type="primary", use_container_width=True):
    st.success("데이터 취합 완료!")
