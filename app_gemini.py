import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 및 API 설정
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# API Client 초기화
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API 키 설정이 필요합니다. Streamlit Secrets를 확인하세요.")
    st.stop()

# 세션 데이터 초기화 (에러 방지)
if 'ai_result' not in st.session_state: st.session_state.ai_result = ""
if 'address_input' not in st.session_state: st.session_state.address_input = ""

# ---------------------------------------------------------
# [화면 1] 사진 촬영 및 AI 동정 (상단)
# ---------------------------------------------------------
st.markdown("### 1. 현장 사진 촬영 및 업로드")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

col_a, col_b = st.columns([3, 1])
with col_a:
    ai_result_input = st.text_input("AI 동정 결과", value=st.session_state.ai_result, help="사진 분석 후 결과가 자동으로 입력됩니다.")
with col_b:
    st.write("###")
    if st.button("🚀 AI 분석 시작", use_container_width=True):
        if uploaded_files and len(uploaded_files) == 3:
            with st.spinner("이미지 분석 중..."):
                try:
                    models = list(client.models.list())
                    model_name = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                    
                    parts = []
                    for f in uploaded_files:
                        img = Image.open(f)
                        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                        img.thumbnail((512, 512))
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG')
                        parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                    
                    parts.append(types.Part.from_text(text="이 사진들의 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                    
                    response = client.models.generate_content(model=model_name, contents=types.Content(role="user", parts=parts))
                    st.session_state.ai_result = response.text
                    st.rerun()
                except Exception as e:
                    st.error(f"분석 오류: {e}")
        else:
            st.warning("사진 3장을 모두 업로드해주세요.")

st.selectbox("💡 오동정 시 수종 직접 선택", ["선택하세요", "잣나무", "소나무", "느티나무", "은행나무", "기타 수종"])

# ---------------------------------------------------------
# [화면 2] GPS 기반 위치 자동 특정 (중단)
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
col_c, col_d = st.columns([3, 1])
with col_c:
    # 안전하게 session_state 값 불러오기
    addr_val = st.session_state.get('address_input', "")
    addr_input = st.text_input("현장 주소", value=addr_val, key="address_input")
with col_d:
    st.write("###")
    if st.button("📍 현재 위치(GPS) 가져오기", use_container_width=True):
        loc = streamlit_geolocation()
        # [방어 코드] 데이터 타입 및 존재 여부 확인
        if loc and isinstance(loc, dict) and loc.get('latitude') is not None and loc.get('longitude') is not None:
            st.session_state.address_input = f"위도:{loc['latitude']:.4f}, 경도:{loc['longitude']:.4f}"
            st.rerun()
        else:
            st.warning("위치 정보를 가져올 수 없습니다. 브라우저 위치 권한을 확인해주세요.")

# ---------------------------------------------------------
# [화면 3] 전문가 관찰 소견 (하단)
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 3. 전문가 관찰 소견")
c1, c2 = st.columns(2)
with c1:
    s1 = st.checkbox("복토(심식)")
    s2 = st.checkbox("딛고 다져짐(답압)")
    s3 = st.checkbox("배수 불량")
with c2:
    s4 = st.checkbox("복토 가해 흔적")
    s5 = st.checkbox("주변 공사 진행")
    s6 = st.checkbox("인근 수목 동시 발병")

st.text_area("전문가 종합 메모", height=100, placeholder="예: 수관 상단부 초두부부터 잎이 변색하기 시작함, 수피에 유출된 송진 흔적 관찰됨.")

if st.button("📄 최종 기술의견서 및 처방전 발행", type="primary", use_container_width=True):
    st.success("데이터 취합 완료! 처방전 발행 로직으로 연결합니다.")
