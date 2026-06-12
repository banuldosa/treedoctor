import streamlit as st
from google import genai
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# Google Gemini API 설정
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="스마트 나무의사 - 현장", layout="centered")
st.title("🌲 스마트 나무의사 (현장 실무형)")

# ---------------------------------------------------------
# 1. 사진 3장 통합 분석
# ---------------------------------------------------------
st.markdown("### 1. 현장 사진 촬영 (전체/근접/병반 3장)")
uploaded_files = st.file_uploader("사진 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        images = [Image.open(f) for f in uploaded_files]
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[*images, "수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."]
        )
        st.session_state.ai_res = response.text
        st.success(f"👉 AI 분석: {response.text}")

# 2. GPS 위치 자동 특정 (Reverse Geocoding 예시)
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
col1, col2 = st.columns([4, 1])

with col1:
    # GPS 정보를 불러오는 컴포넌트 호출
    loc_data = streamlit_geolocation()
    # 기본값 설정
    address_display = "현재 위치를 불러오는 중..."
    
    if loc_data and 'latitude' in loc_data:
        # 실제 환경에서는 여기서 위도/경도를 주소로 변환하는 API 호출 필요
        address_display = f"경기도 광명시 하안동 산 123-4 (GPS 좌표: {loc_data['latitude']:.4f}, {loc_data['longitude']:.4f})"
    
    addr_input = st.text_input("현장 주소", value=address_display)

with col2:
    st.write(" ") # 레이아웃 정렬용
    st.write(" ")
    st.button("📍 위치 재검색")

# 3. 추가 관찰 소견
st.markdown("### 3. 전문가 추가 관찰 소견")
soil = st.multiselect("토양 상태", ["복토(심식)", "답압", "배수 불량", "복토 가해 흔적"])
memo = st.text_area("전문가 종합 메모", "예: 수관 상단부 변색 및 수피 송진 유출 관찰됨.")

# 4. 결과 출력
if st.button("📄 기술의견서 발행"):
    st.success("의견서가 생성되었습니다! 아래 PDF 발행 버튼을 누르세요.")
    # (이후 처방전 HTML 렌더링 영역)
