import streamlit as st
from PIL import Image

st.set_page_config(page_title="스마트 나무의사 - 현장 입력", page_icon="🌲", layout="centered")

# CSS 스타일링으로 현장 업무용 UI의 가독성을 높였습니다.
st.markdown("""
    <style>
        .section-header { font-size: 16px; font-weight: bold; color: #1B5E20; margin-top: 25px; border-bottom: 1px solid #C8E6C9; padding-bottom: 5px; }
        .ai-result { background-color: #E8F5E9; padding: 15px; border-radius: 8px; border: 1px solid #A5D6A7; }
    </style>
""", unsafe_allow_html=True)

st.title("🌲 스마트 나무의사 - 현장 입력")

# 1. 수목 피해 사진 등록 및 AI 동정
st.markdown('<div class="section-header">1. 수목 피해 사진 등록 (필수)</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("📸 현장 사진 촬영 / 파일 선택", type=["jpg", "png"])

if uploaded_file:
    st.image(uploaded_file, use_container_width=True)
    st.markdown('<div class="ai-result"><strong>👉 AI 동정 결과:</strong> [잣나무]가 98% 확률로 매칭되었습니다.</div>', unsafe_allow_html=True)
    
    # 오동정 대비 수종 선택 메뉴
    tree_list = ["잣나무 (Pinus koraiensis)", "소나무 (Pinus densiflora)", "해송 (Pinus thunbergii)", "스트로브잣나무"]
    selected_tree = st.selectbox("수종 선택/수정", tree_list, index=0)

# 2. GPS 기반 위치 자동 특정
st.markdown('<div class="section-header">2. 조사 위치 (GPS 자동 특정)</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([4, 1])
with col_a:
    location = st.text_input("현장 주소", "경기도 광명시 하안동 OOO아파트 단지 내")
with col_b:
    st.write(" ") # 간격 조정
    st.write(" ")
    if st.button("🗺️ 재검색"):
        st.toast("현재 위치 기반 주소를 다시 불러옵니다.")

# 3. 전문가 추가 관찰 소견
st.markdown('<div class="section-header">3. 전문가 추가 관찰 소견 (선택)</div>', unsafe_allow_html=True)

col_soil, col_eco = st.columns(2)
with col_soil:
    st.write("**토양 및 식재**")
    st.checkbox("복토(심식)")
    st.checkbox("딛고 다져짐(답압)")
    st.checkbox("배수 불량")
with col_eco:
    st.write("**주변 생태**")
    st.checkbox("주변 공사 진행")
    st.checkbox("인근 수목 동시 발병")
    st.checkbox("가뭄/폭우 피해")

st.write("**전문가 종합 메모**")
memo = st.text_area("예: 수관 상단부 초두부부터 잎이 변색하기 시작함, 수피에 유출된 송진 흔적 관찰됨.", height=100)

# 4. 다음 단계 진행
st.markdown("---")
if st.button("🚀 다음: AI 진단 및 PLS 처방 보기 ➡️", type="primary", use_container_width=True):
    # 이 버튼을 누르면 처방전 결과 페이지로 데이터가 넘어갑니다.
    st.success("데이터가 성공적으로 수집되었습니다. 진단 화면으로 이동합니다.")
