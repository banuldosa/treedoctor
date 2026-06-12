import streamlit as st
from google import genai
from PIL import Image
from streamlit_cropper import st_cropper

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
                    
                    st.markdown("---")
                    st.markdown("### 📄 의뢰인 전송용 결과물 출력")
                    
                    # 🌟 [혁신적 해결책] 외부 PDF 라이브러리를 쓰지 않고, 
                    # 브라우저 친화적인 HTML 서식으로 진단서를 빌드하여 출력 버그를 원천 차단합니다.
                    html_content = diagnosis_result.replace('\n', '<br>')
                    
                    # 모바일 및 PC에서 즉시 인쇄/PDF 저장이 가능한 컴포넌트 이식
                    st.components.v1.html(f"""
                        <div id="print-area" style="padding:20px; border:1px solid #ddd; border-radius:8px; font-family:sans-serif; background-color:#fff; color:#333; line-height:1.6;">
                            <h2 style="text-align:center; color:#2E7D32;">[AI 수목 진단 및 처방서]</h2>
                            <hr style="border:1px solid #2E7D32;">
                            <p style="font-size:14px;">{html_content}</p>
                        </div>
                        <br>
                        <button onclick="window.print()" style="width:100%; padding:12px; background-color:#2E7D32; color:white; border:none; border-radius:5px; font-size:16px; font-weight:bold; cursor:pointer;">
                            🖨️ 진단서 인쇄 및 PDF 저장하기
                        </button>
                    """, height=400, scrolling=True)
                    
                    st.info("💡 **인쇄 및 PDF 저장 방법**: 위의 초록색 버튼을 누르면 인쇄 창이 뜹니다. 대상 지정을 **'PDF로 저장'**으로 선택하시면 깨끗한 한글 PDF 파일이 생성되며, 이를 카카오톡으로 의뢰인에게 바로 전송할 수 있습니다!")
                    
                else:
                    st.error("No text response generated.")
                
            except Exception as e:
                st.error(f"⚠️ Connection Error: {str(e)}")
