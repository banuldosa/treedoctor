import streamlit as st
import io
import re  # [추가] 텍스트 파싱을 위한 정규표현식 라이브러리
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# API 클라이언트 초기화
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API 키를 확인하세요.")
    st.stop()

# 세션 데이터 초기화 (자동완성을 위해 변수 분리)
if 'ai_result' not in st.session_state: st.session_state.ai_result = ""
if 'detected_species' not in st.session_state: st.session_state.detected_species = "분석 전"
if 'detected_disease' not in st.session_state: st.session_state.detected_disease = "분석 전"
if 'addr_data' not in st.session_state: st.session_state.addr_data = ""

# 2. [섹션 1] 사진 촬영 및 전문가 AI 동정
st.markdown("### 1. 현장 사진 촬영 및 AI 정밀 동정")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if st.button("🚀 AI 전문가 정밀 분석 시작"):
    if uploaded_files and len(uploaded_files) >= 1:
        with st.spinner("전문가 AI가 진단 중입니다..."):
            try:
                models = list(client.models.list())
                model_name = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                
                parts = []
                for f in uploaded_files:
                    img = Image.open(f).convert("RGB")
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                # [수정] 파싱을 쉽게 하기 위해 결과 형식을 명확히 요청
                prompt = "당신은 숙련된 나무의사입니다. 사진을 보고 다음 형식으로만 답해줘.\n수종: [수종명(학명)]\n병명: [병명/해충명]\n피해도: [상/중/하]"
                parts.append(types.Part.from_text(text=prompt))
                
                response = client.models.generate_content(model=model_name, contents=parts)
                st.session_state.ai_result = response.text
                
                # [추가] 결과 자동 파싱 로직
                species_match = re.search(r"수종:\s*\[(.*?)\]", response.text)
                disease_match = re.search(r"병명:\s*\[(.*?)\]", response.text)
                
                if species_match: st.session_state.detected_species = species_match.group(1)
                if disease_match: st.session_state.detected_disease = disease_match.group(1)
                
                st.rerun()
            except Exception as e:
                st.error(f"분석 실패: {e}")
    else:
        st.warning("사진을 먼저 업로드해주세요.")

if st.session_state.ai_result:
    st.info(f"AI 원본 진단 결과:\n{st.session_state.ai_result}")
    col1, col2 = st.columns(2)
    # [수정] value에 session_state에 저장된 자동완성 값을 할당
    with col1: st.text_input("수종 확정", value=st.session_state.detected_species)
    with col2: st.text_input("병명/해충명 확정", value=st.session_state.detected_disease)

# 3. [섹션 2] GPS 위치 수집 (기존 유지)
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

# 4. [섹션 3] 전문가 소견 (기존 유지)
st.markdown("---")
st.markdown("### 3. 전문가 관찰 소견")
# ... (생략: 기존 코드와 동일하게 유지)
