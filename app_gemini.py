import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# [화면 1] 1. 상단: 현장 사진 촬영 및 AI 자동 수종 동정
st.markdown("### 1. 현장 사진 촬영 및 업로드")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

# AI 동정 결과 입력 칸 (수정 가능)
col_a, col_b = st.columns([3, 1])
with col_a:
    ai_result_text = st.text_input("AI 동정 결과", value=st.session_state.get('ai_result', ""))
with col_b:
    st.write("###") # 간격 맞춤
    if st.button("🚀 AI 분석"):
        if uploaded_files and len(uploaded_files) == 3:
            with st.spinner("AI가 수종을 분석 중입니다..."):
                try:
                    models = list(client.models.list())
                    model_name = models[0].name if models else 'gemini-1.5-flash'
                    parts = []
                    for f in uploaded_files:
                        img = Image.open(f)
                        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                        img.thumbnail((512, 512))
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG')
                        parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                    parts.append(types.Part.from_text(text="이 3장의 사진을 종합하여 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                    
                    response = client.models.generate_content(model=model_name, contents=types.Content(role="user", parts=parts))
                    st.session_state.ai_result = response.text
                    st.rerun()
                except Exception as e:
                    st.error(f"분석 오류: {e}")
        else:
            st.warning("사진 3장을 모두 업로드해주세요.")

# 수종 직접 선택/검색 (드롭다운)
st.selectbox("수종 직접 선택/검색", ["잣나무", "소나무", "느티나무", "은행나무", "기타 수종"])

st.markdown("---")

# [화면 1] 2. 중단: GPS 기반 위치 자동 특정
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
loc_data = streamlit_geolocation()
lat = loc_data.get('latitude') if isinstance(loc_data, dict) else None
lon = loc_data.get('longitude') if isinstance(loc_data, dict) else None
addr = f"위도:{lat:.4f}, 경도:{lon:.4f}" if lat else "위치 정보 없음"

col_c, col_d = st.columns([3, 1])
with col_c:
    st.text_input("현장 주소", value=addr)
with col_d:
    st.write("###")
    st.button("📍 위치 갱신")

st.markdown("---")

# [화면 1] 3. 하단: 전문가용 추가 관찰 소견 작성
st.markdown("### 3. 전문가 관찰 소견")
st.write("환경 요인 빠른 체크")
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
    st.success("데이터가 취합되었습니다. 처방전 발행 모듈을 실행합니다.")
