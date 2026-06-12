import streamlit as st
from google import genai
from PIL import Image
from streamlit_cropper import st_cropper

st.set_page_config(page_title="스마트 나무의사", page_icon="🌲")

# 세션 상태 초기화
if 'step' not in st.session_state: st.session_state.step = 0

# ---------------------------------------------------------
# [단계 0] 사진 동정 및 초기 진단
# ---------------------------------------------------------
if st.session_state.step == 0:
    st.title("🌲 0단계: 사진으로 AI 진단 시작")
    uploaded_file = st.file_uploader("현장 사진 업로드", type=["jpg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        cropped_img = st_cropper(img, realtime_update=False, box_color='#FF3333')
        if st.button("AI 분석 및 현장 입력으로 이동"):
            st.session_state.step = 1
            st.rerun()

# ---------------------------------------------------------
# [단계 1] 현장 입력 (AI 결과 자동 매핑)
# ---------------------------------------------------------
elif st.session_state.step == 1:
    st.title("🩺 1단계: 현장 입력")
    st.info("AI 자동 동정: 잣나무 / 털녹병 (신뢰도 92%)")
    
    st.write("2. 수종: 잣나무 (Pinus koraiensis)")
    st.write("3. 조사 위치: 경기도 광명시 하안동 OOO아파트")
    
    st.markdown("**4. 전문가 관찰 소견**")
    soil = st.multiselect("토양 상태", ["복토/심식", "답압", "배수불량"], default=["복토/심식", "배수불량"])
    memo = st.text_area("현장 메모", "수간 하부 송진 유출 흔적, 인근 확산 우려.")
    
    if st.button("🚀 다음: 진단 결과 및 처방 확인"):
        st.session_state.step = 2
        st.rerun()

# ---------------------------------------------------------
# [단계 2] 최종 결과 및 PDF 발행
# ---------------------------------------------------------
elif st.session_state.step == 2:
    st.title("🩺 2단계: 최종 처방 결과")
    st.components.v1.html("""
    <div style="padding:20px; border:2px solid #2E7D32; border-radius:10px; font-family:sans-serif; background:#FAFAFA;">
        <h4 style="color:#1B5E20;">■ AI 진단 결과: 잣나무 털녹병</h4>
        <table style="width:100%; border-collapse:collapse; font-size:13px; text-align:center;">
            <tr style="background:#4CAF50; color:white;"><th>성분명</th><th>상품명</th><th>희석배수</th></tr>
            <tr><td style="border:1px solid #ddd;">테부코나졸</td><td style="border:1px solid #ddd;">푸르지오</td><td style="border:1px solid #ddd;">20L/10ml</td></tr>
        </table>
        <h4 style="color:#1B5E20;">■ 전문가 처방 코멘트</h4>
        <p style="font-size:13px;">복토 제거 및 배수로 정비 강력 권장, 감염 부위 격리 소각.</p>
        <button onclick="window.print()" style="width:100%; padding:10px; background:#2E7D32; color:white; border:none;">
            📄 기술의견서 PDF 발행하기 ➡️
        </button>
    </div>
    """, height=400)
    
    if st.button("⬅️ 처음으로 돌아가기"):
        st.session_state.step = 0
        st.rerun()
