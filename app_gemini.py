import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 및 API 설정
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 2. [단계별 수목 피해 분석]
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("이미지 최적화 및 AI 분석 중..."):
            try:
                # [수정] model_type 인자 제거하여 호출 오류 해결
                models = list(client.models.list())
                # 리스트가 비어있지 않으면 첫 번째 모델 사용
                model_name = models[0].name if models else 'gemini-1.5-flash'
                
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
                    model=model_name,
                    contents=types.Content(role="user", parts=parts)
                )
                
                st.session_state.ai_result = response.text
                st.success(f"👉 AI 분석 완료 ({model_name}): {st.session_state.ai_result}")
            except Exception as e:
                st.error(f"분석 오류: {e}")

st.markdown("---")

# 3. [조사 위치]
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
loc_data = streamlit_geolocation()
lat = loc_data.get('latitude') if isinstance(loc_data, dict) else None
lon = loc_data.get('longitude') if isinstance(loc_data, dict) else None
addr = f"위도:{lat:.4f}, 경도:{lon:.4f}" if lat else "GPS 확인 중..."
st.text_input("현장 주소", value=addr)

# 4. [전문가 소견 및 결과 발행]
st.markdown("### 3. 전문가 소견")
memo = st.text_area("현장 상세 특이사항", height=100)

if st.button("📄 최종 기술의견서 및 처방전 발행", type="primary", use_container_width=True):
    st.success("데이터 취합 완료! 처방전 발행 로직으로 연결합니다.")
