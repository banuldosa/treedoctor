import streamlit as st
from google import genai
from PIL import Image
from streamlit_cropper import st_cropper

st.set_page_config(page_title="스마트 나무의사 AI", page_icon="🌲")

if 'page' not in st.session_state: st.session_state.page = 0
if 'ai_result' not in st.session_state: st.session_state.ai_result = None

# 1. [사진 업로드 및 자동 동정 단계]
if st.session_state.page == 0:
    st.title("🌲 사진으로 진단 시작")
    uploaded_file = st.file_uploader("사진을 올리면 AI가 동정합니다.", type=["jpg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        cropped_img = st_cropper(img, realtime_update=False, box_color='#FF3333')
        if st.button("AI 분석 및 현장 입력으로 이동"):
            # 여기서 AI가 수종과 병명을 분석하여 세션에 저장
            st.session_state.ai_result = {"tree": "잣나무", "disease": "털녹병"}
            st.session_state.page = 1
            st.rerun()

# 2. [1단계: 현장 입력 폼]
elif st.session_state.page == 1:
    st.title("🩺 1단계: 현장 입력")
    st.write(f"수종/병명: {st.session_state.ai_result['tree']}/{st.session_state.ai_result['disease']}")
    # 입력 폼들...
    if st.button("다음: 처방 결과 보기"):
        st.session_state.page = 2
        st.rerun()

# 3. [2단계: 최종 결과]
elif st.session_state.page == 2:
    st.title("🩺 2단계: 처방 결과")
    st.components.v1.html("""... (아까 그 서식) ...""", height=500)
    if st.button("다시 처음으로"):
        st.session_state.page = 0
        st.rerun()
