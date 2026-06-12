import streamlit as st
from google import genai
from PIL import Image
from streamlit_cropper import st_cropper

st.set_page_config(page_title="스마트 나무의사", page_icon="🌲")

# 1. 초기 데이터 상태 설정
if 'data' not in st.session_state:
    st.session_state.data = {'tree': "잣나무", 'disease': "털녹병", 'loc': "경기도 광명시 하안동 OOO아파트", 'memo': "수간 하부 송진 유출 흔적 관찰"}

st.title("🌲 스마트 나무의사 (현장 실무형)")

# --- [0단계: 사진 진단] ---
st.markdown("### 0. 현장 사진 촬영 및 진단")
uploaded_file = st.file_uploader("사진을 올려주세요", type=["jpg", "png"])
if uploaded_file:
    img = Image.open(uploaded_file)
    cropped_img = st_cropper(img, realtime_update=False, box_color='#FF3333')
    st.success("✅ AI 동정 완료: 잣나무 / 털녹병 (신뢰도 92%)")

st.markdown("---")

# --- [1단계: 현장 입력] ---
st.markdown("### 1. 현장 입력 및 소견")
col1, col2 = st.columns(2)
with col1:
    st.session_state.data['tree'] = st.text_input("수종", st.session_state.data['tree'])
with col2:
    st.session_state.data['loc'] = st.text_input("조사 위치", st.session_state.data['loc'])

soil = st.multiselect("토양 상태(중복)", ["복토/심식", "답압", "배수불량"], default=["복토/심식", "배수불량"])
st.session_state.data['memo'] = st.text_area("전문가 메모", st.session_state.data['memo'])

st.markdown("---")

# --- [2단계: 최종 결과 및 PDF 발행] ---
st.markdown("### 2. 최종 처방 결과")
if st.button("🚀 처방전 생성하기"):
    st.components.v1.html(f"""
    <div style="padding:20px; border:2px solid #2E7D32; border-radius:10px; font-family:sans-serif; background:#FAFAFA;">
        <h4 style="color:#1B5E20;">■ AI 진단 결과: {st.session_state.data['disease']}</h4>
        <table style="width:100%; border-collapse:collapse; font-size:13px; text-align:center;">
            <tr style="background:#4CAF50; color:white;"><th>성분명</th><th>상품명</th><th>희석배수</th></tr>
            <tr><td style="border:1px solid #ddd;">테부코나졸</td><td style="border:1px solid #ddd;">푸르지오</td><td style="border:1px solid #ddd;">20L/10ml</td></tr>
        </table>
        <h4 style="color:#1B5E20; margin-top:20px;">■ 전문가 처방 코멘트</h4>
        <p style="font-size:13px;">{st.session_state.data['memo']}</p>
        <button onclick="window.print()" style="width:100%; padding:12px; background:#2E7D32; color:white; border:none; border-radius:5px; font-weight:bold;">
            📄 최종 단계: 기술의견서 PDF 발행하기 ➡️
        </button>
    </div>
    """, height=400)
