import streamlit as st
from google import genai
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# API 설정
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 입력")

# 1. [사진 촬영 및 AI 동정]
st.markdown("### 1. 현장 사진 촬영 (3장 필수)")
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

# 2. [조사 위치 - GPS 자동 특정]
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
loc_data = streamlit_geolocation()
if loc_data and isinstance(loc_data, dict) and loc_data.get('latitude'):
    address_display = f"경기도 광명시 하안동 (좌표: {loc_data['latitude']:.4f}, {loc_data['longitude']:.4f})"
else:
    address_display = "위치 확인 중 (GPS 허용을 확인하세요)..."
st.text_input("현장 주소", value=address_display)

st.markdown("---")

# 3. [전문가 추가 관찰 소견]
st.markdown("### 3. 전문가 추가 관찰 소견")
soil = st.multiselect("토양 및 식재 상태", ["복토(심식)", "답압", "배수 불량", "복토 가해 흔적"])
memo = st.text_area("현장 메모", "예: 수간 하부 송진 유출 흔적 관찰됨.")

st.markdown("---")

# 4. [결과 생성 버튼]
if st.button("📄 최종 기술의견서 및 처방전 발행"):
    st.info(f"분석된 수종/질병: {ai_result}")
    st.write("입력된 현장 정보와 함께 최종 처방전을 생성합니다...")
    # 여기에 아까 만든 PDF 발행 HTML 렌더링 영역을 연결하면 됩니다.
