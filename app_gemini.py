import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정
st.set_page_config(page_title="스마트 나무의사", layout="centered", page_icon="🌲")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# 2. API 설정
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. 사진 촬영 및 AI 동정
st.markdown("### 1. 수목 피해 사진 등록")
uploaded_files = st.file_uploader("피해 사진을 업로드하세요.", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("모델 및 이미지 분석 중..."):
            try:
                # 사용 가능한 모델 목록 확인 (404 에러 디버깅용)
                # 모델 이름이 'gemini-1.5-flash'인지 'models/gemini-1.5-flash'인지 확인
                available_models = [m.name for m in client.models.list()]
                st.write(f"디버그: 확인된 모델 목록 {available_models}")
                
                # 'gemini-1.5-flash'를 포함하는 가장 가까운 모델 ID 찾기
                target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), 'gemini-1.5-flash')

                parts = []
                for f in uploaded_files:
                    img = Image.open(f)
                    img.thumbnail((512, 512))
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                parts.append(types.Part.from_text(text="수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                
                # 자동 선택된 모델 ID 사용
                response = client.models.generate_content(
                    model=target_model, 
                    contents=parts
                )
                
                st.session_state.ai_result = response.text
                st.success(f"✅ 분석 완료: {st.session_state.ai_result}")
            except Exception as e:
                st.error(f"분석 오류 발생: {e}")
                st.info("💡 에러 상세 내용을 캡처해서 저에게 알려주시면 모델명을 바로 고정해 드리겠습니다.")

# (이후 GPS 및 소견 입력 등 나머지 코드는 동일)
