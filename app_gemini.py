import streamlit as st
from google import genai
from PIL import Image

# Google Gemini API 설정
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="스마트 나무의사 - 현장 입력", layout="centered")

st.title("🌲 스마트 나무의사 - 현장 입력")

# 1. 사진 촬영 및 AI 수종 동정
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_file = st.file_uploader("📸 현장 사진 촬영 / 파일 선택", type=["jpg", "png"])

# 초기값 설정
detected_tree = "잣나무 (Pinus koraiensis)" # 기본값

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, use_container_width=True)
    
    with st.spinner("🔍 AI가 사진을 정밀 분석 중입니다..."):
        # Gemini Vision AI에게 수종 및 질병 분석 요청
        prompt = "이 나무의 수종과 보이는 병징(질병명)을 한국어로 짧게 답해줘. 결과값만 '수종:OOO, 병명:OOO' 형식으로 줘."
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img, prompt]
        )
        # AI 결과 파싱 (간단 예시)
        st.success(f"👉 AI 분석 완료: {response.text}")
        detected_tree = response.text.split("수종:")[1].split(",")[0].strip()

# 2. AI 동정 결과 (자동 매핑)
st.markdown("### 2. AI 수종 동정 결과")
tree_list = [detected_tree, "잣나무", "소나무", "해송", "스트로브잣나무"]
selected_tree = st.selectbox("🎯 AI가 동정한 결과 (*수정 가능)", tree_list, index=0)

# (이하 기존 GPS 및 소견 입력란은 동일하게 유지)
# ...
