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

# 2. [섹션 1] 사진 개수 제한 없는 전문가 정밀 동정
st.markdown("### 1. 현장 사진 촬영 및 AI 정밀 동정")
# accept_multiple_files=True는 유지하되, 제한 조건(len==3)을 제거
uploaded_files = st.file_uploader("현장 상황이 담긴 모든 사진을 업로드하세요 (개수 제한 없음).", type=["jpg", "png"], accept_multiple_files=True)

if st.button("🚀 전문가 정밀 진단 시작"):
    if uploaded_files: # 제한 조건 제거
        with st.spinner(f"총 {len(uploaded_files)}장의 사진을 분석 중입니다..."):
            for attempt in range(3):
                try:
                    models = list(client.models.list())
                    model_name = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                    
                    parts = []
                    # 모든 사진을 리스트에 담아 분석 요청
                    for f in uploaded_files:
                        img = Image.open(f).convert("RGB")
                        img.thumbnail((1024, 1024)) # 너무 큰 이미지는 크기 조절하여 전송 효율 향상
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG')
                        parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                    
                    prompt = """
                    당신은 국가공인 나무의사입니다. 업로드된 다수의 현장 사진을 종합적으로 분석하여 수목의 상태를 진단하세요.
                    수종: [국명(학명)]
                    병명: [진단된 병해충명 혹은 생리적 장애명]
                    피해도: [상/중/하]
                    전문가 소견: [종합적인 피해 원인 분석 및 처방 의견]
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
        st.warning("사진을 하나 이상 업로드해주세요.")

# 결과 출력 및 수정 UI (이전과 동일)
if st.session_state.ai_result:
    with st.expander("🔍 전문 진단 보고서", expanded=True):
        st.write(st.session_state.ai_result)
    
    col1, col2 = st.columns(2)
    with col1: st.text_input("수종 확정", value=st.session_state.detected_species, key="s_fix")
    with col2: st.text_input("병명/해충명 확정", value=st.session_state.detected_disease, key="d_fix")
