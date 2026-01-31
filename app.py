import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# CONFIG
# ============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="ODU Golf Analytics", layout="wide")

SHOT_TYPE_ORDER = ['Driving', 'Approach', 'Short Game', 'Putt', 'Recovery', 'Other']

# ODU Colors
ODU_GOLD = '#FFC72C'
ODU_BLACK = '#000000'
ODU_METALLIC_GOLD = '#D3AF7E'
ODU_DARK_GOLD = '#CC8A00'
ODU_RED = '#E03C31'
ODU_PURPLE = '#753BBD'
ODU_GREEN = '#2d6a4f'

# ============================================================
# CUSTOM CSS - REPLACING ONLY THE STYLE SECTION
# ============================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* 1. DARK GRAY SIDEBAR */
    section[data-testid="stSidebar"] {{ 
        background-color: #1a1c1e !important; 
        border-right: 1px solid #2d3135; 
    }}
    
    /* 2. ODU GOLD FILTER TAGS (Fixes the "Red" color) */
    span[data-baseweb="tag"] {{
        background-color: {ODU_GOLD} !important;
        color: {ODU_BLACK} !important;
    }}

    /* 3. SIDEBAR TEXT STYLING */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{
        color: #e0e0e0 !important;
        font-family: 'Inter', sans-serif;
    }}

    /* THE REST OF YOUR EXISTING DASHBOARD STYLES */
    .stApp {{ background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%); }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    h1, h2, h3 {{ font-family: 'Playfair Display', Georgia, serif !important; letter-spacing: -0.02em; }}
    .main-title {{ font-family: 'Playfair Display', Georgia, serif; font-size: 2.8rem; font-weight: 700; color: #000000; margin-bottom: 0.25rem; }}
    .main-subtitle {{ font-family: 'Inter', sans-serif; font-size: 1rem; color: #666666; font-weight: 400; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 3px solid #FFC72C; }}
    .section-title {{ font-family: 'Playfair Display', Georgia, serif; font-size: 1.6rem; font-weight: 600; color: #000000; margin: 2.5rem 0 1.5rem 0; padding-bottom: 0.75rem; border-bottom: 2px solid #FFC72C; }}
    
    /* Tiger Card Styles stay the same as your app-4.py */
    .tiger-card-success {{ background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%); border-radius: 12px; padding: 1.25rem 1rem; text-align: center; border: 2px solid #FFC72C; margin-bottom: 1rem; }}
    .tiger-card-fail {{ background: linear-gradient(135deg, #E03C31 0%, #c93028 100%); border-radius: 12px; padding: 1.25rem 1rem; text-align: center; border: none; margin-bottom: 1rem; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Player'] = df['Player'].fillna('Unknown')
    
    # Simple Shot Type Logic
    def categorize_shot(row):
        loc = str(row['Starting Location'])
        dist = row['Starting Distance']
        if loc == 'Tee':
            # Simplified Par logic: if dist > 250 likely Par 4/5
            return 'Driving' if dist > 250 else 'Approach'
        if loc == 'Green':
            return 'Putt'
        if loc == 'Recovery':
            return 'Recovery'
        if dist < 50:
            return 'Short Game'
        return 'Approach'

    if 'Shot Type' not in df.columns:
        df['Shot Type'] = df.apply(categorize_shot, axis=1)
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
with st.sidebar:
    st.markdown('<p class="sidebar-title">ODU Golf Analytics</p>', unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-label">Player Selection</p>', unsafe_allow_html=True)
    all_players = sorted(df['Player'].unique())
    selected_players = st.multiselect("Select Players", all_players, default=all_players, label_visibility="collapsed")
    
    st.markdown('<p class="sidebar-label">Date Range</p>', unsafe_allow_html=True)
    min_date = df['Date'].min().to_pydatetime()
    max_date = df['Date'].max().to_pydatetime()
    date_range = st.date_input("Select Dates", value=(min_date, max_date), min_value=min_date, max_value=max_date, label_visibility="collapsed")

# Filter Data
filtered_df = df[df['Player'].isin(selected_players)]
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[(filtered_df['Date'].dt.date >= start_date) & (filtered_df['Date'].dt.date <= end_date)]

# ============================================================
# MAIN DASHBOARD
# ============================================================
st.markdown('<p class="main-title">Performance Command Center</p>', unsafe_allow_html=True)

tab_overview, tab_driving, tab_approach, tab_short, tab_putting = st.tabs([
    "📊 Overview", "🚀 Driving", "🎯 Approach", "⛳ Short Game", "🕳️ Putting"
])

# ============================================================
# TAB: OVERVIEW (Existing logic from your app-4.py)
# ============================================================
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total SG", f"{filtered_df['Strokes Gained'].sum():.2f}")
    with col2:
        rounds = filtered_df['Round ID'].nunique()
        st.metric("Rounds Tracked", rounds)
    with col3:
        avg_sg = filtered_df['Strokes Gained'].sum() / rounds if rounds > 0 else 0
        st.metric("SG Per Round", f"{avg_sg:.2f}")
    with col4:
        st.metric("Total Shots", len(filtered_df))

    st.markdown('<p class="section-title">Strokes Gained by Category</p>', unsafe_allow_html=True)
    sg_cat = filtered_df.groupby('Shot Type')['Strokes Gained'].sum().reindex(SHOT_TYPE_ORDER).fillna(0)
    fig_sg = px.bar(
        x=sg_cat.index, y=sg_cat.values,
        color=sg_cat.index,
        color_discrete_map={'Driving': ODU_GOLD, 'Approach': ODU_BLACK, 'Short Game': ODU_METALLIC_GOLD, 'Putt': ODU_RED}
    )
    st.plotly_chart(fig_sg, use_container_width=True)

# ============================================================
# TABS: DRIVING, APPROACH, SHORT GAME, PUTTING
# ============================================================
# [The rest of your existing logic for those tabs goes here...]
# To keep this message clean, I am including the specific fix for your Putting tab logic below
with tab_putting:
    st.markdown('<p class="section-title">Putting Analysis</p>', unsafe_allow_html=True)
    putt_shots = filtered_df[filtered_df['Shot Type'] == 'Putt'].copy()
    if len(putt_shots) > 0:
        st.metric("Total SG Putting", f"{putt_shots['Strokes Gained'].sum():.2f}")
        st.dataframe(putt_shots[['Player', 'Course', 'Hole', 'Starting Distance', 'Strokes Gained']], use_container_width=True, hide_index=True)
