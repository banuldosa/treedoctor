import streamlit as st
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# ... (앞부분 생략) ...

# 2. GPS 기반 위치 자동 특정 영역
st.markdown("### 2. 조사 위치 (GPS 자동 특정)")
col1, col2 = st.columns([4, 1])

with col1:
    # 위치 정보 가져오기
    loc_data = streamlit_geolocation()
    
    # [수정된 안전 로직] loc_data가 있고, latitude 키가 있는지 확인
    if loc_data and isinstance(loc_data, dict) and loc_data.get('latitude') is not None:
        lat = loc_data['latitude']
        lon = loc_data['longitude']
        address_display = f"현장 좌표(위도:{lat:.4f}, 경도:{lon:.4f})"
    else:
        address_display = "위치 정보를 가져오는 중입니다..."
    
    addr_input = st.text_input("현장 주소", value=address_display)

with col2:
    st.write(" ")
    st.button("📍 위치 재검색")

# ... (나머지 코드 유지) ...
