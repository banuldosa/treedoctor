# [화면 1] 상단: 현장 사진 촬영 및 AI 자동 수종 동정
st.markdown("### 1. 현장 사진 촬영 및 업로드")

# 카메라 아이콘과 함께 파일 업로드 버튼 구성
st.write("📷 **현장 수종 및 병반 사진을 3장 업로드하세요.**")
uploaded_files = st.file_uploader("", type=["jpg", "png"], accept_multiple_files=True)

# 결과 영역을 한 줄로 배치하여 가독성 향상
col1, col2 = st.columns([2, 1])
with col1:
    # AI 분석 결과를 담을 텍스트 입력창 (AI가 자동 채워줌)
    ai_result_input = st.text_input("AI 동정 결과", value=st.session_state.get('ai_result', ""), help="사진 분석 후 자동으로 채워집니다.")
with col2:
    st.write("###") # 정렬을 위한 여백
    if st.button("🚀 AI 분석 시작", use_container_width=True):
        if uploaded_files and len(uploaded_files) == 3:
            with st.spinner("이미지 최적화 및 AI 분석 중..."):
                try:
                    # AI 동정 로직 (기존 유지)
                    models = list(client.models.list())
                    model_name = models[0].name if models else 'gemini-1.5-flash'
                    parts = []
                    for f in uploaded_files:
                        img = Image.open(f)
                        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                        img.thumbnail((512, 512))
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG')
                        parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                    parts.append(types.Part.from_text(text="이 3장의 사진을 종합하여 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."))
                    
                    response = client.models.generate_content(model=model_name, contents=types.Content(role="user", parts=parts))
                    st.session_state.ai_result = response.text
                    st.rerun() # 결과 반영을 위해 페이지 새로고침
                except Exception as e:
                    st.error(f"분석 오류: {e}")
        else:
            st.warning("분석을 위해 사진 3장을 모두 업로드해주세요.")

# 우측 배치 대신 가독성을 위해 하단에 드롭다운 메뉴 배치
st.selectbox("💡 오동정 시 수종 직접 선택/검색", 
             ["선택하세요", "잣나무", "소나무", "느티나무", "은행나무", "상수리나무", "기타 수종"])
