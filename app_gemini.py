import streamlit as st
from PIL import Image

# 1. 웹앱 전체 헤더 및 테마 설정
st.set_page_config(page_title="스마트 나무의사 - 현장 입력", page_icon="🌲", layout="centered")

# 카카오톡/모바일 최적화를 위한 부드러운 초록색 스타일 입히기
st.markdown("""
    <style>
        .main-title { font-size: 20px; font-weight: bold; color: #2E7D32; text-align: center; padding: 10px; border-bottom: 2px solid #2E7D32; margin-bottom: 20px; }
        .section-header { font-size: 15px; font-weight: bold; color: #1B5E20; margin-top: 15px; margin-bottom: 5px; }
        .info-box { background-color: #F1F8E9; border-left: 4px solid #7CB342; padding: 10px; border-radius: 4px; font-size: 13px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# [ 🌲 스마트 나무의사 - 현장 입력 ] Title
st.markdown('<div class="main-title">🩺 스마트 나무의사 - 현장 입력</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 1. 수목 피해 사진 등록
# -------------------------------------------------------------------------
st.markdown('<div class="section-header">1. 수목 피해 사진 등록 (필수)</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("📸 스마트폰 카메라 촬영 또는 파일 선택", type=["jpg", "jpeg", "png"])

# 시연용 기본 상태 혹은 파일 업로드 완료 상태 표시
if uploaded_file is not None:
    st.markdown(f'<div class="info-box">👉 {uploaded_file.name} 등록 완료!</div>', unsafe_allow_html=True)
    # 업로드한 사진 미리보기 화면 분출
    img = Image.open(uploaded_file)
    st.image(img, caption="현장 등록 사진", use_container_width=True)
else:
    st.markdown('<div class="info-box">👉 사진을 등록해 주세요. (테스트 시: 잣나무털녹병.jpg)</div>', unsafe_allow_html=True)


# -------------------------------------------------------------------------
# 2. AI 수종 동정 결과
# -------------------------------------------------------------------------
st.markdown('<div class="section-header">2. AI 수종 동정 결과 (자동 입력됨)</div>', unsafe_allow_html=True)
# 대표 수종 목록을 드롭다운박스로 제공하여, 틀렸을 때 사용자가 직접 누르고 바꿀 수 있게 유도
tree_options = ["잣나무 (Pinus koraiensis)", "소나무 (Pinus densiflora)", "해송 (Pinus thunbergii)", "스트로브잣나무 (Pinus strobus)", "직접 입력"]
selected_tree = st.selectbox("🎯 95% 일치 (*틀렸다면 눌러서 직접 변경 가능)", tree_options, index=0)


# -------------------------------------------------------------------------
# 3. 조사 위치
# -------------------------------------------------------------------------
st.markdown('<div class="section-header">3. 조사 위치 (GPS 자동 특정)</div>', unsafe_allow_html=True)
location_input = st.text_input("📍 현장 주소", value="경기도 광명시 하안동 OOO아파트 단지 내")
col1, col2 = st.columns([3, 1])
with col2:
    st.button("🗺️ 위치 재검색", use_container_width=True)


# -------------------------------------------------------------------------
# 4. 전문가 추가 관찰 소견
# -------------------------------------------------------------------------
st.markdown('<div class="section-header">4. 전문가 추가 관찰 소견 (선택)</div>', unsafe_allow_html=True)

st.markdown("**▪ 토양 상태 (중복 체크 가능)**")
# 사용자가 한눈에 체크할 수 있도록 가로 배치 레이아웃 구성
chk_col1, chk_col2, chk_col3 = st.columns(3)
with chk_col1:
    soil_1 = st.checkbox("복토/심식", value=True)  # 기본 체크 상태 활성화
with chk_col2:
    soil_2 = st.checkbox("답압", value=False)
with chk_col3:
    soil_3 = st.checkbox("배수불량", value=True)  # 기본 체크 상태 활성화

st.markdown("**▪ 현장 메모**")
default_memo = "수간 하부에서 약간의 송진 유출 흔적이 관찰되며, 인근 잣나무로의 전염 확산이 우려되는 상황임."
user_memo = st.text_area("현장 특이사항 직접 입력", value=default_memo, height=100)


# -------------------------------------------------------------------------
# 하단 진행 버튼
# -------------------------------------------------------------------------
st.markdown("---")
if st.button("🚀 다음: AI 진단 및 PLS 처방 보기 ➡️", type="primary", use_container_width=True):
    st.success("✅ 1단계 현장 데이터 수집 완료! 2단계 진단서 매핑 단계로 이동합니다.")
