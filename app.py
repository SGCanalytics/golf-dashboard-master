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
    hole_summary = filtered_df.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']).agg(
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
    results = {}
    
    # Tiger 5 #1: 3 Putts
    t5_3putt_attempts = (hole_summary['num_putts'] >= 1).sum()
    t5_3putt_fails = (hole_summary['num_putts'] >= 3).sum()
    three_putt_holes = hole_summary[hole_summary['num_putts'] >= 3][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['3 Putts'] = {
        'attempts': t5_3putt_attempts,
        'fails': t5_3putt_fails,
        'detail_holes': three_putt_holes
    }
    
    # Tiger 5 #2: Double Bogeys
    t5_dbl_bogey_attempts = len(hole_summary)
    dbl_bogey_mask = hole_summary['Hole Score'] >= hole_summary['Par'] + 2
    t5_dbl_bogey_fails = dbl_bogey_mask.sum()
    dbl_bogey_holes = hole_summary[dbl_bogey_mask][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['Double Bogeys'] = {
        'attempts': t5_dbl_bogey_attempts,
        'fails': t5_dbl_bogey_fails,
        'detail_holes': dbl_bogey_holes
    }
    
    # Tiger 5 #3: Bogey on Par 5
    par_5_holes = hole_summary[hole_summary['Par'] == 5]
    t5_bogey_par5_attempts = len(par_5_holes)
    bogey_par5_mask = par_5_holes['Hole Score'] >= 6
    t5_bogey_par5_fails = bogey_par5_mask.sum()
    bogey_par5_holes = par_5_holes[bogey_par5_mask][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['Bogey on Par 5'] = {
        'attempts': t5_bogey_par5_attempts,
        'fails': t5_bogey_par5_fails,
        'detail_holes': bogey_par5_holes
    }
    
    # Tiger 5 #4: 2 Shot Game Shots
    short_game_shots = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()
    short_game_shots['missed_green'] = short_game_shots['Ending Location'] != 'Green'
    sg_by_hole = short_game_shots.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole']).agg(
        any_missed=('missed_green', 'any')
    ).reset_index()
    t5_2shot_attempts = len(sg_by_hole)
    t5_2shot_fails = sg_by_hole['any_missed'].sum()
    missed_sg_holes = sg_by_hole[sg_by_hole['any_missed']][['Player', 'Round ID', 'Date', 'Course', 'Hole']].copy()
    if len(missed_sg_holes) > 0:
        missed_sg_holes = missed_sg_holes.merge(
            hole_summary[['Player', 'Round ID', 'Hole', 'Par', 'Hole Score']],
            on=['Player', 'Round ID', 'Hole'],
            how='left'
        )
    results['2 Shot Game Shots'] = {
        'attempts': t5_2shot_attempts,
        'fails': t5_2shot_fails,
        'detail_holes': missed_sg_holes
    }
    
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
    approach_125_holes = filtered_df[approach_125_condition][['Player', 'Round ID', 'Date', 'Course', 'Hole']].drop_duplicates()
    approach_125_with_score = approach_125_holes.merge(
        hole_summary[['Player', 'Round ID', 'Hole', 'Hole Score', 'Par']],
        on=['Player', 'Round ID', 'Hole'],
        how='left'
    )
    t5_approach125_attempts = len(approach_125_with_score)
    approach125_fail_mask = approach_125_with_score['Hole Score'] > approach_125_with_score['Par']
    t5_approach125_fails = approach125_fail_mask.sum()
    approach125_fail_holes = approach_125_with_score[approach125_fail_mask].copy()
    results['Approach (125yds) Bogey'] = {
        'attempts': t5_approach125_attempts,
        'fails': t5_approach125_fails,
        'detail_holes': approach125_fail_holes
    }
    
    # Build summary dataframe
    tiger5_data = []
    for stat_name in ['3 Putts', 'Double Bogeys', 'Bogey on Par 5', '2 Shot Game Shots', 'Approach (125yds) Bogey']:
        data = results[stat_name]
        tiger5_data.append({
            'Stat': stat_name,
            'Attempts': data['attempts'],
            'Fails': data['fails']
        })
    
    tiger5_df = pd.DataFrame(tiger5_data)
    tiger5_df['Fail %'] = (tiger5_df['Fails'] / tiger5_df['Attempts'] * 100).round(1)
    tiger5_df['Success %'] = ((tiger5_df['Attempts'] - tiger5_df['Fails']) / tiger5_df['Attempts'] * 100).round(1)
    tiger5_df = tiger5_df.fillna(0)
    
    return tiger5_df, results

def get_shots_for_hole(filtered_df, player, round_id, hole):
    return filtered_df[
        (filtered_df['Player'] == player) &
        (filtered_df['Round ID'] == round_id) &
        (filtered_df['Hole'] == hole)
    ][['Shot', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']].copy()

def calculate_scoring_distribution(hole_summary):
    score_order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double or Worse']
    
    scoring_dist = hole_summary.groupby(['Par', 'Score Name']).size().unstack(fill_value=0)
    scoring_dist = scoring_dist.reindex(columns=score_order, fill_value=0)
    scoring_dist['Total'] = scoring_dist.sum(axis=1)
    scoring_dist['Avg Score'] = hole_summary.groupby('Par')['Hole Score'].mean().round(2)
    
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
# TIGER 5 (TOP FOCUS)
# ============================================================
st.header("Tiger 5 Summary")
st.markdown("*Goal: 0 Total Fails*")

tiger5_df, tiger5_details = calculate_tiger5(filtered_df, hole_summary)

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

# Tiger 5 Drill-Downs
st.subheader("Tiger 5 Fail Details")

for stat_name in ['3 Putts', 'Double Bogeys', 'Bogey on Par 5', '2 Shot Game Shots', 'Approach (125yds) Bogey']:
    detail = tiger5_details[stat_name]
    fail_count = detail['fails']
    
    if fail_count > 0:
        with st.expander(f"{stat_name} ({int(fail_count)} fails)"):
            detail_holes = detail['detail_holes']
            
            for idx, row in detail_holes.iterrows():
                player = row['Player']
                round_id = row['Round ID']
                hole = row['Hole']
                date = row['Date']
                course = row['Course']
                par = row['Par']
                hole_score = row['Hole Score']
                
                st.markdown(f"**{player}** | {date} | {course} | Hole {hole} (Par {int(par)}) | Score: {int(hole_score)}")
                
                # Get relevant shots based on fail type
                if stat_name == '3 Putts':
                    shots = filtered_df[
                        (filtered_df['Player'] == player) &
                        (filtered_df['Round ID'] == round_id) &
                        (filtered_df['Hole'] == hole) &
                        (filtered_df['Shot Type'] == 'Putt')
                    ][['Shot', 'Starting Distance', 'Ending Distance', 'Strokes Gained']].copy()
                    shots.columns = ['Putt #', 'Start (ft)', 'End (ft)', 'SG']
                
                elif stat_name == '2 Shot Game Shots':
                    shots = filtered_df[
                        (filtered_df['Player'] == player) &
                        (filtered_df['Round ID'] == round_id) &
                        (filtered_df['Hole'] == hole) &
                        (filtered_df['Shot Type'] == 'Short Game')
                    ][['Shot', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']].copy()
                    shots.columns = ['Shot #', 'Start Dist', 'Start Lie', 'End Dist', 'End Lie', 'SG']
                
                else:
                    shots = filtered_df[
                        (filtered_df['Player'] == player) &
                        (filtered_df['Round ID'] == round_id) &
                        (filtered_df['Hole'] == hole)
                    ][['Shot', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']].copy()
                    shots.columns = ['Shot #', 'Start Dist', 'Start Lie', 'End Dist', 'End Lie', 'SG']
                
                shots['SG'] = shots['SG'].round(2)
                st.dataframe(shots, use_container_width=True, hide_index=True)
                st.markdown("---")

# ============================================================
# SG BY SHOT TYPE
# ============================================================
st.header("Strokes Gained by Shot Type")

# Table
sg_by_type = filtered_df.groupby('Shot Type')['Strokes Gained'].agg(
    Total_SG='sum',
    Num_Shots='count',
    SG_per_Shot='mean'
).reset_index()
sg_by_type.columns = ['Shot Type', 'Total SG', '# Shots', 'SG/Shot']
sg_by_type['Total SG'] = sg_by_type['Total SG'].round(2)
sg_by_type['SG/Shot'] = sg_by_type['SG/Shot'].round(3)
sg_by_type = sg_by_type.sort_values('Total SG', ascending=False)

st.dataframe(sg_by_type, use_container_width=True, hide_index=True)

# Trend Chart by Date
st.subheader("SG by Shot Type Trend (by Date)")

sg_trend = filtered_df.groupby([filtered_df['Date'].dt.date, 'Shot Type'])['Strokes Gained'].sum().reset_index()
sg_trend.columns = ['Date', 'Shot Type', 'Total SG']

fig_trend = px.line(
    sg_trend,
    x='Date',
    y='Total SG',
    color='Shot Type',
    markers=True
)
fig_trend.update_layout(
    xaxis_title="Date",
    yaxis_title="Total Strokes Gained",
    hovermode="x unified"
)
fig_trend.add_hline(y=0, line_dash="dash", line_color="gray")
st.plotly_chart(fig_trend, use_container_width=True)

# Bar chart
st.subheader("Total SG by Shot Type")

fig_sg_type = px.bar(
    sg_by_type,
    x='Shot Type',
    y='Total SG',
    color='Total SG',
    color_continuous_scale=['#c77d3a', '#fafaf8', '#2d5016'],
    color_continuous_midpoint=0
)
st.plotly_chart(fig_sg_type, use_container_width=True)

# ============================================================
# SG BY STARTING LOCATION
# ============================================================
st.header("Strokes Gained by Starting Location")

sg_by_lie = filtered_df.groupby('Starting Location')['Strokes Gained'].agg(
    Total_SG='sum',
    Num_Shots='count',
    SG_per_Shot='mean'
).reset_index()
sg_by_lie.columns = ['Starting Location', 'Total SG', '# Shots', 'SG/Shot']
sg_by_lie['Total SG'] = sg_by_lie['Total SG'].round(2)
sg_by_lie['SG/Shot'] = sg_by_lie['SG/Shot'].round(3)
sg_by_lie = sg_by_lie.sort_values('Total SG', ascending=False)

st.dataframe(sg_by_lie, use_container_width=True, hide_index=True)

fig_sg_lie = px.bar(
    sg_by_lie,
    x='Starting Location',
    y='Total SG',
    color='Total SG',
    color_continuous_scale=['#c77d3a', '#fafaf8', '#2d5016'],
    color_continuous_midpoint=0
)
st.plotly_chart(fig_sg_lie, use_container_width=True)

# ============================================================
# SCORING DISTRIBUTION
# ============================================================
st.header("Scoring Distribution by Par")

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
