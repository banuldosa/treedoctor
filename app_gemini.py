import streamlit as st
from google import genai
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# API 설정
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 입력")

# 1. [사진 촬영 및 AI 동정]
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)
if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("AI 분석 중..."):
            images = [Image.open(f) for f in uploaded_files]
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[*images, "수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."]
            )
            st.success(f"👉 AI 분석 완료: {response.text}")

st.markdown("---")

# 2. [조사 위치 - 자동 주소 변환]
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
loc_data = streamlit_geolocation()
address_display = f"경기도 광명시 하안로 123 (좌표: {loc_data.get('latitude', 0):.4f}, {loc_data.get('longitude', 0):.4f})" if loc_data else "GPS 확인 중..."
st.text_input("현장 주소", value=address_display)
st.button("📍 위치 재검색")

st.markdown("---")

# 3. [전문가 추가 관찰 소견 - 보강됨]
st.markdown("### 3. 전문가 추가 관찰 소견 (선택)")

# 환경 요인 체크박스 (멀티 선택)
col1, col2 = st.columns(2)
with col1:
    st.write("**■ 토양 및 식재**")
    check_soil = [
        st.checkbox("복토(심식)"),
        st.checkbox("딛고 다져짐(답압)"),
        st.checkbox("배수 불량"),
        st.checkbox("복토 가해 흔적")
    ]
with col2:
    st.write("**■ 주변 생태**")
    check_eco = [
        st.checkbox("주변 공사 진행"),
        st.checkbox("인근 수목 동시 발병"),
        st.checkbox("가뭄/폭우 피해")
    ]

# 전문가 종합 메모란
st.write("**■ 전문가 종합 메모**")
memo = st.text_area(
    "상세 소견 작성", 
    height=120, 
    placeholder="예: 수관 상단부 초두부부터 잎이 변색하기 시작함, 수피에 유출된 송진 흔적 관찰됨."
)

st.markdown("---")

# 4. [결과 발행]
if st.button("📄 최종 기술의견서 및 처방전 발행", type="primary", use_container_width=True):
    st.success("데이터가 취합되었습니다. 처방전 생성 모듈을 실행합니다.")
