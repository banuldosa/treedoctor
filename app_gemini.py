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
    st.error("API 키를 확인하세요. (Settings > Secrets)")
    st.stop()

# 세션 데이터 초기화
defaults = {'ai_result': "", 'detected_species': "", 'detected_disease': "", 'addr_data': "", 'uploaded_images': []}
for key, value in defaults.items():
    if key not in st.session_state: st.session_state[key] = value

# 모델 자동 선택 함수 (404 방지)
def get_model():
    models = [m.name for m in client.models.list()]
    # 범용적으로 사용 가능한 최신 모델로 우선 탐색
    for preferred in ['models/gemini-3.5-flash', 'models/gemini-2.0-flash', 'models/gemini-1.5-flash']:
        if preferred in models: return preferred
    return models[0]

# 2. [섹션 1] 사진 촬영 및 전문가 AI 동정
st.markdown("### 1. 현장 사진 촬영 및 AI 정밀 동정")
uploaded_files = st.file_uploader("현장 상황이 담긴 모든 사진을 업로드하세요.", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("🚀 전문가 정밀 진단 시작"):
    if uploaded_files:
        st.session_state.uploaded_images = uploaded_files
        with st.spinner("이미지 최적화 및 정밀 진단 중..."):
            try:
                parts = []
                for f in uploaded_files:
                    # [최적화 코드] 이미지 크기 조정 및 압축
                    img = Image.open(f).convert("RGB")
                    # 1024px로 리사이징하여 토큰 효율 극대화
                    img.thumbnail((1024, 1024))
                    
                    # 메모리 내에서 압축 저장
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=85)
                    img_bytes = img_byte_arr.getvalue()
                    
                    parts.append(types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'))
                
                prompt = "당신은 국가공인 나무의사입니다. 사진을 보고 진단하세요. 형식:\n수종: [국명(학명)]\n병명: [병해충명/장애명]\n피해도: [상/중/하]\n전문가 소견: [해설 및 처방]"
                parts.append(types.Part.from_text(text=prompt))
                
                response = client.models.generate_content(model=get_model(), contents=parts)
                st.session_state.ai_result = response.text
                
                # 결과 파싱
                s_match = re.search(r"수종:\s*\[(.*?)\]", response.text)
                d_match = re.search(r"병명:\s*\[(.*?)\]", response.text)
                st.session_state.detected_species = s_match.group(1) if s_match else ""
                st.session_state.detected_disease = d_match.group(1) if d_match else ""
                
                st.rerun()
            except Exception as e:
                st.error(f"진단 실패: {e}")
    else:
        st.warning("사진을 하나 이상 업로드해주세요.")

# 결과 출력 및 수정 섹션
if st.session_state.ai_result:
    with st.expander("🔍 전문 진단 보고서", expanded=True):
        if st.session_state.uploaded_images:
            cols = st.columns(min(len(st.session_state.uploaded_images), 3))
            for i, img_file in enumerate(st.session_state.uploaded_images):
                cols[i % 3].image(img_file, use_container_width=True)
        st.write(st.session_state.ai_result)
    
    col1, col2 = st.columns(2)
    with col1: st.text_input("수종 확정", value=st.session_state.detected_species, key="s_fix")
    with col2: st.text_input("병명 확정", value=st.session_state.detected_disease, key="d_fix")

    if st.button("🔄 수정된 정보로 보고서 재생성"):
        st.session_state.detected_species = st.session_state.s_fix
        st.session_state.detected_disease = st.session_state.d_fix
        st.rerun()
