import streamlit as st

# [1단계] 설정: 페이지 구성 및 세션 데이터 초기화
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# 세션 상태 초기화 (데이터 유지)
if 'step' not in st.session_state: st.session_state.step = 1

# [2단계] UI 레이아웃
st.markdown("---")
st.write("### 현장 데이터 수집 시작")

# 향후 추가될 기능들의 자리
if st.button("시스템 초기화 및 테스트"):
    st.write("시스템이 정상 작동 중입니다.")

# 다음 단계 진행을 위한 확인
if st.button("기능 1: 사진 동정 모듈 준비"):
    st.session_state.step = 2
    st.rerun()
