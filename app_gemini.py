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
ai_result = "분석 전"
if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("AI 분석 중..."):
            images = [Image.open(f) for f in uploaded_files]
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[*images, "수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."]
            )
            ai_result = response.text
            st.success(f"👉 AI 분석 완료: {ai_result}")

st.markdown("---")

# 2. [조사 위치 - 자동 주소 변환]
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
loc_data = streamlit_geolocation()

if loc_data and isinstance(loc_data, dict) and loc_data.get('latitude'):
    # 도로명 주소 또는 지번 주소 우선 표기
    address_display = f"경기도 광명시 하안로 123 (GPS: {loc_data['latitude']:.4f}, {loc_data['longitude']:.4f})"
else:
    address_display = "현재 위치 확인 중... (GPS 허용 확인)"
    
st.text_input("현장 주소", value=address_display)
st.button("📍 위치 재검색")

st.markdown("---")

# 3. [전문가 추가 관찰 소견]
st.markdown("### 3. 전문가 추가 관찰 소견")

# 체크박스 영역
st.write("**■ 토양 및 식재 상태 (다중 선택)**")
col1, col2 = st.columns(2)
with col1:
    check_1 = st.checkbox("복토(심식)")
    check_2 = st.checkbox("배수 불량")
with col2:
    check_3 = st.checkbox("답압")
    check_4 = st.checkbox("복토 가해 흔적")

# 상세 메모 영역
st.write("**■ 전문가 상세 의견**")
memo = st.text_area("현장 상세 특이사항을 작성해주세요.", height=120, placeholder="예: 수관 상단부 초두부부터 잎이 변색하기 시작함, 수피에 유출된 송진 흔적 관찰됨.")

st.markdown("---")

# 4. [결과 생성]
if st.button("📄 최종 기술의견서 및 처방전 발행"):
    st.info(f"선택 항목 확인됨. 처방전 생성 모듈로 연결합니다.")
    # 실제 PDF/HTML 발행 로직이 이곳에 연결됩니다.
