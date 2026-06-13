import streamlit as st
import io
import re
import requests
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="스마트 나무의사", layout="centered", page_icon="🌲")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# API 클라이언트 초기화
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API 키를 확인하세요. (Settings > Secrets에서 확인)")
    st.stop()

# 세션 상태 초기화
defaults = {'ai_result': "", 'detected_species': "", 'detected_disease': "", 'addr_data': "", 'uploaded_images': []}
for key, value in defaults.items():
    if key not in st.session_state: st.session_state[key] = value

# 모델 자동 선택 함수
def get_model():
    # 404 에러를 방지하기 위해 사용 가능한 모델 리스트 중 gemini-3.5-flash 우선 선택
    models = [m.name for m in client.models.list()]
    if 'models/gemini-3.5-flash' in models: return 'models/gemini-3.5-flash'
    return models[0]

# 2. [섹션 1] 사진 촬영 및 전문가 AI 동정
st.markdown("### 1. 현장 사진 촬영 및 AI 정밀 동정")
uploaded_files = st.file_uploader("현장 사진을 모두 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 전문가 정밀 진단 시작"):
        st.session_state.uploaded_images = uploaded_files
        with st.spinner("전문가 AI가 진단 중입니다..."):
            try:
                parts = []
                for f in uploaded_files:
                    img = Image.open(f).convert("RGB")
                    img.thumbnail((1024, 1024))
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG', quality=85)
                    parts.append(types.Part.from_bytes(data=buf.getvalue(), mime_type='image/jpeg'))
                
                parts.append(types.Part.from_text(text="당신은 국가공인 나무의사입니다. 사진을 보고 진단하세요. 형식:\n수종: [국명(학명)]\n병명: [병해충명/장애명]\n피해도: [상/중/하]\n전문가 소견: [해설 및 처방]"))
                
                response = client.models.generate_content(model=get_model(), contents=parts)
                st.session_state.ai_result = response.text
                
                # 정규식으로 결과 추출
                s_match = re.search(r"수종:\s*\[(.*?)\]", response.text)
                d_match = re.search(r"병명:\s*\[(.*?)\]", response.text)
                st.session_state.detected_species = s_match.group(1) if s_match else ""
                st.session_state.detected_disease = d_match.group(1) if d_match else ""
                st.rerun()
            except Exception as e:
                st.error(f"진단 실패: {e}")

if st.session_state.ai_result:
    with st.expander("🔍 전문 진단 보고서", expanded=True):
        st.write(st.session_state.ai_result)
    
    # 수정 영역
    c1, c2 = st.columns(2)
    with c1: st.text_input("수종 확정", key="s_fix", value=st.session_state.detected_species)
    with c2: st.text_input("병명/해충명 확정", key="d_fix", value=st.session_state.detected_disease)
    
    if st.button("🔄 수정된 정보로 보고서 재생성"):
        st.session_state.detected_species = st.session_state.s_fix
        st.session_state.detected_disease = st.session_state.d_fix
        st.rerun()

# 3. [섹션 2] 조사 위치 (간소화)
st.markdown("### 2. 조사 위치 (GPS)")
if st.button("📍 주소 자동입력 (현재위치)"):
    loc = streamlit_geolocation()
    if loc and loc.get('latitude'):
        # 간단한 GPS 표기 혹은 Naver API 연동
        st.session_state.addr_data = f"위도:{loc['latitude']:.4f}, 경도:{loc['longitude']:.4f}"
        st.rerun()
st.text_input("현장 주소", value=st.session_state.addr_data)

# 4. [섹션 3] 최종 발행
st.markdown("### 3. 전문가 관찰 소견")
memo = st.text_area("전문가 종합 메모")
if st.button("📄 최종 기술의견서 발행"):
    st.balloons()
    st.success("데이터 취합 완료! PDF 생성 모듈 연동 준비 완료.")
