import streamlit as st
from google import genai
from PIL import Image

# Google Gemini API 설정
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="스마트 나무의사 - 현장 입력", layout="centered")
st.title("🌲 스마트 나무의사 (3장 통합 분석)")

# 1. 3장 동시 사진 업로드
st.markdown("### 1. 현장 사진 촬영 (전체/근접/병반 3장 필수)")
uploaded_files = st.file_uploader("현장 사진 3장을 선택하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    if len(uploaded_files) > 3:
        st.warning("⚠️ 3장까지만 분석 가능합니다. 사진을 다시 선택해주세요.")
    else:
        # 사진 미리보기
        cols = st.columns(len(uploaded_files))
        for i, file in enumerate(uploaded_files):
            cols[i].image(file, use_container_width=True)
        
        if st.button("🚀 3장 통합 AI 분석 시작"):
            with st.spinner("🔍 AI가 사진 3장을 종합 분석 중입니다..."):
                # 3장의 이미지를 리스트로 생성
                images = [Image.open(f) for f in uploaded_files]
                
                # 프롬프트: 3장의 맥락을 설명
                prompt = (
                    "이 3장의 사진은 동일한 나무의 현장 사진입니다. "
                    "첫 번째는 수형, 두 번째는 잎/수피, 세 번째는 병반의 근접 샷입니다. "
                    "이 데이터를 종합하여 정확한 수종과 질병명을 한국어로 답해줘. "
                    "결과값만 '수종: OOO, 병명: OOO' 형식으로 출력해."
                )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[*images, prompt]
                )
                
                # 결과 저장 및 표시
                st.session_state.ai_analysis = response.text
                st.success(f"👉 AI 통합 분석 결과: {response.text}")

# 2. 동정 결과 자동 매핑 및 입력 폼 (이후 단계 동일)
st.markdown("### 2. AI 수종 동정 결과")
default_val = st.session_state.get('ai_analysis', "분석 전")
st.selectbox("🎯 AI 분석 결과 (*수정 가능)", [default_val, "잣나무", "소나무"], index=0)

# (이후 위치/소견 입력 폼은 이전과 동일하게 유지)
