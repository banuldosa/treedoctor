import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

st.set_page_config(page_title="스마트 나무의사", page_icon="🌲")

# 1. 세션 상태 초기화
if 'step' not in st.session_state: st.session_state.step = 0
if 'form_data' not in st.session_state: st.session_state.form_data = {}

# ---------------------------------------------------------
# [0단계] 사진 촬영 및 AI 동정
# ---------------------------------------------------------
if st.session_state.step == 0:
    st.title("🌲 0단계: 사진으로 진단 시작")
    uploaded_file = st.file_uploader("현장 사진 업로드", type=["jpg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        cropped_img = st_cropper(img, realtime_update=False, box_color='#FF3333')
        if st.button("AI 분석 및 현장 입력으로 이동"):
            # AI 동정 결과 시뮬레이션
            st.session_state.form_data['tree'] = "잣나무 (Pinus koraiensis)"
            st.session_state.form_data['disease'] = "잣나무 털녹병"
            st.session_state.step = 1
            st.rerun()

# ---------------------------------------------------------
# [1단계] 현장 입력 (데이터 자동 매핑)
# ---------------------------------------------------------
elif st.session_state.step == 1:
    st.title("🩺 1단계: 현장 입력")
    st.info(f"AI 동정 결과: {st.session_state.form_data['tree']} / {st.session_state.form_data['disease']}")
    
    st.write("2. 수종: " + st.session_state.form_data['tree'])
    st.session_state.form_data['loc'] = st.text_input("3. 조사 위치", "경기도 광명시 하안동 OOO아파트")
    
    st.markdown("**4. 전문가 관찰 소견**")
    st.session_state.form_data['soil'] = st.multiselect("토양 상태", ["복토/심식", "답압", "배수불량"], default=["복토/심식", "배수불량"])
    st.session_state.form_data['memo'] = st.text_area("현장 메모", "수간 하부 송진 유출 흔적, 인근 확산 우려.")
    
    if st.button("🚀 다음: 진단 결과 및 처방 확인"):
        st.session_state.step = 2
        st.rerun()

# ---------------------------------------------------------
# [2단계] 최종 결과 및 PDF 발행 (이대표님 디자인)
# ---------------------------------------------------------
elif st.session_state.step == 2:
    st.title("🩺 2단계: 최종 처방 결과")
    st.components.v1.html(f"""
    <div style="padding:25px; border:2px solid #2E7D32; border-radius:12px; font-family:'Malgun Gothic', sans-serif; background:#FAFAFA; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
        <h3 style="text-align:center; color:#2E7D32;">🩺 스마트 나무의사 - 진단 및 처방 결과</h3>
        <h4 style="color:#1B5E20;">■ AI 진단 결과</h4>
        <div style="background:#E8F5E9; padding:10px; text-align:center; font-weight:bold; border-radius:6px; color:#2E7D32;">
            [★ 1순위] {st.session_state.form_data['disease']} (신뢰도 92%)
        </div>
        <h4 style="color:#1B5E20; margin-top:20px;">■ 산림청 PLS 등록 약제 목록 (2026년 기준)</h4>
        <table style="width:100%; border-collapse:collapse; font-size:13px; text-align:center;">
            <tr style="background:#4CAF50; color:white;"><th>성분명</th><th>상품명</th><th>희석배수</th></tr>
            <tr><td style="border:1px solid #ddd;">테부코나졸</td><td style="border:1px solid #ddd;">푸르지오</td><td style="border:1px solid #ddd;">20L/10ml</td></tr>
        </table>
        <h4 style="color:#1B5E20; margin-top:20px;">■ 전문가 처방 코멘트</h4>
        <p style="font-size:13px;">{st.session_state.form_data['memo']}</p>
        <button onclick="window.print()" style="width:100%; padding:12px; background:#2E7D32; color:white; border:none; border-radius:6px; font-weight:bold;">
            📄 최종 단계: 기술의견서 PDF 발행하기 ➡️
        </button>
    </div>
    """, height=500)
    
    if st.button("⬅️ 처음으로 돌아가기"):
        st.session_state.step = 0
        st.rerun()
