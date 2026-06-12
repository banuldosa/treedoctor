import streamlit as st
import io
import re
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

# 세션 데이터 초기화
if 'ai_species' not in st.session_state: st.session_state.ai_species = ""
if 'ai_disease' not in st.session_state: st.session_state.ai_disease = ""

# 2. [섹션 1] 사진 촬영 및 자동완성 동정
st.markdown("### 1. 현장 사진 촬영 및 자동 동정")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if st.button("🚀 AI 분석 및 정보 자동완성"):
    if uploaded_files and len(uploaded_files) >= 1:
        with st.spinner("AI가 수종과 병명을 분석 중입니다..."):
            try:
                models = list(client.models.list())
                model_name = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                
                parts = []
                for f in uploaded_files:
                    img = Image.open(f).convert("RGB")
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                # 결과 포맷 지정 (파싱을 위해 고정)
                prompt = "사진을 분석해. 결과는 반드시 '수종: [수종명], 병명: [병명]' 형식으로만 답해."
                parts.append(types.Part.from_text(text=prompt))
                
                response = client.models.generate_content(model=model_name, contents=parts)
                
                # [핵심] 결과 파싱 및 자동완성
                res_text = response.text
                species_match = re.search(r"수종:\s*\[(.*?)\]", res_text)
                disease_match = re.search(r"병명:\s*\[(.*?)\]", res_text)
                
                st.session_state.ai_species = species_match.group(1) if species_match else "분석 실패"
                st.session_state.ai_disease = disease_match.group(1) if disease_match else "분석 실패"
                st.rerun()
            except Exception as e:
                st.error(f"분석 오류: {e}")
    else:
        st.warning("사진을 업로드해주세요.")

# 자동완성된 값을 바로 수정할 수 있는 입력창
st.text_input("수종 확정", value=st.session_state.ai_species, key="s1")
st.text_input("병명/해충명 확정", value=st.session_state.ai_disease, key="d1")

# 3. [섹션 2] GPS 위치 특정
st.markdown("---")
st.markdown("### 2. 조사 위치 (GPS)")
col_c, col_d = st.columns([3, 1])
with col_c:
    addr_input = st.text_input("현장 주소", key="addr_key")
with col_d:
    if st.button("📍 현재 위치 가져오기"):
        loc = streamlit_geolocation()
        if loc and isinstance(loc, dict) and loc.get('latitude'):
            st.session_state.addr_key = f"위도:{loc['latitude']:.4f}, 경도:{loc['longitude']:.4f}"
            st.rerun()

# 4. [섹션 3] 전문가 관찰 소견
st.markdown("---")
st.markdown("### 3. 전문가 관찰 소견")
st.text_area("종합 메모", height=100)

if st.button("📄 기술의견서 발행"):
    st.success("데이터 취합 완료!")
