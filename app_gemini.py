import time # [추가] 재시도 대기 시간을 위해 필요

# ... (기존 코드 생략)

                # 분석 시도 (3번까지 재시도)
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = client.models.generate_content(model=model_name, contents=parts)
                        st.session_state.ai_result = response.text
                        
                        # 파싱 로직
                        species_match = re.search(r"수종:\s*\[(.*?)\]", response.text)
                        disease_match = re.search(r"병명:\s*\[(.*?)\]", response.text)
                        if species_match: st.session_state.detected_species = species_match.group(1)
                        if disease_match: st.session_state.detected_disease = disease_match.group(1)
                        
                        st.rerun()
                        break # 성공 시 루프 종료
                    except Exception as e:
                        if "503" in str(e) and attempt < max_retries - 1:
                            st.warning(f"{attempt+1}차 분석 실패 (서버 혼잡). 2초 후 재시도합니다...")
                            time.sleep(2)
                        else:
                            st.error(f"최종 분석 실패: {e}")
                            break
# ... (이하 동일)
