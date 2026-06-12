# 1. 수정된 [섹션 1] 사진 촬영 및 AI 동정 (전문가 버전)
st.markdown("### 1. 현장 사진 촬영 및 AI 정밀 동정")
uploaded_files = st.file_uploader("전체/근접/병반 3장을 업로드하세요.", type=["jpg", "png"], accept_multiple_files=True)

if st.button("🚀 AI 전문가 정밀 분석 시작"):
    if uploaded_files and len(uploaded_files) >= 1:
        with st.spinner("전문가 AI가 수종 및 병해충을 진단 중입니다..."):
            try:
                models = list(client.models.list())
                model_name = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                
                parts = []
                for f in uploaded_files:
                    img = Image.open(f).convert("RGB")
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    parts.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'))
                
                # 전문성을 높이기 위한 프롬프트 강화
                prompt = """
                당신은 숙련된 나무의사입니다. 
                제공된 사진을 바탕으로 다음 내용을 분석하세요:
                1. 수종 (국명 및 학명)
                2. 주요 발생 병해충명 (의심되는 병징 중심)
                3. 현재 상태 (피해 정도)
                결과를 '수종:OOO, 병명:OOO, 피해도:상/중/하' 형식으로 답해줘.
                """
                parts.append(types.Part.from_text(text=prompt))
                
                response = client.models.generate_content(model=model_name, contents=parts)
                st.session_state.ai_result = response.text
                st.rerun()
            except Exception as e:
                st.error(f"분석 실패: {e}")

# [보강] 결과 분리 표시 (전문가 가독성 향상)
if st.session_state.ai_result:
    st.markdown("#### 🔍 AI 정밀 진단 결과")
    st.info(st.session_state.ai_result)
    
    # 수정 가능한 입력 필드 (전문가 검수용)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("수종 확정", value="분석 결과를 바탕으로 입력")
    with col2:
        st.text_input("병명/해충명 확정", value="분석 결과를 바탕으로 입력")

st.selectbox("💡 데이터베이스 수종 검색", ["선택하세요", "잣나무(Pinus koraiensis)", "소나무(Pinus densiflora)", "느티나무(Zelkova serrata)"])
