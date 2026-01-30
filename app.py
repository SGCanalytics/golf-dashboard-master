import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIG
# ============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="Golf Shot Tracker", layout="wide")

# ============================================================
# CALCULATION FUNCTIONS
# ============================================================
def determine_par(distance):
    if distance <= 245:
        return 3
    elif distance <= 475:
        return 4
    else:
        return 5

def determine_shot_type(start_location, start_distance, par):
    if start_distance is None:
        return 'Other'
    if start_location == 'Green':
        return 'Putt'
    if start_location == 'Tee':
        if par == 3:
            return 'Approach'
        else:
            return 'Driving'
    if start_location == 'Recovery':
        return 'Recovery'
    if start_distance < 50:
        return 'Short Game'
    if start_location in ['Fairway', 'Rough', 'Sand'] and 50 <= start_distance <= 245:
        return 'Approach'
    return 'Other'

def score_to_name(hole_score, par):
    diff = hole_score - par
    if diff <= -2:
        return 'Eagle'
    elif diff == -1:
        return 'Birdie'
    elif diff == 0:
        return 'Par'
    elif diff == 1:
        return 'Bogey'
    else:
        return 'Double or Worse'

# ============================================================
# LOAD AND TRANSFORM DATA
# ============================================================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(SHEET_URL)
    
    # Standardize text fields
    df['Player'] = df['Player'].str.strip().str.title()
    df['Course'] = df['Course'].str.strip().str.title()
    df['Tournament'] = df['Tournament'].str.strip().str.title()
    
    # Calculate Par from first shot of each hole
    first_shots = df[df['Shot'] == 1].copy()
    first_shots['Par'] = first_shots['Starting Distance'].apply(determine_par)
    df = df.merge(first_shots[['Round ID', 'Hole', 'Par']], on=['Round ID', 'Hole'], how='left')
    
    # Calculate Shot Type
    df['Shot Type'] = df.apply(lambda row: determine_shot_type(
        row['Starting Location'],
        row['Starting Distance'],
        row['Par']
    ), axis=1)
    
    # Create unique Shot ID
    df['Shot ID'] = df['Round ID'] + '-H' + df['Hole'].astype(str) + '-S' + df['Shot'].astype(str)
    
    return df

def build_hole_summary(filtered_df):
    hole_summary = filtered_df.groupby(['Player', 'Round ID', 'Hole', 'Par']).agg(
        num_shots=('Shot', 'count'),
        num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
        num_putts=('Shot Type', lambda x: (x == 'Putt').sum())
    ).reset_index()
    
    hole_summary['Hole Score'] = hole_summary['num_shots'] + hole_summary['num_penalties']
    hole_summary['Score Name'] = hole_summary.apply(
        lambda row: score_to_name(row['Hole Score'], row['Par']), axis=1
    )
    
    return hole_summary

def calculate_tiger5(filtered_df, hole_summary):
    # Tiger 5 #1: 3 Putts
    t5_3putt_attempts = (hole_summary['num_putts'] >= 1).sum()
    t5_3putt_fails = (hole_summary['num_putts'] >= 3).sum()
    
    # Tiger 5 #2: Double Bogeys
    t5_dbl_bogey_attempts = len(hole_summary)
    t5_dbl_bogey_fails = (hole_summary['Hole Score'] >= hole_summary['Par'] + 2).sum()
    
    # Tiger 5 #3: Bogey on Par 5
    par_5_holes = hole_summary[hole_summary['Par'] == 5]
    t5_bogey_par5_attempts = len(par_5_holes)
    t5_bogey_par5_fails = (par_5_holes['Hole Score'] >= 6).sum()
    
    # Tiger 5 #4: 2 Shot Game Shots
    short_game_shots = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()
    short_game_shots['missed_green'] = short_game_shots['Ending Location'] != 'Green'
    sg_by_hole = short_game_shots.groupby(['Player', 'Round ID', 'Hole']).agg(
        any_missed=('missed_green', 'any')
    ).reset_index()
    t5_2shot_attempts = len(sg_by_hole)
    t5_2shot_fails = sg_by_hole['any_missed'].sum()
    
    # Tiger 5 #5: Approach (125yds) Bogey
    approach_125_condition = (
        (filtered_df['Starting Distance'] <= 125) & 
        (filtered_df['Starting Location'] != 'Recovery') &
        (
            ((filtered_df['Shot'] == 3) & (filtered_df['Par'] == 5)) |
            ((filtered_df['Shot'] == 2) & (filtered_df['Par'] == 4)) |
            ((filtered_df['Shot'] == 1) & (filtered_df['Par'] == 3))
        )
    )
    approach_125_holes = filtered_df[approach_125_condition][['Player', 'Round ID', 'Hole']].drop_duplicates()
    approach_125_with_score = approach_125_holes.merge(
        hole_summary[['Player', 'Round ID', 'Hole', 'Hole Score', 'Par']],
        on=['Player', 'Round ID', 'Hole'],
        how='left'
    )
    t5_approach125_attempts = len(approach_125_with_score)
    t5_approach125_fails = (approach_125_with_score['Hole Score'] > approach_125_with_score['Par']).sum()
    
    tiger5_data = [
        {'Stat': '3 Putts', 'Attempts': t5_3putt_attempts, 'Fails': t5_3putt_fails},
        {'Stat': 'Double Bogeys', 'Attempts': t5_dbl_bogey_attempts, 'Fails': t5_dbl_bogey_fails},
        {'Stat': 'Bogey on Par 5', 'Attempts': t5_bogey_par5_attempts, 'Fails': t5_bogey_par5_fails},
        {'Stat': '2 Shot Game Shots', 'Attempts': t5_2shot_attempts, 'Fails': t5_2shot_fails},
        {'Stat': 'Approach (125yds) Bogey', 'Attempts': t5_approach125_attempts, 'Fails': t5_approach125_fails}
    ]
    
    tiger5_df = pd.DataFrame(tiger5_data)
    tiger5_df['Fail %'] = (tiger5_df['Fails'] / tiger5_df['Attempts'] * 100).round(1)
    tiger5_df['Success %'] = ((tiger5_df['Attempts'] - tiger5_df['Fails']) / tiger5_df['Attempts'] * 100).round(1)
    tiger5_df = tiger5_df.fillna(0)
    
    return tiger5_df

def calculate_scoring_distribution(hole_summary):
    score_order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double or Worse']
    
    # By Par
    scoring_dist = hole_summary.groupby(['Par', 'Score Name']).size().unstack(fill_value=0)
    scoring_dist = scoring_dist.reindex(columns=score_order, fill_value=0)
    scoring_dist['Total'] = scoring_dist.sum(axis=1)
    scoring_dist['Avg Score'] = hole_summary.groupby('Par')['Hole Score'].mean().round(2)
    
    # Calculate percentages
    scoring_pct = scoring_dist.copy()
    for col in score_order:
        scoring_pct[col] = (scoring_dist[col] / scoring_dist['Total'] * 100).round(1)
    
    return scoring_dist, scoring_pct

# ============================================================
# LOAD DATA
# ============================================================
df = load_data()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
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

# Apply filters
filtered_df = df[
    (df['Player'].isin(players)) &
    (df['Course'].isin(courses)) &
    (df['Tournament'].isin(tournaments)) &
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1])
]

# Build hole summary from filtered data
hole_summary = build_hole_summary(filtered_df)

# ============================================================
# HEADER
# ============================================================
st.title("Golf Shot Tracker Dashboard")
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
# SG BY STARTING LOCATION
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
# TIGER 5
# ============================================================
st.subheader("Tiger 5 Summary")
st.markdown("*Goal: 0 Total Fails*")

tiger5_df = calculate_tiger5(filtered_df, hole_summary)

col_t5_1, col_t5_2 = st.columns([3, 1])

with col_t5_1:
    st.dataframe(
        tiger5_df,
        use_container_width=True,
        hide_index=True
    )

with col_t5_2:
    total_fails = tiger5_df['Fails'].sum()
    st.metric("Total Tiger 5 Fails", int(total_fails))

# ============================================================
# SCORING DISTRIBUTION
# ============================================================
st.subheader("Scoring Distribution by Par")

scoring_dist, scoring_pct = calculate_scoring_distribution(hole_summary)

tab1, tab2 = st.tabs(["Counts", "Percentages"])

with tab1:
    st.dataframe(scoring_dist, use_container_width=True)

with tab2:
    score_order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double or Worse']
    st.dataframe(scoring_pct[score_order], use_container_width=True)

# Overall stats
st.markdown("**Overall**")
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    st.metric("Avg Score", f"{hole_summary['Hole Score'].mean():.2f}")

with col_s2:
    pars_or_better = (hole_summary['Hole Score'] <= hole_summary['Par']).sum()
    pars_or_better_pct = pars_or_better / len(hole_summary) * 100
    st.metric("Pars or Better", f"{pars_or_better_pct:.1f}%")

with col_s3:
    total_holes = len(hole_summary)
    st.metric("Total Holes", total_holes)

# ============================================================
# RAW DATA
# ============================================================
with st.expander("View Raw Shot Data"):
    st.dataframe(filtered_df)

with st.expander("View Hole Summary"):
    st.dataframe(hole_summary)
