import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIG
# ============================================================
SHEET_URL = "YOUR_PUBLISHED_CSV_URL_HERE"

st.set_page_config(page_title="Golf Shot Tracker", layout="wide")

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    df = pd.read_csv(SHEET_URL)
    return df

df = load_data()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
st.sidebar.title("Filters")

players = st.sidebar.multiselect(
    "Player",
    options=df['Player'].unique(),
    default=df['Player'].unique()
)

courses = st.sidebar.multiselect(
    "Course",
    options=df['Course'].unique(),
    default=df['Course'].unique()
)

tournaments = st.sidebar.multiselect(
    "Tournament",
    options=df['Tournament'].unique(),
    default=df['Tournament'].unique()
)

# Apply filters
filtered_df = df[
    (df['Player'].isin(players)) &
    (df['Course'].isin(courses)) &
    (df['Tournament'].isin(tournaments))
]

# ============================================================
# HEADER
# ============================================================
st.title("🏌️ Golf Shot Tracker Dashboard")
st.markdown(f"**{len(filtered_df)}** shots from **{filtered_df['Round ID'].nunique()}** rounds")

# ============================================================
# KEY METRICS
# ============================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_sg = filtered_df['Strokes Gained'].mean()
    st.metric("Avg Strokes Gained", f"{avg_sg:.2f}")

with col2:
    total_rounds = filtered_df['Round ID'].nunique()
    st.metric("Rounds", total_rounds)

with col3:
    total_shots = len(filtered_df)
    st.metric("Total Shots", total_shots)

with col4:
    unique_players = filtered_df['Player'].nunique()
    st.metric("Players", unique_players)

# ============================================================
# SG BY SHOT TYPE
# ============================================================
st.subheader("Strokes Gained by Shot Type")

sg_by_type = filtered_df.groupby('Shot Type')['Strokes Gained'].agg(['mean', 'count']).reset_index()
sg_by_type.columns = ['Shot Type', 'Avg SG', 'Count']

fig_sg_type = px.bar(
    sg_by_type,
    x='Shot Type',
    y='Avg SG',
    color='Avg SG',
    color_continuous_scale=['#c77d3a', '#fafaf8', '#2d5016'],
    color_continuous_midpoint=0
)
st.plotly_chart(fig_sg_type, use_container_width=True)

# ============================================================
# SG BY LIE TYPE
# ============================================================
st.subheader("Strokes Gained by Starting Location")

sg_by_lie = filtered_df.groupby('Starting Location')['Strokes Gained'].agg(['mean', 'count']).reset_index()
sg_by_lie.columns = ['Starting Location', 'Avg SG', 'Count']

fig_sg_lie = px.bar(
    sg_by_lie,
    x='Starting Location',
    y='Avg SG',
    color='Avg SG',
    color_continuous_scale=['#c77d3a', '#fafaf8', '#2d5016'],
    color_continuous_midpoint=0
)
st.plotly_chart(fig_sg_lie, use_container_width=True)

# ============================================================
# RAW DATA
# ============================================================
with st.expander("View Raw Data"):
    st.dataframe(filtered_df)
