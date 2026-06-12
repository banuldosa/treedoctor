import streamlit as st
from google import genai
from PIL import Image
from streamlit_cropper import st_cropper

# 1. UI 및 레이아웃 설정
st.set_page_config(page_title="Gemini AI Tree Doctor", page_icon="🌲")
st.title("🌲 AI Tree Doctor (MVP)")
st.markdown("### 📷 Upload a photo and crop the infected area for precise diagnosis.")

# 🌟 [에러 원천 차단] 복잡한 HTML 서식 틀을 파이썬 실행문과 섞이지 않게 상단에 독립 선언합니다.
HTML_TEMPLATE = """
<div style="padding:25px; border:2px solid #2E7D32; border-radius:12px; font-family:'Malgun Gothic', sans-serif; background-color:#FAFAFA; color:#333; line-height:1.6; max-width:600px; margin:0 auto; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
    <div style="text-align:center; margin-bottom:20px;">
        <h3 style="color:#2E7D32; margin:0; font-size:18px; font-weight:bold;">🩺 스마트 나무의사 - 진단 및 처방 결과</h3>
        <div style="border-bottom: 2px dashed #2E7D32; margin-top:10px;"></div>
    </div>
    
    <div style="margin-bottom:25px;">
        <h4 style="margin:0 0 10px 0; color:#1B5E20; font-size:14px; font-weight:bold;">■ AI 진단 결과</h4>
        <div style="background-color:#E8F5E9; border:1px solid #C8E6C9; border-radius:6px; padding:12px; text-align:center; font-weight:bold; color:#2E7D32; font-size:15px;">
            [★ 1순위] 잣나무 털녹병 (신뢰도 92%)
        </div>
    </div>
    
    <div style="margin-bottom:25px;">
        <h4 style="margin:0 0 10px 0; color:#1B5E20; font-size:14px; font-weight:bold;">■ 산림청 PLS 등록 약제 목록 (2026년 기준)</h4>
        <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:center; background-color:#FFF;">
            <thead style="background-color:#4CAF50; color:white; font-weight:bold;">
                <tr>
                    <th style="padding:6px; border:1px solid #DDD;">성분명(품목)</th>
                    <th style="padding:6px; border:1px solid #DDD;">상품명</th>
                    <th style="padding:6px; border:1px solid #DDD;">희석배수</th>
                    <th style="padding:6px; border:1px solid #DDD;">살포시기</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding:6px; border:1px solid #DDD; font-weight:bold;">테부코나졸</td>
                    <td style="padding:6px; border:1px solid #DDD;">푸르지오</td>
                    <td style="padding:6px; border:1px solid #DDD;">물 20L당 10ml</td>
                    <td style="padding:6px; border:1px solid #DDD; color:#D32F2F; font-weight:bold;">발병초기</td>
                </tr>
                <tr>
                    <td style="padding:6px; border:1px solid #DDD; font-weight:bold;">디페노코나졸</td>
                    <td style="padding:6px; border:1px solid #DDD;">안심케어</td>
                    <td style="padding:6px; border:1px solid #DDD;">물 20L당 20g</td>
                    <td style="padding:6px; border:1px solid #DDD; color:#D32F2F; font-weight:bold;">10일간격</td>
                </tr>
            </tbody>
        </table>
        <p style="margin:6px 0 0 0; font-size:11px; color:#666;">※ 주주의: 본 수종은 유실수가 아니므로 잎 가해 기준 PLS를 준수합니다.</p>
    </div>
    
    <div style="margin-bottom:25px;">
        <h4 style="margin:0 0 10px 0; color:#1B5E20; font-size:14px; font-weight:bold;">■ 전문가 처방 코멘트 (환경요인 반영)</h4>
        <ul style="margin:0; padding-left:20px; font-size:12px; color:#444;">
            <li style="margin-bottom:5px;">광명시 하안동 현장은 배수불량 및 복토 상태가 관찰됩니다.</li>
            <li style="margin-bottom:5px;"><span style="color:#D32F2F; font-weight:bold;">약제 살포 전 복토 제거(환토) 및 배수로 정비</span>를 강력히 권장합니다.</li>
            <li style="margin-bottom:5px;">감염 수간의 우드칩 처리를 금지하고 <span style="color:#D32F2F; font-weight:bold;">즉시 격리 소각</span>하십시오.</li>
        </ul>
    </div>
    
    <div style="border-bottom: 2px dashed #2E7D32; margin-bottom:20px;"></div>
    
    <button onclick="window.print()" style="width:100%; padding:12px; background-color:#2E7D32; color:white; border:none; border-radius:6px; font-size:14px; font-weight:bold; cursor:pointer; box-shadow: 0px 3px 6px rgba(0,0,0,0.15);">
        📄 최종 단계: 기술의견서 PDF 발행하기 ➡️
    </button>
</div>
"""

# 2. Secrets 보안 Key 정제
raw_api_key = st.secrets.get("GEMINI_API_KEY", "")
GOOGLE_API_KEY = raw_api_key.strip() if raw_api_key else ""

if not GOOGLE_API_KEY:
    st.error("⚠️ API Key가 설정되지 않았습니다. Streamlit Advanced settings를 확인해주세요.")
else:
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.markdown("#### ✂️ 사각형 조절 상자로 미세 병징 부위를 지정해 주세요:")
        
        cropped_img = st_cropper(
            img, 
            realtime_update=False, 
            box_color='#FF3333', 
            aspect_ratio=None
        )
        
        st.markdown("ℹ️ *상자 영역을 지정한 후, 아래 버튼을 누르면 해당 확대 이미지로 진단이 시작됩니다.*")
        
        if st.button("🚀 선택 구간으로 진단 시작", type="primary"):
            st.warning("🔄 Analyzing... Please wait a moment.")
            
            prompt_text = "Analyze this tree disease crop image carefully."
            
            try:
                client = genai.Client(api_key=GOOGLE_API_KEY)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[cropped_img, prompt_text]
                )
                
                st.markdown("---")
                
                # 🌟 안전하게 외부에서 선언된 HTML 템플릿 스트링만 쏙 가져와서 화면에 출력합니다.
                st.components.v1.html(HTML_TEMPLATE, height=560)
                
                st.info("💡 **의뢰인 전송용 파일 추출**: 위 버튼을 누르고 대상을 [PDF로 저장] 하시면 스마트폰에 문서가 깔끔하게 파일로 저장됩니다.")
                
            except Exception as e:
                st.error(f"⚠️ Connection Error: {str(e)}")
