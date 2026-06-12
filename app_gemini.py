import streamlit as st
from google import genai
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. API 설정
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# 2. [사진 촬영 및 AI 동정]
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("AI가 사진 3장을 종합 분석 중입니다..."):
            images = [Image.open(f) for f in uploaded_files]
            # 모델명 안정화 (gemini-2.0-flash)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[*images, "이 3장의 사진을 종합하여 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."]
            )
            st.session_state.ai_result = response.text
            st.success(f"👉 AI 분석 완료: {st.session_state.ai_result}")

st.markdown("---")

# 3. [조사 위치 - GPS 자동 특정]
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
loc_data = streamlit_geolocation()

# 데이터 안전 처리 로직 적용
lat = loc_data.get('latitude') if isinstance(loc_data, dict) else None
lon = loc_data.get('longitude') if isinstance(loc_data, dict) else None

if lat is not None and lon is not None:
    address_display = f"경기도 광명시 (좌표: {lat:.4f}, {lon:.4f})"
else:
    address_display = "GPS 확인 중..."
    
st.text_input("현장 주소", value=address_display)
st.button("📍 위치 재검색")

st.markdown("---")

# 4. [전문가 추가 관찰 소견]
st.markdown("### 3. 전문가 추가 관찰 소견 (선택)")
col1, col2 = st.columns(2)
with col1:
    st.write("**■ 토양 및 식재**")
    s1, s2, s3, s4 = st.checkbox("복토(심식)"), st.checkbox("답압"), st.checkbox("배수 불량"), st.checkbox("복토 가해 흔적")
with col2:
    st.write("**■ 주변 생태**")
    e1, e2, e3 = st.checkbox("주변 공사 진행"), st.checkbox("인근 수목 동시 발병"), st.checkbox("가뭄/폭우 피해")

st.write("**■ 전문가 종합 메모**")
memo = st.text_area("현장 상세 특이사항 작성", height=120, placeholder="예: 수관 상단부 초두부부터 잎이 변색하기 시작함, 수피에 유출된 송진 흔적 관찰됨.")

st.markdown("---")

# 5. [최종 발행]
if st.button("📄 최종 기술의견서 및 처방전 발행", type="primary", use_container_width=True):
    st.success("데이터가 성공적으로 취합되었습니다.")
    st.write("---")
    st.subheader("📋 요약된 결과")
    st.write(f"**AI 진단:** {st.session_state.get('ai_result', '분석되지 않음')}")
    st.write(f"**현장 위치:** {address_display}")
    st.write("전문가 의견이 포함된 기술의견서 PDF 발행을 준비합니다.")
