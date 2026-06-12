import streamlit as st
import io
import re
import time
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정
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
if 'detected_species' not in st.session_state: st.session_state.detected_species = ""
if 'detected_disease' not in st.session_state: st.session_state.detected_disease = ""
if 'addr_data' not in st.session_state: st.session_state.addr_data = ""

# 2. [섹션 1] 전문가 정밀 동정 (프롬프트 보강)
st.markdown("### 1. 현장 사진 촬영 및 AI 정밀 동정")
uploaded_files = st.file_uploader("전체(수관), 근접(잎/줄기), 병반부 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if st.button("🚀 전문가 정밀 진단 시작"):
    if uploaded_files and len(uploaded_files) >= 1:
        with st.spinner("나무의사 AI가 생태적 분석을 수행 중입니다..."):
            # 503 오류 방지를 위한 재시도 로직
            for attempt in range(3):
                try:
                    models = list(client.models.list())
                    model_name = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                    
                    parts = []
                    for f in uploaded_files:
                        img = Image.open(f).convert("RGB")
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG')
                        parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                    
                    # [핵심 보강] 나무의사 수준의 정밀 진단 프롬프트
                    prompt = """
                    당신은 국가공인 나무의사입니다. 업로드된 사진을 기반으로 수목의 상태를 정밀 진단하세요.
                    분석 결과는 반드시 아래 형식을 엄격히 준수하여 출력할 것:
                    
                    수종: [국명(학명)]
                    병명: [진단된 병해충명 혹은 생리적 장애명]
                    피해도: [상/중/하]
                    전문가 소견: [병징에 대한 간략한 해설 및 추가 확인이 필요한 사항]
                    """
                    parts.append(types.Part.from_text(text=prompt))
                    
                    response = client.models.generate_content(model=model_name, contents=parts)
                    st.session_state.ai_result = response.text
                    
                    # 자동 파싱
                    s_match = re.search(r"수종:\s*\[(.*?)\]", response.text)
                    d_match = re.search(r"병명:\s*\[(.*?)\]", response.text)
                    
                    if s_match: st.session_state.detected_species = s_match.group(1)
                    if d_match: st.session_state.detected_disease = d_match.group(1)
                    
                    st.rerun()
                    break 
                except Exception as e:
                    if "503" in str(e) and attempt < 2:
                        time.sleep(2)
                        continue
                    st.error(f"진단 실패: {e}")
                    break
    else:
        st.warning("사진 3장을 모두 업로드해주세요.")

# 결과 출력 및 수정 UI
if st.session_state.ai_result:
    with st.expander("🔍 전문 진단 보고서", expanded=True):
        st.write(st.session_state.ai_result)
    
    col1, col2 = st.columns(2)
    with col1: st.text_input("수종 확정", value=st.session_state.detected_species, key="s_fix")
    with col2: st.text_input("병명/해충명 확정", value=st.session_state.detected_disease, key="d_fix")
