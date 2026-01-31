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
# CUSTOM CSS - UPDATED SIDEBAR & FILTER COLORS
# ============================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&family=Roboto:wght@300;400;700&display=swap');

    /* Premium Sidebar Container */
    section[data-testid="stSidebar"] {{ 
        background-color: #1a1c1e; 
        border-right: 1px solid #2d3135; 
    }}

    /* Sidebar Title */
    .sidebar-title {{ 
        font-family: 'Playfair Display', serif; 
        font-size: 1.4rem; 
        font-weight: 600; 
        color: {ODU_GOLD}; 
        margin-bottom: 0.5rem; 
        padding-bottom: 1rem; 
        border-bottom: 1px solid rgba(211, 175, 126, 0.3); 
    }}

    /* Sidebar Label */
    .sidebar-label {{ 
        font-family: 'Inter', sans-serif; 
        font-size: 0.75rem; 
        font-weight: 500; 
        color: {ODU_METALLIC_GOLD}; 
        text-transform: uppercase; 
        letter-spacing: 0.08em; 
        margin-bottom: 0.5rem; 
        margin-top: 1.25rem; 
    }}

    /* Fix for Multi-select "Red" text - Forces ODU Gold */
    span[data-baseweb="tag"] {{
        background-color: {ODU_GOLD} !important;
        color: {ODU_BLACK} !important;
    }}
    
    /* Overall App Font */
    html, body, [class*="st-"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .main-title {{
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        color: {ODU_BLACK};
        margin-bottom: 0rem;
    }}
    
    .section-title {{
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: {ODU_BLACK};
        border-bottom: 2px solid {ODU_GOLD};
        padding-bottom: 5px;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }}
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
