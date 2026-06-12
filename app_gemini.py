import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 및 API 설정
st.set_page_config(page_title="스마트 나무의사", layout="centered")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 2. [사진 촬영 및 AI 동정]
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("이미지 최적화 및 모델 연결 중..."):
            try:
                # 1. 사용 가능한 모델 검색 (404 에러 원천 차단)
                available_models = [m.name for m in client.models.list(model_type="generateContent")]
                # gemini-1.5-flash가 있으면 쓰고, 없으면 리스트의 첫 번째 모델 사용
                model_name = 'gemini-1.5-flash' if 'gemini-1.5-flash' in available_models else available_models[0]
                
                parts = []
                for f in uploaded_files:
                    img = Image.open(f)
                    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                    img.thumbnail((512, 512))
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                parts.append(types.Part.from_text(text="이 사진들의 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                
                # 2. 확인된 모델명으로 호출
                response = client.models.generate_content(
                    model=model_name,
                    contents=types.Content(role="user", parts=parts)
                )
                
                st.session_state.ai_result = response.text
                st.success(f"👉 AI 분석 완료 ({model_name}): {st.session_state.ai_result}")
            except Exception as e:
                st.error(f"분석 오류: {e}")
                st.write("서버가 지원하는 모델 목록:", available_models)

st.markdown("---")
# ... (GPS 및 소견 입력은 이전과 동일)
