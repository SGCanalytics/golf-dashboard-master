import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIG
# ============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="ODU Golf Analytics", layout="wide")

# Shot type order
SHOT_TYPE_ORDER = ['Driving', 'Approach', 'Short Game', 'Putt', 'Recovery', 'Other']

# ODU Colors
ODU_GOLD = '#FFC72C'
ODU_BLACK = '#000000'
ODU_METALLIC_GOLD = '#D3AF7E'
ODU_DARK_GOLD = '#CC8A00'
ODU_RED = '#E03C31'
ODU_PURPLE = '#753BBD'

# ============================================================
# CUSTOM CSS - MODERN ELEGANT DESIGN
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%);
    }
    
    /* Hide default Streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Playfair Display', Georgia, serif !important;
        letter-spacing: -0.02em;
    }
    
    p, span, div, label, .stMarkdown {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Title */
    .main-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #000000;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    
    .main-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #666666;
        font-weight: 400;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 3px solid #FFC72C;
    }
    
    /* Section Headers */
    .section-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.6rem;
        font-weight: 600;
        color: #000000;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #FFC72C;
        letter-spacing: -0.01em;
    }
    
    /* Tiger 5 Success Card */
    .tiger-card-success {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        border-radius: 12px;
        padding: 1.25rem 1rem;
        text-align: center;
        border: 2px solid #FFC72C;
        margin-bottom: 1rem;
    }
    
    .tiger-card-success .card-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        color: #FFC72C;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    
    .tiger-card-success .card-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.25rem;
        font-weight: 700;
        color: #FFC72C;
        line-height: 1;
        margin-bottom: 0.25rem;
    }
    
    .tiger-card-success .card-unit {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        color: rgba(255,199,44,0.7);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Tiger 5 Fail Card */
    .tiger-card-fail {
        background: linear-gradient(135deg, #E03C31 0%, #c93028 100%);
        border-radius: 12px;
        padding: 1.25rem 1rem;
        text-align: center;
        border: none;
        margin-bottom: 1rem;
    }
    
    .tiger-card-fail .card-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        color: rgba(255,255,255,0.9);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    
    .tiger-card-fail .card-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.25rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 0.25rem;
    }
    
    .tiger-card-fail .card-unit {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        color: rgba(255,255,255,0.7);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Grit Score Card */
    .grit-card {
        background: linear-gradient(135deg, #FFC72C 0%, #e6b327 100%);
        border-radius: 12px;
        padding: 1.25rem 1rem;
        text-align: center;
        border: none;
        margin-bottom: 1rem;
    }
    
    .grit-card .card-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        color: rgba(0,0,0,0.7);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    
    .grit-card .card-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.25rem;
        font-weight: 700;
        color: #000000;
        line-height: 1;
        margin-bottom: 0.25rem;
    }
    
    .grit-card .card-unit {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        color: rgba(0,0,0,0.6);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* SG Metric Card */
    .sg-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e8e8e8;
        margin-bottom: 1rem;
    }
    
    .sg-card .card-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    
    .sg-card .card-value {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #000000;
        line-height: 1;
    }
    
    .sg-card .card-value.positive {
        color: #2d6a4f;
    }
    
    .sg-card .card-value.negative {
        color: #E03C31;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    .sidebar-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: #FFC72C;
        margin-bottom: 0.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #333;
    }
    
    .sidebar-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        color: #D3AF7E;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
        margin-top: 1.25rem;
    }
    
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stDateInput label {
        color: #D3AF7E !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }
    
    section[data-testid="stSidebar"] .stMultiSelect > div > div {
        background-color: #2a2a2a !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
    }
    
    section[data-testid="stSidebar"] .stDateInput > div > div > input {
        background-color: #2a2a2a !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    /* Data Table Styling */
    .stDataFrame {
        width: 100%;
    }
    
    .stDataFrame table {
        width: 100%;
        text-align: center !important;
    }
    
    .stDataFrame th {
        text-align: center !important;
        background-color: #000000 !important;
        color: #FFC72C !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
    }
    
    .stDataFrame td {
        text-align: center !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        background-color: #f8f8f8 !important;
        border-radius: 8px !important;
    }
    
    /* Metric Override */
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.8rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* Plotly Chart Container */
    .stPlotlyChart {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e8e8e8;
    }
    
    /* Spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Par Score Card */
    .par-score-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #FFC72C;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .par-score-card .par-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: #333;
    }
    
    .par-score-card .par-value {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

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
    
    df['Player'] = df['Player'].str.strip().str.title()
    df['Course'] = df['Course'].str.strip().str.title()
    df['Tournament'] = df['Tournament'].str.strip().str.title()
    
    first_shots = df[df['Shot'] == 1].copy()
    first_shots['Par'] = first_shots['Starting Distance'].apply(determine_par)
    df = df.merge(first_shots[['Round ID', 'Hole', 'Par']], on=['Round ID', 'Hole'], how='left')
    
    df['Shot Type'] = df.apply(lambda row: determine_shot_type(
        row['Starting Location'],
        row['Starting Distance'],
        row['Par']
    ), axis=1)
    
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
    
    t5_3putt_attempts = (hole_summary['num_putts'] >= 1).sum()
    t5_3putt_fails = (hole_summary['num_putts'] >= 3).sum()
    three_putt_holes = hole_summary[hole_summary['num_putts'] >= 3][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['3 Putts'] = {'attempts': t5_3putt_attempts, 'fails': t5_3putt_fails, 'detail_holes': three_putt_holes}
    
    t5_dbl_bogey_attempts = len(hole_summary)
    dbl_bogey_mask = hole_summary['Hole Score'] >= hole_summary['Par'] + 2
    t5_dbl_bogey_fails = dbl_bogey_mask.sum()
    dbl_bogey_holes = hole_summary[dbl_bogey_mask][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['Double Bogey'] = {'attempts': t5_dbl_bogey_attempts, 'fails': t5_dbl_bogey_fails, 'detail_holes': dbl_bogey_holes}
    
    par_5_holes = hole_summary[hole_summary['Par'] == 5]
    t5_bogey_par5_attempts = len(par_5_holes)
    bogey_par5_mask = par_5_holes['Hole Score'] >= 6
    t5_bogey_par5_fails = bogey_par5_mask.sum()
    bogey_par5_holes = par_5_holes[bogey_par5_mask][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['Par 5 Bogey'] = {'attempts': t5_bogey_par5_attempts, 'fails': t5_bogey_par5_fails, 'detail_holes': bogey_par5_holes}
    
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
    results['Missed Green'] = {'attempts': t5_2shot_attempts, 'fails': t5_2shot_fails, 'detail_holes': missed_sg_holes}
    
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
    results['125yd Bogey'] = {'attempts': t5_approach125_attempts, 'fails': t5_approach125_fails, 'detail_holes': approach125_fail_holes}
    
    total_attempts = sum(r['attempts'] for r in results.values())
    total_fails = sum(r['fails'] for r in results.values())
    grit_score = ((total_attempts - total_fails) / total_attempts * 100) if total_attempts > 0 else 0
    
    return results, total_fails, grit_score

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
with st.sidebar:
    st.markdown('<p class="sidebar-title">Filters</p>', unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-label">Player</p>', unsafe_allow_html=True)
    players = st.multiselect(
        "Player",
        options=sorted(df['Player'].unique()),
        default=df['Player'].unique(),
        label_visibility="collapsed"
    )
    
    st.markdown('<p class="sidebar-label">Course</p>', unsafe_allow_html=True)
    courses = st.multiselect(
        "Course",
        options=sorted(df['Course'].unique()),
        default=df['Course'].unique(),
        label_visibility="collapsed"
    )
    
    st.markdown('<p class="sidebar-label">Tournament</p>', unsafe_allow_html=True)
    tournaments = st.multiselect(
        "Tournament",
        options=sorted(df['Tournament'].unique()),
        default=df['Tournament'].unique(),
        label_visibility="collapsed"
    )
    
    df['Date'] = pd.to_datetime(df['Date'])
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    st.markdown('<p class="sidebar-label">Date Range</p>', unsafe_allow_html=True)
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )

filtered_df = df[
    (df['Player'].isin(players)) &
    (df['Course'].isin(courses)) &
    (df['Tournament'].isin(tournaments)) &
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1])
]

hole_summary = build_hole_summary(filtered_df)
tiger5_results, total_tiger5_fails, grit_score = calculate_tiger5(filtered_df, hole_summary)

# ============================================================
# HEADER
# ============================================================
st.markdown('<p class="main-title">ODU Golf Analytics</p>', unsafe_allow_html=True)
st.markdown(f'<p class="main-subtitle">{len(filtered_df)} shots from {filtered_df["Round ID"].nunique()} rounds</p>', unsafe_allow_html=True)

# ============================================================
# TIGER 5 SECTION
# ============================================================
st.markdown('<p class="section-title">Tiger 5 Performance</p>', unsafe_allow_html=True)

tiger5_names = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']

col1, col2, col3, col4, col5, col6 = st.columns(6)

for i, (col, stat_name) in enumerate(zip([col1, col2, col3, col4, col5], tiger5_names)):
    fails = int(tiger5_results[stat_name]['fails'])
    with col:
        if fails > 0:
            st.markdown(f'''
                <div class="tiger-card-fail">
                    <div class="card-label">{stat_name}</div>
                    <div class="card-value">{fails}</div>
                    <div class="card-unit">fails</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="tiger-card-success">
                    <div class="card-label">{stat_name}</div>
                    <div class="card-value">{fails}</div>
                    <div class="card-unit">fails</div>
                </div>
            ''', unsafe_allow_html=True)

with col6:
    st.markdown(f'''
        <div class="grit-card">
            <div class="card-label">Grit Score</div>
            <div class="card-value">{grit_score:.1f}%</div>
            <div class="card-unit">success rate</div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

with st.expander("View Tiger 5 Fail Details"):
    for stat_name in tiger5_names:
        detail = tiger5_results[stat_name]
        fail_count = detail['fails']
        
        if fail_count > 0:
            st.markdown(f"**{stat_name}** ({int(fail_count)} fails)")
            detail_holes = detail['detail_holes']
            
            for idx, row in detail_holes.iterrows():
                player = row['Player']
                round_id = row['Round ID']
                hole = row['Hole']
                date = row['Date']
                course = row['Course']
                par = row['Par']
                hole_score = row['Hole Score']
                
                st.caption(f"{player} | {date} | {course} | Hole {hole} (Par {int(par)}) | Score: {int(hole_score)}")
                
                if stat_name == '3 Putts':
                    shots = filtered_df[
                        (filtered_df['Player'] == player) &
                        (filtered_df['Round ID'] == round_id) &
                        (filtered_df['Hole'] == hole) &
                        (filtered_df['Shot Type'] == 'Putt')
                    ][['Shot', 'Starting Distance', 'Ending Distance', 'Strokes Gained']].copy()
                    shots.columns = ['Putt', 'Start (ft)', 'End (ft)', 'SG']
                elif stat_name == 'Missed Green':
                    shots = filtered_df[
                        (filtered_df['Player'] == player) &
                        (filtered_df['Round ID'] == round_id) &
                        (filtered_df['Hole'] == hole) &
                        (filtered_df['Shot Type'] == 'Short Game')
                    ][['Shot', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']].copy()
                    shots.columns = ['Shot', 'Start', 'Lie', 'End', 'Result', 'SG']
                else:
                    shots = filtered_df[
                        (filtered_df['Player'] == player) &
                        (filtered_df['Round ID'] == round_id) &
                        (filtered_df['Hole'] == hole)
                    ][['Shot', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']].copy()
                    shots.columns = ['Shot', 'Start', 'Lie', 'End', 'Result', 'SG']
                
                shots['SG'] = shots['SG'].round(2)
                st.dataframe(shots, use_container_width=True, hide_index=True)
            st.divider()

# ============================================================
# STROKES GAINED SUMMARY
# ============================================================
st.markdown('<p class="section-title">Strokes Gained Summary</p>', unsafe_allow_html=True)

num_rounds = filtered_df['Round ID'].nunique()
total_sg = filtered_df['Strokes Gained'].sum()
sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0

# SG Tee to Green (all shots except putts)
sg_tee_to_green = filtered_df[filtered_df['Shot Type'] != 'Putt']['Strokes Gained'].sum()

# SG Putting
sg_putting = filtered_df[filtered_df['Shot Type'] == 'Putt']['Strokes Gained'].sum()

# SG Putts 5-10 feet
putts_5_10 = filtered_df[
    (filtered_df['Shot Type'] == 'Putt') &
    (filtered_df['Starting Distance'] >= 5) &
    (filtered_df['Starting Distance'] <= 10)
]
sg_putts_5_10 = putts_5_10['Strokes Gained'].sum()

def sg_value_class(val):
    if val > 0:
        return "positive"
    elif val < 0:
        return "negative"
    return ""

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    val_class = sg_value_class(total_sg)
    st.markdown(f'''
        <div class="sg-card">
            <div class="card-label">Total SG</div>
            <div class="card-value {val_class}">{total_sg:.2f}</div>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    val_class = sg_value_class(sg_per_round)
    st.markdown(f'''
        <div class="sg-card">
            <div class="card-label">SG / Round</div>
            <div class="card-value {val_class}">{sg_per_round:.2f}</div>
        </div>
    ''', unsafe_allow_html=True)

with col3:
    val_class = sg_value_class(sg_tee_to_green)
    st.markdown(f'''
        <div class="sg-card">
            <div class="card-label">SG Tee to Green</div>
            <div class="card-value {val_class}">{sg_tee_to_green:.2f}</div>
        </div>
    ''', unsafe_allow_html=True)

with col4:
    val_class = sg_value_class(sg_putting)
    st.markdown(f'''
        <div class="sg-card">
            <div class="card-label">SG Putting</div>
            <div class="card-value {val_class}">{sg_putting:.2f}</div>
        </div>
    ''', unsafe_allow_html=True)

with col5:
    val_class = sg_value_class(sg_putts_5_10)
    st.markdown(f'''
        <div class="sg-card">
            <div class="card-label">SG Putts 5-10ft</div>
            <div class="card-value {val_class}">{sg_putts_5_10:.2f}</div>
        </div>
    ''', unsafe_allow_html=True)

# ============================================================
# SG BY SHOT TYPE
# ============================================================
st.markdown('<p class="section-title">Performance by Shot Type</p>', unsafe_allow_html=True)

sg_by_type = filtered_df.groupby('Shot Type')['Strokes Gained'].agg(
    Total_SG='sum',
    Num_Shots='count',
    SG_per_Shot='mean'
).reset_index()
sg_by_type.columns = ['Shot Type', 'Total SG', 'Shots', 'SG/Shot']
sg_by_type['Total SG'] = sg_by_type['Total SG'].round(2)
sg_by_type['SG/Shot'] = sg_by_type['SG/Shot'].round(3)

sg_by_type['Shot Type'] = pd.Categorical(sg_by_type['Shot Type'], categories=SHOT_TYPE_ORDER, ordered=True)
sg_by_type = sg_by_type.sort_values('Shot Type')

colors = [ODU_RED if x < 0 else ODU_GOLD for x in sg_by_type['Total SG']]

fig_sg_type = go.Figure(data=[
    go.Bar(
        x=sg_by_type['Shot Type'],
        y=sg_by_type['Total SG'],
        marker_color=colors,
        text=sg_by_type['Total SG'].apply(lambda x: f'{x:.2f}'),
        textposition='outside',
        textfont=dict(family='Inter', size=12, color='#000000')
    )
])

fig_sg_type.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family='Inter',
    yaxis=dict(
        title='Total Strokes Gained',
        gridcolor='#e8e8e8',
        zerolinecolor=ODU_BLACK,
        zerolinewidth=2
    ),
    xaxis=dict(title=''),
    margin=dict(t=40, b=40, l=60, r=40),
    height=400
)

col_chart, col_table = st.columns([2, 1])

with col_chart:
    st.plotly_chart(fig_sg_type, use_container_width=True)

with col_table:
    summary_table = sg_by_type[['Shot Type', 'Shots', 'SG/Shot']].copy()
    summary_table.columns = ['Shot Type', '# Shots', 'SG/Shot']
    st.dataframe(summary_table, use_container_width=True, hide_index=True, height=400)

# Shot Type Detail Expanders
for shot_type in SHOT_TYPE_ORDER:
    shot_data = filtered_df[filtered_df['Shot Type'] == shot_type]
    if len(shot_data) > 0:
        with st.expander(f"{shot_type} Details ({len(shot_data)} shots)"):
            detail_table = shot_data[['Course', 'Hole', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']].copy()
            detail_table.columns = ['Course', 'Hole', 'Start Dist', 'Start Lie', 'End Dist', 'End Lie', 'SG']
            detail_table['SG'] = detail_table['SG'].round(2)
            st.dataframe(detail_table, use_container_width=True, hide_index=True)

# ============================================================
# SG TREND BY DATE
# ============================================================
st.markdown('<p class="section-title">Strokes Gained Trend</p>', unsafe_allow_html=True)

sg_trend = filtered_df.groupby([filtered_df['Date'].dt.date, 'Shot Type'])['Strokes Gained'].sum().reset_index()
sg_trend.columns = ['Date', 'Shot Type', 'Total SG']
sg_trend['Shot Type'] = pd.Categorical(sg_trend['Shot Type'], categories=SHOT_TYPE_ORDER, ordered=True)

odu_line_colors = {
    'Driving': ODU_GOLD,
    'Approach': ODU_BLACK,
    'Short Game': ODU_DARK_GOLD,
    'Putt': ODU_METALLIC_GOLD,
    'Recovery': ODU_RED,
    'Other': ODU_PURPLE
}

fig_trend = px.line(
    sg_trend,
    x='Date',
    y='Total SG',
    color='Shot Type',
    markers=True,
    category_orders={'Shot Type': SHOT_TYPE_ORDER},
    color_discrete_map=odu_line_colors
)

fig_trend.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family='Inter',
    xaxis_title='',
    yaxis_title='Total Strokes Gained',
    yaxis=dict(gridcolor='#e8e8e8', zerolinecolor=ODU_BLACK, zerolinewidth=2),
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    margin=dict(t=60, b=40, l=60, r=40),
    height=400
)

st.plotly_chart(fig_trend, use_container_width=True)

# ============================================================
# SCORING DISTRIBUTION
# ============================================================
st.markdown('<p class="section-title">Scoring Distribution</p>', unsafe_allow_html=True)

scoring_dist, scoring_pct = calculate_scoring_distribution(hole_summary)
score_order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double or Worse']

overall_dist = hole_summary['Score Name'].value_counts().reindex(score_order, fill_value=0)

fig_pie = go.Figure(data=[go.Pie(
    labels=overall_dist.index,
    values=overall_dist.values,
    hole=0.5,
    marker_colors=[ODU_PURPLE, ODU_GOLD, ODU_METALLIC_GOLD, ODU_DARK_GOLD, ODU_RED],
    textinfo='percent+label',
    textfont=dict(family='Inter', size=12),
    insidetextorientation='horizontal'
)])

fig_pie.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family='Inter',
    showlegend=False,
    margin=dict(t=40, b=40, l=40, r=40),
    height=400
)

col_chart, col_metrics = st.columns([2, 1])

with col_chart:
    st.plotly_chart(fig_pie, use_container_width=True)

with col_metrics:
    st.markdown("**Average Score by Par**")
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    avg_by_par = hole_summary.groupby('Par')['Hole Score'].mean()
    
    for par in [3, 4, 5]:
        if par in avg_by_par.index:
            avg_score = avg_by_par[par]
            st.markdown(f'''
                <div class="par-score-card">
                    <span class="par-label">Par {par}</span>
                    <span class="par-value">{avg_score:.2f}</span>
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    overall_avg = hole_summary['Hole Score'].mean() if len(hole_summary) > 0 else 0
    st.markdown(f'''
        <div class="par-score-card" style="border-left-color: #000;">
            <span class="par-label">Overall Avg</span>
            <span class="par-value">{overall_avg:.2f}</span>
        </div>
    ''', unsafe_allow_html=True)

with st.expander("View Scoring Distribution by Par"):
    tab1, tab2 = st.tabs(["Counts", "Percentages"])
    with tab1:
        st.dataframe(scoring_dist, use_container_width=True)
    with tab2:
        st.dataframe(scoring_pct[score_order], use_container_width=True)

# ============================================================
# RAW DATA
# ============================================================
st.markdown('<p class="section-title">Data</p>', unsafe_allow_html=True)

with st.expander("View Raw Shot Data"):
    st.dataframe(filtered_df, use_container_width=True)

with st.expander("View Hole Summary"):
    # Clean up hole summary for display
    display_hole_summary = hole_summary[['Player', 'Course', 'Hole', 'Par', 'Hole Score', 'num_penalties', 'num_putts', 'Score Name']].copy()
    display_hole_summary.columns = ['Player', 'Course', 'Hole', 'Par', 'Score', 'Penalties', 'Putts', 'Result']
    st.dataframe(display_hole_summary, use_container_width=True, hide_index=True)
