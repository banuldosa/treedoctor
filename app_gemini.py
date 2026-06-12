import streamlit as st
import io
import re
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 세션 데이터 초기화
if 'ai_raw' not in st.session_state: st.session_state.ai_raw = ""
if 'detected_species' not in st.session_state: st.session_state.detected_species = ""
if 'detected_disease' not in st.session_state: st.session_state.detected_disease = ""
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
                
                # 결과 포맷을 고정하여 파싱이 쉽도록 프롬프트 수정
                prompt = "수종: [수종명(학명)], 병명: [병명/해충명], 피해도: [상/중/하] 형식으로만 간결하게 답해줘."
                parts.append(types.Part.from_text(text=prompt))
                
                response = client.models.generate_content(model=model_name, contents=parts)
                st.session_state.ai_raw = response.text
                
                # [자동 파싱 로직]
                species_match = re.search(r"수종:\s*\[(.*?)\]", response.text)
                disease_match = re.search(r"병명:\s*\[(.*?)\]", response.text)
                
                st.session_state.detected_species = species_match.group(1) if species_match else ""
                st.session_state.detected_disease = disease_match.group(1) if disease_match else ""
                st.rerun()
            except Exception as e:
                st.error(f"분석 실패: {e}")
    else:
        st.warning("사진을 먼저 업로드해주세요.")

# [보강] 자동 입력된 결과를 수정 가능하게 배치
col1, col2 = st.columns(2)
with col1:
    st.text_input("수종(국명/학명)", value=st.session_state.detected_species, key="species_input")
with col2:
    st.text_input("병명/해충명", value=st.session_state.detected_disease, key="disease_input")

# 3. [섹션 2] GPS 기반 위치
st.markdown("---")
st.markdown("### 2. 조사 위치 (GPS)")
# ... (기존 GPS 로직 유지)
