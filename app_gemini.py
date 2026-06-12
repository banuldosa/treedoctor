import streamlit as st
import io
import re
import time
import requests
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
if 'ai_result' not in st.session_state: st.session_state.ai_result = ""
if 'detected_species' not in st.session_state: st.session_state.detected_species = ""
if 'detected_disease' not in st.session_state: st.session_state.detected_disease = ""
if 'addr_data' not in st.session_state: st.session_state.addr_data = ""

# 2. [섹션 1] 사진 촬영 및 전문가 AI 동정
st.markdown("### 1. 현장 사진 촬영 및 AI 정밀 동정")
uploaded_files = st.file_uploader("현장 상황이 담긴 모든 사진을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if st.button("🚀 전문가 정밀 진단 시작"):
    if uploaded_files:
        with st.spinner(f"총 {len(uploaded_files)}장의 사진을 분석 중입니다..."):
            for attempt in range(3):
                try:
                    models = list(client.models.list())
                    model_name = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                    
                    parts = []
                    for f in uploaded_files:
                        img = Image.open(f).convert("RGB")
                        img.thumbnail((1024, 1024))
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG')
                        parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                    
                    prompt = """
                    당신은 국가공인 나무의사입니다. 사진을 보고 진단하세요.
                    형식:
                    수종: [국명(학명)]
                    병명: [병해충명/장애명]
                    피해도: [상/중/하]
                    전문가 소견: [해설 및 처방]
                    """
                    parts.append(types.Part.from_text(text=prompt))
                    
                    response = client.models.generate_content(model=model_name, contents=parts)
                    st.session_state.ai_result = response.text
                    
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

if st.session_state.ai_result:
    with st.expander("🔍 전문 진단 보고서", expanded=True):
        st.write(st.session_state.ai_result)
    
    col1, col2 = st.columns(2)
    with col1: st.text_input("수종 확정", value=st.session_state.detected_species, key="s_fix")
    with col2: st.text_input("병명/해충명 확정", value=st.session_state.detected_disease, key="d_fix")

    if st.button("🔄 수정된 정보로 보고서 재생성"):
        st.session_state.detected_species = st.session_state.s_fix
        st.session_state.detected_disease = st.session_state.d_fix
        with st.spinner("전문가 의견을 재작성 중입니다..."):
            try:
                models = list(client.models.list())
                model_name = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                re_prompt = f"수종: {st.session_state.detected_species}\n병명: {st.session_state.detected_disease}\n이 정보를 바탕으로 전문가 진단 보고서를 다시 작성해주세요."
                response = client.models.generate_content(model=model_name, contents=re_prompt)
                st.session_state.ai_result = response.text
                st.rerun()
            except Exception as e:
                st.error(f"보고서 재생성 실패: {e}")

# 3. [섹션 2] 조사 위치 (GPS 및 네이버 주소 변환)
st.markdown("---")
st.markdown("### 2. 조사 위치 (GPS)")
col_a, col_b = st.columns([3, 1])
with col_a:
    addr_input = st.text_input("현장 주소", value=st.session_state.addr_data)
with col_b:
    if st.button("📍 주소 자동입력"):
        loc = streamlit_geolocation()
        if loc and loc.get('latitude'):
            lat, lon = loc['latitude'], loc['longitude']
            url = f"https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc?coords={lon},{lat}&output=json"
            headers = {
                "X-NCP-APIGW-API-KEY-ID": st.secrets["NAVER_CLIENT_ID"],
                "X-NCP-APIGW-API-KEY": st.secrets["NAVER_CLIENT_SECRET"]
            }
            try:
                res = requests.get(url, headers=headers).json()
                if res['status']['code'] == 0 and res['results']:
                    area = res['results'][0]['region']
                    addr = f"{area['area1']['name']} {area['area2']['name']} {area['area3']['name']} {area['area4']['name']}".strip()
                    st.session_state.addr_data = addr
                    st.rerun()
                else:
                    st.warning("주소 정보를 찾을 수 없습니다.")
            except Exception as e:
                st.error(f"주소 변환 실패: {e}")

# 4. [섹션 3] 전문가 소견
st.markdown("---")
st.markdown("### 3. 전문가 관찰 소견")
st.text_area("전문가 종합 메모", height=100)

if st.button("📄 최종 기술의견서 발행", type="primary", use_container_width=True):
    st.success("데이터 취합 완료! PDF 생성 모듈 연동 준비 완료.")
