import streamlit as st
import io
from google import genai
from google.genai import types
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# 1. 페이지 설정
st.set_page_config(page_title="스마트 나무의사", layout="centered", page_icon="🌲")
st.title("🌲 스마트 나무의사 - 현장 통합 시스템")

# 2. API 설정 (secrets.toml 관리)
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API 키 설정이 필요합니다. Streamlit Secrets 설정을 확인하세요.")
    st.stop()

# 3. [사진 촬영 및 AI 동정 (개수 무제한)]
st.markdown("### 1. 수목 피해 사진 등록")
# accept_multiple_files=True로 무제한 등록 가능
uploaded_files = st.file_uploader("피해 사진을 필요한 만큼 모두 업로드하세요 (개수 제한 없음)", 
                                type=["jpg", "jpeg", "png"], 
                                accept_multiple_files=True)

# 사진 미리보기 및 관리 (현장 확인용)
if uploaded_files:
    st.write(f"현재 **{len(uploaded_files)}장**의 사진이 로드되었습니다.")
    # 그리드 뷰 구성
    cols = st.columns(min(len(uploaded_files), 4)) # 최대 4열로 표시
    for i, file in enumerate(uploaded_files):
        try:
            img = Image.open(file)
            cols[i % 4].image(img, caption=file.name, use_container_width=True)
        except Exception as e:
            st.error(f"{file.name} 이미지를 로드하는 중 오류 발생: {e}")

# 분석 버튼 영역
if uploaded_files:
    if st.button("🚀 AI 종합 분석 시작"):
        with st.spinner(f"{len(uploaded_files)}장의 사진을 종합 분석 중입니다..."):
            try:
                parts = []
                for f in uploaded_files:
                    # [코드 최적화] 이미지 리사이징으로 무제한 사진 대응 (토큰 절약)
                    img = Image.open(f)
                    img.thumbnail((512, 512)) # 가로세로 512px 축소
                    
                    img_byte_arr = io.BytesIO()
                    # MIME 타입을 JPEG로 통일하여 전송 (속도 향상)
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                # 프롬프트 구성 (종합 분석 유도)
                prompt_text = f"업로드된 {len(uploaded_files)}장의 사진을 종합하여 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."
                parts.append(types.Part.from_text(text=prompt_text))
                
                # 모델 호출 (가장 안정적인 gemini-1.5-flash 사용)
                # 만약 404가 발생하면 'models/gemini-1.5-flash'로 변경
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=parts
                )
                
                st.session_state.ai_result = response.text
                st.success(f"👉 AI 분석 완료: {st.session_state.ai_result}")
            except Exception as e:
                st.error(f"분석 오류 발생: {e}")
                st.warning("⚠️ 사진 파일 형식이나 네트워크 상태를 확인해주세요.")

st.markdown("---")

# 4. [조사 위치 - GPS 자동 특정]
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
loc_data = streamlit_geolocation()
# 데이터 안전 처리
if loc_data:
    lat = loc_data.get('latitude')
    lon = loc_data.get('longitude')
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        # f-string formatting (.4f) 오류 방지
        addr = f"위도:{lat:.4f}, 경도:{lon:.4f}"
    else:
        addr = "위치 정보를 가져오지 못했습니다."
else:
    addr = "위치 정보를 가져오는 중입니다..."
    
st.text_input("현장 주소", value=addr)
st.button("📍 위치 재검색")

st.markdown("---")

# 5. [전문가 추가 관찰 소견]
st.markdown("### 3. 전문가 추가 관찰 소견")
col1, col2 = st.columns(2)
with col1:
    s1, s2 = st.checkbox("복토(심식)"), st.checkbox("배수 불량")
with col2:
    s3, s4 = st.checkbox("답압"), st.checkbox("복토 가해 흔적")
memo = st.text_area("상세 특이사항", height=100, placeholder="예: 수관 상단부 변색 관찰됨.")

# 6. [결과 발행]
if st.button("📄 최종 기술의견서 및 처방전 발행", type="primary", use_container_width=True):
    st.info("처방전 생성 모듈로 데이터를 전송합니다.")
