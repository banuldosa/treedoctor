import streamlit as st
from PIL import Image

st.set_page_config(page_title="스마트 나무의사 - 진단 및 처방", page_icon="🌲")

# 1. 2단계 처방 화면 UI 로직
def show_diagnosis_screen():
    # 이 부분은 실제로는 AI가 1단계 데이터를 받아 생성한 결과물입니다.
    st.components.v1.html("""
    <div style="padding:25px; border:2px solid #2E7D32; border-radius:12px; font-family:'Malgun Gothic', sans-serif; background-color:#FAFAFA; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
        <h3 style="text-align:center; color:#2E7D32;">🩺 스마트 나무의사 - 진단 및 처방 결과</h3>
        
        <h4 style="color:#1B5E20; border-bottom: 2px solid #2E7D32; padding-bottom:5px;">■ AI 진단 결과</h4>
        <div style="background:#E8F5E9; padding:12px; text-align:center; font-weight:bold; border-radius:6px; color:#2E7D32; margin-bottom:20px;">
            [★ 1순위] 잣나무 털녹병 (신뢰도 92%)
        </div>

        <h4 style="color:#1B5E20; border-bottom: 2px solid #2E7D32; padding-bottom:5px;">■ 산림청 PLS 등록 약제 목록 (2026년 기준)</h4>
        <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:center; margin-bottom:20px;">
            <tr style="background:#4CAF50; color:white;">
                <th style="padding:8px;">성분명</th><th>상품명</th><th>희석배수</th><th>살포시기</th>
            </tr>
            <tr>
                <td style="padding:8px; border:1px solid #ddd;">테부코나졸</td><td style="padding:8px; border:1px solid #ddd;">푸르지오</td>
                <td style="padding:8px; border:1px solid #ddd;">20L/10ml</td><td style="padding:8px; border:1px solid #ddd; color:red;">발병초기</td>
            </tr>
            <tr>
                <td style="padding:8px; border:1px solid #ddd;">디페노코나졸</td><td style="padding:8px; border:1px solid #ddd;">안심케어</td>
                <td style="padding:8px; border:1px solid #ddd;">20L/20g</td><td style="padding:8px; border:1px solid #ddd; color:red;">10일간격</td>
            </tr>
        </table>

        <h4 style="color:#1B5E20; border-bottom: 2px solid #2E7D32; padding-bottom:5px;">■ 전문가 처방 코멘트</h4>
        <ul style="font-size:13px; color:#444; padding-left:20px;">
            <li>광명시 하안동 현장은 배수불량 및 복토 상태가 관찰됩니다.</li>
            <li>약제 살포 전 복토 제거(환토) 및 배수로 정비를 강력히 권장합니다.</li>
            <li>감염 수간의 우드칩 처리를 금지하고 즉시 격리 소각하십시오.</li>
        </ul>

        <button onclick="window.print()" style="width:100%; padding:14px; background-color:#2E7D32; color:white; border:none; border-radius:6px; font-size:15px; font-weight:bold; cursor:pointer;">
            📄 최종 단계: 기술의견서 PDF 발행하기 ➡️
        </button>
    </div>
    """, height=560)

# 2. 실행 흐름 제어
show_diagnosis_screen()

if st.button("⬅️ 다시 진단하기"):
    st.rerun()
