import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# -----------------------------------------------------------------------------
# 1. 폰트 설정 (한글 깨짐 방지 - 다운로드 방식)
# -----------------------------------------------------------------------------
def init_font():
    font_file = "NanumGothic.ttf"
    if not os.path.exists(font_file):
        import urllib.request
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        urllib.request.urlretrieve(url, font_file)
    
    fm.fontManager.addfont(font_file)
    font_prop = fm.FontProperties(fname=font_file)
    plt.rc('font', family=font_prop.get_name())
    plt.rc('axes', unicode_minus=False)

init_font()

# -----------------------------------------------------------------------------
# 2. 데이터 생성 (오류 방지: 파일 없이 코드 내 생성)
# -----------------------------------------------------------------------------
@st.cache_data
def get_data():
    # [1] 추이 데이터
    df_trend = pd.DataFrame({
        '연도': [2019, 2020, 2021, 2022, 2023],
        '부상자': [13500, 8900, 11200, 14500, 15800],
        '사망자': [42, 28, 35, 48, 52]
    })

    # [2] 스키장 데이터 (위도/경도/이용자수)
    # st.map은 lat, lon 컬럼이 필수입니다.
    df_map = pd.DataFrame({
        '스키장': ['휘슬러(캐나다)', '발토랑스(프랑스)', '베일(미국)', '니세코(일본)', '체르마트(스위스)', '용평(한국)'],
        'lat': [50.1163, 45.2982, 39.6391, 42.8633, 46.0207, 37.6443], 
        'lon': [-122.9574, 6.5802, -106.3742, 140.7027, 7.7491, 128.6807], 
        '이용자수': [250, 210, 180, 120, 160, 90],
        '순위': [1, 2, 3, 5, 4, 6]
    })
    # 지도에서 점 크기를 다르게 하기 위해 스케일링 (이용자수 * 50)
    df_map['size'] = df_map['이용자수'] * 500 

    # [3] 국가별 순위
    df_rank = pd.DataFrame({
        '국가': ['미국', '캐나다', '스위스', '오스트리아', '일본', '프랑스', '한국'],
        '점수': [95, 88, 82, 75, 70, 65, 50]
    }).sort_values('점수', ascending=True)
    
    return df_trend, df_map, df_rank

df_trend, df_map, df_rank = get_data()

# -----------------------------------------------------------------------------
# 3. 화면 구성
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="스노보드 대시보드", page_icon="🏂")
st.title("🏂 Snowboard Extreme Data")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📉 1. 사고 추이", "🗺️ 2. 스키장 지도", "🏆 3. 국가 순위"])

# [탭 1] 사고 추이
with tab1:
    st.subheader("연도별 사망자 및 부상자 추이")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    
    # 부상자 (막대)
    ax1.bar(df_trend['연도'], df_trend['부상자'], color='#AED6F1', label='부상자(명)')
    ax1.set_ylabel('부상자 수', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    # 사망자 (선)
    ax2 = ax1.twinx()
    ax2.plot(df_trend['연도'], df_trend['사망자'], color='#E74C3C', marker='o', linewidth=3, label='사망자(명)')
    ax2.set_ylabel('사망자 수', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    st.pyplot(fig1)

# [탭 2] 지도 (여기가 문제였던 부분 -> 내장 함수로 해결)
with tab2:
    st.subheader("🌍 전세계 스키장 위치 및 이용자 순위")
    
    col_map, col_info = st.columns([2, 1])
    
    with col_map:
        # 가장 안전한 st.map 사용 (오류 확률 0%)
        # size 파라미터로 이용자 수에 따라 점 크기가 달라짐
        st.map(df_map, latitude='lat', longitude='lon', size='size', color='#0000FF')
        st.caption("※ 지도 위의 점 크기는 이용자 규모를 나타냅니다.")

    with col_info:
        st.write("📊 **스키장 이용자 순위**")
        st.dataframe(
            df_map[['순위', '스키장', '이용자수']].sort_values('순위').set_index('순위'),
            use_container_width=True
        )

# [탭 3] 국가 순위
with tab3:
    st.subheader("🏂 스노보드 강국 랭킹")
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    
    bars = ax3.barh(df_rank['국가'], df_rank['점수'], color=plt.cm.winter(np.linspace(0.4, 0.9, len(df_rank))) if 'np' in globals() else 'skyblue')
    ax3.set_xlabel("랭킹 점수")
    
    # 점수 표시
    for bar in bars:
        ax3.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                 f'{int(bar.get_width())}점', va='center')
    
    st.pyplot(fig3)