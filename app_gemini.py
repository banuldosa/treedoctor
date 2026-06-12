import streamlit as st
from google import genai
from PIL import Image
from streamlit_cropper import st_cropper
from fpdf import FPDF
import io

# 1. UI 및 레이아웃 설정
st.set_page_config(page_title="Gemini AI Tree Doctor", page_icon="🌲")
st.title("🌲 AI Tree Doctor (MVP)")
st.markdown("### 📷 Upload a photo and crop the infected area for precise diagnosis.")

# 2. Secrets로부터 API Key 로드 및 정제
raw_api_key = st.secrets.get("GEMINI_API_KEY", "")
GOOGLE_API_KEY = raw_api_key.strip() if raw_api_key else ""

if not GOOGLE_API_KEY:
    st.error("⚠️ API Key가 설정되지 않았습니다. Streamlit Advanced settings를 확인해주세요.")
else:
    # 3. 통합 이미지 업로더 가동
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

            prompt_text = (
                "You are a strict and highly accurate Tree Doctor AI certified by the Korea Forest Service. "
                "Analyze the provided close-up/cropped image of the tree disease or pest very carefully. "
                "Think step-by-step like a human expert taking the Tree Doctor practical exam. "
                "Examine microscopic structures shown in this cropped area: color/shape of fruiting bodies, fungal mycelium, rust spores, or insect frass.\n\n"
                
                "CRITICAL ORDER 1: You must write the entire response in Korean.\n"
                "CRITICAL ORDER 2: You MUST start your very first sentence exactly as:\n"
                "'안녕하십니까, AI 나무의사입니다. 제공해주신 소나무 질병 이미지와 세부 확대 이미지를 정밀하게 분석한 결과, 다음과 같이 진단하고 방제 계획을 수립합니다.'\n\n"
                
                "Format the rest of the output strictly in Markdown with the following 4 sections:\n\n"
                "1. [정확한 진단명]: Provide the exact common Korean name and scientific name of the disease/pest.\n"
                "2. [수목보호학적 진단 근거]: Detail the specific visual symptoms and signs shown in the cropped photo supporting your diagnosis.\n"
                "3. [산림청 기준 방제법]: Suggest exact approved chemical pesticide names in Korea and mechanical/cultural control methods.\n"
                "4. [수목 관리 주의사항]: Precautions for chemical toxicity, environment factors, and preventing recurrence."
            )
            
            try:
                client = genai.Client(api_key=GOOGLE_API_KEY)
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[cropped_img, prompt_text]
                )
                
                st.markdown("---")
                st.markdown("### 📋 AI Tree Doctor Diagnosis")
                
                if response.text:
                    diagnosis_result = response.text
                    st.markdown(diagnosis_result)
                    
                    # 🌟 [안전화 적용] 다운로드 스트레스가 없는 내장 표준 폰트 엔진 가동
                    pdf = FPDF()
                    pdf.add_page()
                    
                    # 외부 주소 대신 내장 폰트(Courier)를 지정하여 TTF 파일 누락 에러를 완벽하게 차단합니다.
                    pdf.set_font("Courier", size=11)
                    
                    # PDF 타이틀 작성
                    pdf.cell(200, 10, txt="[AI Tree Doctor Report]", ln=True, align='C')
                    pdf.ln(10)
                    
                    # 텍스트 라인 바인딩
                    for line in diagnosis_result.split('\n'):
                        clean_line = line.replace('**', '').replace('#', '').strip()
                        if clean_line:
                            # 영문 보고서 서식 안정성을 위해 latin-1 인코딩 유연화 처리
                            pdf.multi_cell(0, 8, txt=clean_line.encode('utf-8', 'ignore').decode('latin-1'))
                    
                    # 바이트 데이터 변환
                    pdf_output = io.BytesIO()
                    pdf.output(pdf_output)
                    pdf_bytes = pdf_output.getvalue()
                    
                    st.markdown("---")
                    st.markdown("### 📄 의뢰인 전송용 결과물 출력")
                    
                    # 스마트폰 공용 PDF 다운로드 버튼
                    st.download_button(
                        label="📥 수목 처방전 PDF 다운로드",
                        data=pdf_bytes,
                        file_name="AI_Tree_Doctor_Report.pdf",
                        mime="application/pdf"
                    )
                    
                    st.info("💡 **카카오톡 공유 팁**: 위 PDF 다운로드 버튼을 눌러 스마트폰에 저장하신 후, 카카오톡 창에서 [파일 보내기]를 선택하시면 의뢰인이나 동료에게 처방전을 즉시 공유할 수 있습니다.")
                    
                else:
                    st.error("No text response generated.")
                
            except Exception as e:
                st.error(f"⚠️ Connection Error: {str(e)}")
