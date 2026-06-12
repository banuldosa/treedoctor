import streamlit as st
from PIL import Image

# 세션 상태(Session State)를 사용하여 1단계 데이터를 2단계로 전달합니다.
if 'page' not in st.session_state:
    st.session_state.page = 1

# [1단계 입력값 저장소]
if 'tree_data' not in st.session_state:
    st.session_state.tree_data = {}

def go_to_step2():
    st.session_state.page = 2

# 페이지 라우팅
if st.session_state.page == 1:
    st.title("🩺 스마트 나무의사 - 현장 입력")
    # ... (생략: 이전 단계 코드와 동일하게 유지) ...
    if st.button("🚀 다음: AI 진단 및 PLS 처방 보기 ➡️", type="primary"):
        go_to_step2()
        st.rerun()

elif st.session_state.page == 2:
    st.title("🩺 스마트 나무의사 - 진단 및 처방 결과")
    
    # 🌟 [핵심] 이대표님이 요청하신 바로 그 레이아웃 서식 적용
    st.components.v1.html(f"""
    <div style="padding:20px; border:2px solid #2E7D32; border-radius:10px; font-family:sans-serif; background-color:#FAFAFA;">
        <h4 style="color:#1B5E20;">■ AI 진단 결과</h4>
        <div style="background:#E8F5E9; padding:10px; text-align:center; font-weight:bold; border-radius:5px;">
            [★ 1순위] 잣나무 털녹병 (신뢰도 92%)
        </div>
        
        <h4 style="color:#1B5E20; margin-top:20px;">■ 산림청 PLS 등록 약제 목록 (2026년 기준)</h4>
        <table style="width:100%; border-collapse:collapse; font-size:12px;">
            <tr style="background:#4CAF50; color:white;">
                <th style="padding:5px;">성분명</th><th>상품명</th><th>희석배수</th><th>살포시기</th>
            </tr>
            <tr>
                <td style="border:1px solid #ddd; padding:5px;">테부코나졸</td><td style="border:1px solid #ddd; padding:5px;">푸르지오</td>
                <td style="border:1px solid #ddd; padding:5px;">20L/10ml</td><td style="border:1px solid #ddd; padding:5px;">발병초기</td>
            </tr>
        </table>
        <p style="font-size:11px; color:#666;">※ 본 수종은 잎 가해 기준 PLS를 준수함.</p>

        <h4 style="color:#1B5E20; margin-top:20px;">■ 전문가 처방 코멘트</h4>
        <ul style="font-size:13px;">
            <li>광명시 하안동 현장은 배수불량 및 복토 상태 관찰됨.</li>
            <li>약제 살포 전 복토 제거 및 배수로 정비 권장.</li>
        </ul>
        
        <button onclick="window.print()" style="width:100%; padding:10px; background:#2E7D32; color:white; border:none; border-radius:5px; font-weight:bold;">
            📄 최종 단계: 기술의견서 PDF 발행하기 ➡️
        </button>
    </div>
    """, height=500)
    
    if st.button("⬅️ 이전: 현장 입력 수정"):
        st.session_state.page = 1
        st.rerun()
