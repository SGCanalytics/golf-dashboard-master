import streamlit as st
import pandas as pd
import plotly.express as px

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="Golf Shot Tracker", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df['Player'] = df['Player'].str.strip().str.title()
    df['Course'] = df['Course'].str.strip().str.title()
    df['Tournament'] = df['Tournament'].str.strip().str.title()
    return df

df = load_data()

st.sidebar.title("Filters")

players = st.sidebar.multiselect(
    "Player",
    options=sorted(df['Player'].unique()),
    default=df['Player'].unique()
)

courses = st.sidebar.multiselect(
    "Course",
    options=sorted(df['Course'].unique()),
    default=df['Course'].unique()
)

tournaments = st.sidebar.multiselect(
    "Tournament",
    options=sorted(df['Tournament'].unique()),
    default=df['Tournament'].unique()
)

df['Date'] = pd.to_datetime(df['Date'])
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df[
    (df['Player'].isin(players)) &
    (df['Course'].isin(courses)) &
    (df['Tournament'].isin(tournaments)) &
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1])
]

st.title("Golf Shot Tracker Dashboard")
st.markdown(f"**{len(filtered_df)}** shots from **{filtered_df['Round ID'].nunique()}** rounds")

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

with st.expander("View Raw Data"):
    st.dataframe(filtered_df)
