import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정 및 초기화 (반드시 맨 위)
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# API 클라이언트 초기화
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API 키를 확인하세요.")
    st.stop()

# 세션 데이터 초기화
if 'ai_result' not in st.session_state: st.session_state.ai_result = ""
if 'addr_data' not in st.session_state: st.session_state.addr_data = ""

# 2. [섹션 1] 사진 촬영 및 전문가 AI 동정
st.markdown("### 1. 현장 사진 촬영 및 AI 정밀 동정")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if st.button("🚀 AI 전문가 정밀 분석 시작"):
    if uploaded_files and len(uploaded_files) >= 1:
        with st.spinner("전문가 AI가 수종 및 병해충을 진단 중입니다..."):
            try:
                models = list(client.models.list())
                model_name = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                
                parts = []
                for f in uploaded_files:
                    img = Image.open(f).convert("RGB")
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                prompt = "당신은 숙련된 나무의사입니다. 사진을 보고 '수종:OOO(학명), 병명:OOO, 피해도:상/중/하' 형식으로 진단해줘."
                parts.append(types.Part.from_text(text=prompt))
                
                response = client.models.generate_content(model=model_name, contents=parts)
                st.session_state.ai_result = response.text
                st.rerun()
            except Exception as e:
                st.error(f"분석 실패: {e}")
    else:
        st.warning("사진을 먼저 업로드해주세요.")

if st.session_state.ai_result:
    st.info(f"진단 결과: {st.session_state.ai_result}")
    col1, col2 = st.columns(2)
    with col1: st.text_input("수종 확정", value="분석 결과 기반 자동입력")
    with col2: st.text_input("병명/해충명 확정", value="분석 결과 기반 자동입력")

# 3. [섹션 2] GPS 위치 수집
st.markdown("---")
st.markdown("### 2. 조사 위치 (GPS)")
col1, col2 = st.columns([3, 1])
with col1:
    addr_input = st.text_input("현장 주소", value=st.session_state.addr_data)
with col2:
    if st.button("📍 GPS 가져오기"):
        loc = streamlit_geolocation()
        if loc and isinstance(loc, dict) and loc.get('latitude'):
            st.session_state.addr_data = f"위도:{loc['latitude']:.4f}, 경도:{loc['longitude']:.4f}"
            st.rerun()
        else:
            st.warning("위치 권한을 확인하세요.")

# 4. [섹션 3] 전문가 소견
st.markdown("### 3. 전문가 관찰 소견")
c1, c2 = st.columns(2)
with c1:
    st.checkbox("복토(심식)"); st.checkbox("답압"); st.checkbox("배수 불량")
with c2:
    st.checkbox("복토 가해 흔적"); st.checkbox("주변 공사"); st.checkbox("인근 수목 동시 발병")
st.text_area("전문가 종합 메모", height=100)

if st.button("📄 최종 기술의견서 발행", type="primary", use_container_width=True):
    st.success("데이터 취합 완료!")
