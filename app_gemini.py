# 2. [사진 촬영 및 AI 동정]
st.markdown("### 1. 수목 피해 사진 등록 (필수)")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 3:
    if st.button("🚀 AI 분석 시작"):
        with st.spinner("AI가 사진 3장을 종합 분석 중입니다..."):
            try:
                # 텍스트와 이미지 데이터를 각각 Part로 생성하여 리스트 구성
                content_parts = []
                for f in uploaded_files:
                    img = Image.open(f)
                    # PIL 이미지를 직접 전달하는 대신, 이미지 데이터(bytes) 기반 Part 생성
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    content_parts.append(types.Part.from_bytes(
                        data=img_bytes,
                        mime_type='image/jpeg'
                    ))
                
                # 프롬프트 텍스트 추가
                content_parts.append(types.Part.from_text(
                    text="이 3장의 사진을 종합하여 수종과 병명을 '수종:OOO, 병명:OOO' 형식으로 답해줘."
                ))
                
                # 모델 호출 (types.Content 객체로 구성하여 전달)
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=types.Content(role="user", parts=content_parts)
                )
                
                st.session_state.ai_result = response.text
                st.success(f"👉 AI 분석 완료: {st.session_state.ai_result}")
            except Exception as e:
                # 에러를 더 자세히 출력하여 디버깅
                st.error(f"분석 오류: {type(e).__name__} - {str(e)}")
