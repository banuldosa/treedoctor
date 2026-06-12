import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

# 세션 상태 유지
if 'step' not in st.session_state: st.session_state.step = 0
if 'form' not in st.session_state: 
    st.session_state.form = {
        'tree': "잣나무 (Pinus koraiensis)",
        'loc': "경기도 광명시 하안동 OOO아파트 단지 내",
        'memo': "수간 하부에서 약간의 송진 유출 흔적이 관찰되며,\n인근 잣나무로의 전염 확산이 우려되는 상황임."
    }

st.title("🌲 스마트 나무의사 - 현장 입력")

# 1. 수목 피해 사진 등록
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_file = st.file_uploader("📸 스마트폰 카메라 촬영 / 파일 선택", type=["jpg", "png"])
if uploaded_file:
    st.image(uploaded_file, caption="등록된 피해 사진", use_container_width=True)
    st.success(f"👉 {uploaded_file.name} 등록 완료!")

# 2. AI 수종 동정 결과
st.markdown("### 2. AI 수종 동정 결과")
st.session_state.form['tree'] = st.selectbox(
    "🎯 95% 일치 (틀렸다면 직접 변경)", 
    ["잣나무 (Pinus koraiensis)", "소나무 (Pinus densiflora)", "해송 (Pinus thunbergii)"],
    index=0
)

# 3. 조사 위치 (GPS 자동 특정)
st.markdown("### 3. 조사 위치 (GPS 자동 특정)")
col1, col2 = st.columns([4, 1])
with col1:
    st.session_state.form['loc'] = st.text_input("위치 정보", st.session_state.form['loc'])
with col2:
    st.button("🗺️ 재검색")

# 4. 전문가 추가 관찰 소견
st.markdown("### 4. 전문가 추가 관찰 소견 (선택)")
soil_status = st.multiselect("토양 상태(중복 체크)", ["복토/심식", "답압", "배수불량"], default=["복토/심식", "배수불량"])
st.session_state.form['memo'] = st.text_area("현장 메모", st.session_state.form['memo'], height=100)

st.markdown("---")

# 2단계(처방 보기)로 넘어가는 버튼
if st.button("🚀 다음: AI 진단 및 PLS 처방 보기 ➡️", type="primary", use_container_width=True):
    st.session_state.step = 2
    st.rerun()
