import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import sys

# 1. 시스템 내부 한글 처리(UTF-8) 환경 강제 표준화
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
    except Exception:
        pass

# 2. 웹앱 메인 타이틀 및 레이아웃 설정
st.set_page_config(page_title="Gemini AI 나무의사", page_icon="🌲", layout="centered")
st.title("🌲 구글 AI 기반 스마트 나무의사 (MVP)")
st.write("현장에서 아픈 나무 사진을 찍어 올리면 수목보호학 기반 전문 처방전이 즉시 발급됩니다.")

# 3. Streamlit Cloud Secrets로부터 안전하게 API Key 로드
GOOGLE_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not GOOGLE_API_KEY:
    st.warning("👈 Streamlit Advanced settings -> Secrets에 GEMINI_API_KEY를 올바르게 설정해 주세요.")
else:
    # 구글 GenAI 클라이언트 초기화
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    # 모바일/PC 통합 파일 업로더 가동 (카메라 촬영 및 앨범 선택 대응)
    uploaded_file = st.file_uploader("📷 아픈 나무 사진을 촬영하거나 앨범에서 선택해 주세요", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # 이미지 로드 및 화면 출력
        image = Image.open(uploaded_file)
        st.image(image, caption="분석 대상 수목 이미지", use_container_width=True)
        
        st.info("🔄 구글 최고 성능 AI가 수목 병해충 분석 및 처방전을 생성하고 있습니다. 잠시만 기다려 주세요...")

        # 🌟 인코딩 문제를 원천 차단하기 위해 지시문을 명확한 문자열로 가공
        prompt_text = (
            "당신은 전 세계 최고의 전문 나무의사(Tree Doctor)입니다. "
            "제공된 수목 사진의 병징이나 충해를 정밀 진단해 주세요. "
            "출력은 반드시 한국어로 작성해야 하며, 아래의 4가지 항목을 철저히 지켜 마크다운 서식으로 출력하세요:\n\n"
            "1. [진단명]: 정확한 수목 병명 또는 해충명\n"
            "2. [판단 이유]: 사진에서 관찰되는 병징 및 발생 원인 설명\n"
            "3. [추천 방제법]: 산림청 지침에 준하는 효과적인 약제(농약 명칭) 및 방제법\n"
            "4. [주의사항]: 약제 살포 시 주의사항 및 향후 수목 관리 팁"
        )
        
        try:
            # 🌟 [가장 중요] 한글 텍스트 인코딩 충돌을 방지하기 위해 
            # 구글 API 전용 Content 타입 객체로 안전하게 변환하여 송신
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    image,
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt_text)]
                    )
                ]
            )
            
            # 최종 결과 리포트 출력
            st.markdown("---")
            st.subheader("📋 AI 나무의사 정밀 진단서")
            if response.text:
                st.markdown(response.text)
            else:
                st.error("⚠️ AI가 이미지를 분석했으나 텍스트 답변을 생성하지 못했습니다. 다시 시도해 주세요.")
            
        except Exception as e:
            # 시스템 에러 메시지 자체의 한글 깨짐까지 방어하기 위해 안전하게 문자열 변환 처리
            error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
            st.error(f"⚠️ 진단 중 예기치 못한 통신 오류가 발생했습니다.\n상세 내용: {error_msg}")
