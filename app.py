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
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    .stApp { background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif !important; letter-spacing: -0.02em; }
    p, span, div, label, .stMarkdown { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    .main-title { font-family: 'Playfair Display', Georgia, serif; font-size: 2.8rem; font-weight: 700; color: #000000; margin-bottom: 0.25rem; }
    .main-subtitle { font-family: 'Inter', sans-serif; font-size: 1rem; color: #666666; font-weight: 400; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 3px solid #FFC72C; }
    .section-title { font-family: 'Playfair Display', Georgia, serif; font-size: 1.6rem; font-weight: 600; color: #000000; margin: 2.5rem 0 1.5rem 0; padding-bottom: 0.75rem; border-bottom: 2px solid #FFC72C; }
    
    .tiger-card-success { background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%); border-radius: 12px; padding: 1.25rem 1rem; text-align: center; border: 2px solid #FFC72C; margin-bottom: 1rem; }
    .tiger-card-success .card-label { font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600; color: #FFC72C; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
    .tiger-card-success .card-value { font-family: 'Playfair Display', serif; font-size: 2.25rem; font-weight: 700; color: #FFC72C; line-height: 1; margin-bottom: 0.25rem; }
    .tiger-card-success .card-unit { font-family: 'Inter', sans-serif; font-size: 0.65rem; color: rgba(255,199,44,0.7); text-transform: uppercase; letter-spacing: 0.05em; }
    
    .tiger-card-fail { background: linear-gradient(135deg, #E03C31 0%, #c93028 100%); border-radius: 12px; padding: 1.25rem 1rem; text-align: center; border: none; margin-bottom: 1rem; }
    .tiger-card-fail .card-label { font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.9); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
    .tiger-card-fail .card-value { font-family: 'Playfair Display', serif; font-size: 2.25rem; font-weight: 700; color: #ffffff; line-height: 1; margin-bottom: 0.25rem; }
    .tiger-card-fail .card-unit { font-family: 'Inter', sans-serif; font-size: 0.65rem; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 0.05em; }
    
    .grit-card { background: linear-gradient(135deg, #FFC72C 0%, #e6b327 100%); border-radius: 12px; padding: 1.25rem 1rem; text-align: center; border: none; margin-bottom: 1rem; }
    .grit-card .card-label { font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600; color: rgba(0,0,0,0.7); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
    .grit-card .card-value { font-family: 'Playfair Display', serif; font-size: 2.25rem; font-weight: 700; color: #000000; line-height: 1; margin-bottom: 0.25rem; }
    .grit-card .card-unit { font-family: 'Inter', sans-serif; font-size: 0.65rem; color: rgba(0,0,0,0.6); text-transform: uppercase; letter-spacing: 0.05em; }
    
    .sg-card { background: #ffffff; border-radius: 12px; padding: 1.25rem 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e8e8e8; margin-bottom: 1rem; }
    .sg-card .card-label { font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600; color: #666666; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
    .sg-card .card-value { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; color: #000000; line-height: 1; }
    .sg-card .card-value.positive { color: #2d6a4f; }
    .sg-card .card-value.negative { color: #E03C31; }
    
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%); }
    .sidebar-title { font-family: 'Playfair Display', Georgia, serif; font-size: 1.4rem; font-weight: 600; color: #FFC72C; margin-bottom: 0.5rem; padding-bottom: 1rem; border-bottom: 1px solid #333; }
    .sidebar-label { font-family: 'Inter', sans-serif; font-size: 0.75rem; font-weight: 500; color: #D3AF7E; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; margin-top: 1.25rem; }
    
    .stDataFrame th { text-align: center !important; background-color: #000000 !important; color: #FFC72C !important; font-family: 'Inter', sans-serif !important; font-weight: 600 !important; font-size: 0.8rem !important; }
    .stDataFrame td { text-align: center !important; font-family: 'Inter', sans-serif !important; font-size: 0.85rem !important; }
    
    .streamlit-expanderHeader { font-family: 'Inter', sans-serif !important; font-weight: 500 !important; font-size: 0.9rem !important; background-color: #f8f8f8 !important; border-radius: 8px !important; }
    .stPlotlyChart { background: #ffffff; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e8e8e8; }
    
    .par-score-card { background: #ffffff; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-left: 4px solid #FFC72C; display: flex; justify-content: space-between; align-items: center; }
    .par-score-card .par-label { font-family: 'Inter', sans-serif; font-size: 0.9rem; font-weight: 500; color: #333; }
    .par-score-card .par-value { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 700; color: #000; }
    
    .driving-table { width: 100%; border-collapse: separate; border-spacing: 0; font-family: 'Inter', sans-serif; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
    .driving-table th { background: #1a1a1a; color: #FFC72C; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 1rem 0.75rem; text-align: center; }
    .driving-table th:first-child { text-align: left; padding-left: 1.25rem; }
    .driving-table td { padding: 0.75rem; text-align: center; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; color: #333; }
    .driving-table td:first-child { text-align: left; padding-left: 1.25rem; font-weight: 500; }
    .driving-table tr:last-child td { border-bottom: none; }
    .driving-table .row-primary { background: #f8f8f8; }
    .driving-table .row-primary td { font-weight: 600; font-size: 1rem; padding: 1rem 0.75rem; }
    .driving-table .row-header { background: #2a2a2a; }
    .driving-table .row-header td { color: #D3AF7E; font-weight: 600; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.6rem 0.75rem; }
    .driving-table .row-highlight { background: linear-gradient(90deg, #FFC72C 0%, #e6b327 100%); }
    .driving-table .row-highlight td { font-weight: 700; color: #000; padding: 0.875rem 0.75rem; }
    .driving-table .row-danger { background: linear-gradient(90deg, #E03C31 0%, #c93028 100%); }
    .driving-table .row-danger td { font-weight: 700; color: #fff; padding: 0.875rem 0.75rem; }
    .driving-table .indent { padding-left: 2rem !important; }

    .hero-stat {
    background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    border: 2px solid #FFC72C;
    margin-bottom: 1.5rem;
}

.hero-stat .hero-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;        /* was 4rem */
    font-weight: 700;
    color: #FFC72C;
    line-height: 1.1;
    margin-bottom: 0.4rem;
}

.hero-stat .hero-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #D3AF7E;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
}

.hero-stat .hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;       /* slightly smaller */
    color: rgba(255,199,44,0.75);  /* stronger contrast */
    margin-top: 0.25rem;
}

.hero-stat:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 18px rgba(255, 199, 44, 0.45);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #f0f0f0; border-radius: 8px 8px 0 0; padding: 0 24px; font-family: 'Inter', sans-serif; font-weight: 500; }
    .stTabs [aria-selected="true"] { background-color: #FFC72C !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def determine_par(distance):
    if distance <= 245: return 3
    elif distance <= 475: return 4
    else: return 5

def determine_shot_type(start_location, start_distance, par):
    if start_distance is None: return 'Other'
    if start_location == 'Green': return 'Putt'
    if start_location == 'Tee': return 'Approach' if par == 3 else 'Driving'
    if start_location == 'Recovery': return 'Recovery'
    if start_distance < 50: return 'Short Game'
    if start_location in ['Fairway', 'Rough', 'Sand'] and 50 <= start_distance <= 245: return 'Approach'
    return 'Other'

def score_to_name(hole_score, par):
    diff = hole_score - par
    if diff <= -2: return 'Eagle'
    elif diff == -1: return 'Birdie'
    elif diff == 0: return 'Par'
    elif diff == 1: return 'Bogey'
    else: return 'Double or Worse'

def sg_value_class(val):
    if val > 0: return "positive"
    elif val < 0: return "negative"
    return ""

def fmt_pct(count, total):
    return f"{count/total*100:.1f}%" if total > 0 else "-"

def fmt_pr(count, rounds):
    return f"{count/rounds:.1f}" if rounds > 0 else "-"

# Distance bucket assignment for hero cards (all lies)
def approach_bucket(distance):
    if 50 <= distance < 100:
        return "50–100"
    elif 100 <= distance < 150:
        return "100–150"
    elif 150 <= distance < 200:
        return "150–200"
    elif distance >= 200:
        return ">200"
    return None

# Distance bucket assignment for table (lie‑restricted)
def approach_bucket_table(row):
    d = row['Starting Distance']
    lie = row['Starting Location']

    # Tee + Fairway buckets
    if lie in ['Fairway', 'Tee']:
        if 50 <= d < 100:
            return "50–100"
        elif 100 <= d < 150:
            return "100–150"
        elif 150 <= d < 200:
            return "150–200"
        elif d >= 200:
            return ">200"

    # Rough buckets
    if lie == 'Rough':
        if d < 150:
            return "Rough <150"
        else:
            return "Rough >150"

    return None


# ============================================================
# DATA LOADING
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
    df['Shot Type'] = df.apply(lambda row: determine_shot_type(row['Starting Location'], row['Starting Distance'], row['Par']), axis=1)
    df['Shot ID'] = df['Round ID'] + '-H' + df['Hole'].astype(str) + '-S' + df['Shot'].astype(str)
    return df

def build_hole_summary(filtered_df):
    hole_summary = filtered_df.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']).agg(
        num_shots=('Shot', 'count'),
        num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
        num_putts=('Shot Type', lambda x: (x == 'Putt').sum()),
        total_sg=('Strokes Gained', 'sum')
    ).reset_index()
    hole_summary['Hole Score'] = hole_summary['num_shots'] + hole_summary['num_penalties']
    hole_summary['Score Name'] = hole_summary.apply(lambda row: score_to_name(row['Hole Score'], row['Par']), axis=1)
    return hole_summary

def calculate_tiger5(filtered_df, hole_summary):
    results = {}
    
    # 3 Putts
    t5_3putt_attempts = (hole_summary['num_putts'] >= 1).sum()
    t5_3putt_fails = (hole_summary['num_putts'] >= 3).sum()
    three_putt_holes = hole_summary[hole_summary['num_putts'] >= 3][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['3 Putts'] = {'attempts': t5_3putt_attempts, 'fails': t5_3putt_fails, 'detail_holes': three_putt_holes}
    
    # Double Bogey
    t5_dbl_bogey_attempts = len(hole_summary)
    dbl_bogey_mask = hole_summary['Hole Score'] >= hole_summary['Par'] + 2
    t5_dbl_bogey_fails = dbl_bogey_mask.sum()
    dbl_bogey_holes = hole_summary[dbl_bogey_mask][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['Double Bogey'] = {'attempts': t5_dbl_bogey_attempts, 'fails': t5_dbl_bogey_fails, 'detail_holes': dbl_bogey_holes}
    
    # Par 5 Bogey
    par_5_holes = hole_summary[hole_summary['Par'] == 5]
    t5_bogey_par5_attempts = len(par_5_holes)
    bogey_par5_mask = par_5_holes['Hole Score'] >= 6
    t5_bogey_par5_fails = bogey_par5_mask.sum()
    bogey_par5_holes = par_5_holes[bogey_par5_mask][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['Par 5 Bogey'] = {'attempts': t5_bogey_par5_attempts, 'fails': t5_bogey_par5_fails, 'detail_holes': bogey_par5_holes}
    
    # Missed Green (Short Game)
    short_game_shots = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()
    short_game_shots['missed_green'] = short_game_shots['Ending Location'] != 'Green'
    sg_by_hole = short_game_shots.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole']).agg(any_missed=('missed_green', 'any')).reset_index()
    t5_2shot_attempts = len(sg_by_hole)
    t5_2shot_fails = sg_by_hole['any_missed'].sum()
    missed_sg_holes = sg_by_hole[sg_by_hole['any_missed']][['Player', 'Round ID', 'Date', 'Course', 'Hole']].copy()
    if len(missed_sg_holes) > 0:
        missed_sg_holes = missed_sg_holes.merge(hole_summary[['Player', 'Round ID', 'Hole', 'Par', 'Hole Score']], on=['Player', 'Round ID', 'Hole'], how='left')
    results['Missed Green'] = {'attempts': t5_2shot_attempts, 'fails': t5_2shot_fails, 'detail_holes': missed_sg_holes}
    
    # 125yd Bogey
    approach_125_condition = (
        (filtered_df['Starting Distance'] <= 125) & 
        (filtered_df['Starting Location'] != 'Recovery') &
        (((filtered_df['Shot'] == 3) & (filtered_df['Par'] == 5)) | ((filtered_df['Shot'] == 2) & (filtered_df['Par'] == 4)) | ((filtered_df['Shot'] == 1) & (filtered_df['Par'] == 3)))
    )
    approach_125_holes = filtered_df[approach_125_condition][['Player', 'Round ID', 'Date', 'Course', 'Hole']].drop_duplicates()
    approach_125_with_score = approach_125_holes.merge(hole_summary[['Player', 'Round ID', 'Hole', 'Hole Score', 'Par']], on=['Player', 'Round ID', 'Hole'], how='left')
    t5_approach125_attempts = len(approach_125_with_score)
    approach125_fail_mask = approach_125_with_score['Hole Score'] > approach_125_with_score['Par']
    t5_approach125_fails = approach125_fail_mask.sum()
    approach125_fail_holes = approach_125_with_score[approach125_fail_mask].copy()
    results['125yd Bogey'] = {'attempts': t5_approach125_attempts, 'fails': t5_approach125_fails, 'detail_holes': approach125_fail_holes}
    
    total_attempts = sum(r['attempts'] for r in results.values())
    total_fails = sum(r['fails'] for r in results.values())
    grit_score = ((total_attempts - total_fails) / total_attempts * 100) if total_attempts > 0 else 0
    
    return results, total_fails, grit_score

# ============================================================
# LOAD DATA
# ============================================================
df = load_data()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<p class="sidebar-title">ODU Golf</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-label">Filters</p>', unsafe_allow_html=True)
    
    players = st.multiselect("Player", options=sorted(df['Player'].unique()), default=df['Player'].unique(), label_visibility="collapsed")
    
    st.markdown('<p class="sidebar-label">Course</p>', unsafe_allow_html=True)
    courses = st.multiselect("Course", options=sorted(df['Course'].unique()), default=df['Course'].unique(), label_visibility="collapsed")
    
    st.markdown('<p class="sidebar-label">Tournament</p>', unsafe_allow_html=True)
    tournaments = st.multiselect("Tournament", options=sorted(df['Tournament'].unique()), default=df['Tournament'].unique(), label_visibility="collapsed")
    
    df['Date'] = pd.to_datetime(df['Date'])
    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    
    st.markdown('<p class="sidebar-label">Date Range</p>', unsafe_allow_html=True)
    date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date, label_visibility="collapsed")

# Apply filters
filtered_df = df[
    (df['Player'].isin(players)) & (df['Course'].isin(courses)) & (df['Tournament'].isin(tournaments)) &
    (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
]

hole_summary = build_hole_summary(filtered_df)
num_rounds = filtered_df['Round ID'].nunique()

# ============================================================
# HEADER
# ============================================================
st.markdown('<p class="main-title">ODU Golf Analytics</p>', unsafe_allow_html=True)
st.markdown(f'<p class="main-subtitle">{len(filtered_df)} shots from {num_rounds} rounds</p>', unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
tab_overview, tab_driving, tab_approach, tab_short_game, tab_putting = st.tabs(["📊 Overview", "🏌️ Driving", "🎯 Approach", "⛳ Short Game", "🕳️ Putting"])

# ============================================================
# TAB: OVERVIEW
# ============================================================
with tab_overview:
    tiger5_results, total_tiger5_fails, grit_score = calculate_tiger5(filtered_df, hole_summary)
    
    # Tiger 5 Section
    st.markdown('<p class="section-title">Tiger 5 Performance</p>', unsafe_allow_html=True)
    tiger5_names = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    for col, stat_name in zip([col1, col2, col3, col4, col5], tiger5_names):
        fails = int(tiger5_results[stat_name]['fails'])
        attempts = int(tiger5_results[stat_name]['attempts'])
        with col:
            card_class = "tiger-card-fail" if fails > 0 else "tiger-card-success"
            st.markdown(f'''
                <div class="{card_class}">
                    <div class="card-label">{stat_name}</div>
                    <div class="card-value">{fails}</div>
                    <div class="card-unit">of {attempts}</div>
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

    # Tiger 5 Trend Chart (Stacked Bar + Score Line)
    with st.expander("View Tiger 5 Trend by Round"):
        # Calculate Tiger 5 failures by round
        round_info = filtered_df.groupby('Round ID').agg(
            Date=('Date', 'first'),
            Course=('Course', 'first')
        ).reset_index()
        
        # Build hole summary by round for Tiger 5 calculations
        t5_by_round = []
        for _, round_row in round_info.iterrows():
            rid = round_row['Round ID']
            round_holes = hole_summary[hole_summary['Round ID'] == rid]
            round_shots = filtered_df[filtered_df['Round ID'] == rid]
            
            # 3 Putts
            three_putts = (round_holes['num_putts'] >= 3).sum()
            
            # Double Bogey
            dbl_bogey = (round_holes['Hole Score'] >= round_holes['Par'] + 2).sum()
            
            # Par 5 Bogey
            par5_holes = round_holes[round_holes['Par'] == 5]
            par5_bogey = (par5_holes['Hole Score'] >= 6).sum()
            
            # Missed Green (short game not ending on green)
            sg_shots = round_shots[round_shots['Shot Type'] == 'Short Game']
            if len(sg_shots) > 0:
                sg_shots_missed = sg_shots[sg_shots['Ending Location'] != 'Green']
                missed_green_holes = sg_shots_missed[['Hole']].drop_duplicates()
                missed_green = len(missed_green_holes)
            else:
                missed_green = 0
            
            # 125yd Bogey
            approach_125 = round_shots[
                (round_shots['Starting Distance'] <= 125) & 
                (round_shots['Starting Location'] != 'Recovery') &
                (((round_shots['Shot'] == 3) & (round_shots['Par'] == 5)) | 
                 ((round_shots['Shot'] == 2) & (round_shots['Par'] == 4)) | 
                 ((round_shots['Shot'] == 1) & (round_shots['Par'] == 3)))
            ]
            if len(approach_125) > 0:
                approach_holes = approach_125[['Hole']].drop_duplicates()
                approach_with_score = approach_holes.merge(round_holes[['Hole', 'Hole Score', 'Par']], on='Hole')
                bogey_125 = (approach_with_score['Hole Score'] > approach_with_score['Par']).sum()
            else:
                bogey_125 = 0
            
            # Total score for round
            total_score = round_holes['Hole Score'].sum()
            
            # Create label: Mon-YY Course
            date_obj = pd.to_datetime(round_row['Date'])
            label = f"{date_obj.strftime('%m/%d/%Y')} {round_row['Course']}"
            
            t5_by_round.append({
                'Round ID': rid,
                'Label': label,
                'Date': date_obj,
                '3 Putts': three_putts,
                'Double Bogey': dbl_bogey,
                'Par 5 Bogey': par5_bogey,
                'Missed Green': missed_green,
                '125yd Bogey': bogey_125,
                'Total Score': total_score
            })
        
        t5_df = pd.DataFrame(t5_by_round).sort_values('Date')
        t5_df['Total Fails'] = t5_df['3 Putts'] + t5_df['Double Bogey'] + t5_df['Par 5 Bogey'] + t5_df['Missed Green'] + t5_df['125yd Bogey']
        
        # Create stacked bar chart with score line
        fig_t5_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        t5_categories = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']
        t5_colors = [ODU_RED, ODU_DARK_GOLD, ODU_METALLIC_GOLD, ODU_PURPLE, ODU_BLACK]
        
        for cat, color in zip(t5_categories, t5_colors):
            fig_t5_trend.add_trace(
                go.Bar(name=cat, x=t5_df['Label'], y=t5_df[cat], marker_color=color),
                secondary_y=False
            )
        
        fig_t5_trend.add_trace(
            go.Scatter(
                name='Total Score',
                x=t5_df['Label'],
                y=t5_df['Total Score'],
                mode='lines+markers',
                line=dict(color=ODU_GOLD, width=3),
                marker=dict(size=10, color=ODU_GOLD, line=dict(color=ODU_BLACK, width=2))
            ),
            secondary_y=True
        )
        
        fig_t5_trend.update_layout(
            barmode='stack',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_family='Inter',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            margin=dict(t=60, b=80, l=60, r=60),
            height=400,
            hovermode='x unified'
        )
        
        fig_t5_trend.update_xaxes(title_text='', tickangle=-45)
        fig_t5_trend.update_yaxes(title_text='Tiger 5 Fails', gridcolor='#e8e8e8', secondary_y=False)
        fig_t5_trend.update_yaxes(title_text='Total Score', showgrid=False, secondary_y=True)
        
        st.plotly_chart(fig_t5_trend, use_container_width=True, config={'displayModeBar': False})

    with st.expander("View Tiger 5 Fail Details"):
        for stat_name in tiger5_names:
            detail = tiger5_results[stat_name]
            if detail['fails'] > 0:
                st.markdown(f"**{stat_name}** ({int(detail['fails'])} fails)")
                for idx, row in detail['detail_holes'].iterrows():
                    st.caption(f"{row['Player']} | {row['Date']} | {row['Course']} | Hole {row['Hole']} (Par {int(row['Par'])}) | Score: {int(row['Hole Score'])}")
                    if stat_name == '3 Putts':
                        shots = filtered_df[(filtered_df['Player'] == row['Player']) & (filtered_df['Round ID'] == row['Round ID']) & (filtered_df['Hole'] == row['Hole']) & (filtered_df['Shot Type'] == 'Putt')][['Shot', 'Starting Distance', 'Ending Distance', 'Strokes Gained']].copy()
                        shots.columns = ['Putt', 'Start (ft)', 'End (ft)', 'SG']
                    else:
                        shots = filtered_df[(filtered_df['Player'] == row['Player']) & (filtered_df['Round ID'] == row['Round ID']) & (filtered_df['Hole'] == row['Hole'])][['Shot', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']].copy()
                        shots.columns = ['Shot', 'Start', 'Lie', 'End', 'Result', 'SG']
                    shots['SG'] = shots['SG'].round(2)
                    st.dataframe(shots, use_container_width=True, hide_index=True)
                st.divider()

    # SG Summary
    st.markdown('<p class="section-title">Strokes Gained Summary</p>', unsafe_allow_html=True)
    
    total_sg = filtered_df['Strokes Gained'].sum()
    sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0
    sg_tee_to_green = filtered_df[filtered_df['Shot Type'] != 'Putt']['Strokes Gained'].sum()
    
    # SG Putting >30 feet
    putts_over_30 = filtered_df[(filtered_df['Shot Type'] == 'Putt') & (filtered_df['Starting Distance'] > 30)]
    sg_putts_over_30 = putts_over_30['Strokes Gained'].sum()
    
    # SG Putts 5-10ft
    putts_5_10 = filtered_df[(filtered_df['Shot Type'] == 'Putt') & (filtered_df['Starting Distance'] >= 5) & (filtered_df['Starting Distance'] <= 10)]
    sg_putts_5_10 = putts_5_10['Strokes Gained'].sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [('Total SG', total_sg), ('SG / Round', sg_per_round), ('SG Tee to Green', sg_tee_to_green), ('SG Putting >30ft', sg_putts_over_30), ('SG Putts 5-10ft', sg_putts_5_10)]
    for col, (label, val) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            val_class = sg_value_class(val)
            st.markdown(f'''<div class="sg-card"><div class="card-label">{label}</div><div class="card-value {val_class}">{val:.2f}</div></div>''', unsafe_allow_html=True)

    # SG by Shot Type
    st.markdown('<p class="section-title">Performance by Shot Type</p>', unsafe_allow_html=True)
    
    sg_by_type = filtered_df.groupby('Shot Type')['Strokes Gained'].agg(Total_SG='sum', Num_Shots='count', SG_per_Shot='mean').reset_index()
    sg_by_type.columns = ['Shot Type', 'Total SG', 'Shots', 'SG/Shot']
    sg_by_type['Total SG'] = sg_by_type['Total SG'].round(2)
    sg_by_type['SG/Shot'] = sg_by_type['SG/Shot'].round(3)
    sg_by_type['Shot Type'] = pd.Categorical(sg_by_type['Shot Type'], categories=SHOT_TYPE_ORDER, ordered=True)
    sg_by_type = sg_by_type.sort_values('Shot Type')
    sg_by_type = sg_by_type[sg_by_type['Shots'] > 0]  # Remove empty shot types

    colors = [ODU_RED if x < 0 else ODU_GOLD for x in sg_by_type['Total SG']]
    fig_sg_type = go.Figure(data=[go.Bar(x=sg_by_type['Shot Type'], y=sg_by_type['Total SG'], marker_color=colors, text=sg_by_type['Total SG'].apply(lambda x: f'{x:.2f}'), textposition='outside', textfont=dict(family='Inter', size=12, color='#000000'))])
    fig_sg_type.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family='Inter', yaxis=dict(title='Total Strokes Gained', gridcolor='#e8e8e8', zerolinecolor=ODU_BLACK, zerolinewidth=2), xaxis=dict(title=''), margin=dict(t=40, b=40, l=60, r=40), height=400)

    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig_sg_type, use_container_width=True)
    with col_table:
        st.dataframe(sg_by_type[['Shot Type', 'Shots', 'SG/Shot']], use_container_width=True, hide_index=True, height=400)

    # SG Trend Line Graph
    st.markdown('<p class="section-title">Strokes Gained Trend</p>', unsafe_allow_html=True)
    
    # Create round labels for x-axis
    round_labels = filtered_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()
    round_labels['Label'] = round_labels.apply(lambda r: f"{pd.to_datetime(r['Date']).strftime('%m/%d/%Y')} {r['Course']}", axis=1)
    
    sg_trend = filtered_df[~filtered_df['Shot Type'].isin(['Recovery', 'Other'])].groupby(['Round ID', 'Shot Type'])['Strokes Gained'].sum().reset_index()
    sg_trend = sg_trend.merge(round_labels[['Round ID', 'Label', 'Date']], on='Round ID')
    sg_trend = sg_trend.sort_values('Date')
    sg_trend['Shot Type'] = pd.Categorical(sg_trend['Shot Type'], categories=SHOT_TYPE_ORDER, ordered=True)

    odu_line_colors = {'Driving': ODU_GOLD, 'Approach': ODU_BLACK, 'Short Game': ODU_PURPLE, 'Putt': ODU_GREEN}

    fig_trend = px.line(sg_trend, x='Label', y='Strokes Gained', color='Shot Type', markers=True, category_orders={'Shot Type': SHOT_TYPE_ORDER}, color_discrete_map=odu_line_colors)
    fig_trend.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family='Inter', xaxis_title='', yaxis_title='Total Strokes Gained', yaxis=dict(gridcolor='#e8e8e8', zerolinecolor=ODU_BLACK, zerolinewidth=2), hovermode='x unified', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(t=60, b=80, l=60, r=40), height=400, xaxis=dict(tickangle=-45))
    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

    # Scoring Distribution
    st.markdown('<p class="section-title">Scoring Distribution</p>', unsafe_allow_html=True)
    
    score_order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double or Worse']
    overall_dist = hole_summary['Score Name'].value_counts().reindex(score_order, fill_value=0)

    fig_pie = go.Figure(data=[go.Pie(labels=overall_dist.index, values=overall_dist.values, hole=0.5, marker_colors=[ODU_PURPLE, ODU_GOLD, ODU_METALLIC_GOLD, ODU_DARK_GOLD, ODU_RED], textinfo='percent+label', textfont=dict(family='Inter', size=12))])
    fig_pie.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family='Inter', showlegend=False, margin=dict(t=40, b=40, l=40, r=40), height=400)

    col_chart, col_metrics = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_metrics:
        st.markdown("**Average Score by Par**")
        avg_by_par = hole_summary.groupby('Par')['Hole Score'].mean()
        sg_by_par = hole_summary.groupby('Par')['total_sg'].sum()
        for par in [3, 4, 5]:
            if par in avg_by_par.index:
                sg_val = sg_by_par.get(par, 0)
                sg_color = ODU_GREEN if sg_val >= 0 else ODU_RED
                st.markdown(f'''<div class="par-score-card"><span class="par-label">Par {par}</span><span class="par-value">{avg_by_par[par]:.2f}</span></div>''', unsafe_allow_html=True)
        
        st.markdown("**Total SG by Par**")
        for par in [3, 4, 5]:
            if par in sg_by_par.index:
                sg_val = sg_by_par[par]
                border_color = ODU_GREEN if sg_val >= 0 else ODU_RED
                st.markdown(f'''<div class="par-score-card" style="border-left-color: {border_color};"><span class="par-label">Par {par}</span><span class="par-value" style="color: {border_color};">{sg_val:+.2f}</span></div>''', unsafe_allow_html=True)

    # Data Section
    st.markdown('<p class="section-title">Data</p>', unsafe_allow_html=True)
    with st.expander("View Raw Shot Data"):
        st.dataframe(filtered_df, use_container_width=True)
    with st.expander("View Hole Summary"):
        display_hole_summary = hole_summary[['Player', 'Course', 'Hole', 'Par', 'Hole Score', 'num_penalties', 'num_putts', 'Score Name']].copy()
        display_hole_summary.columns = ['Player', 'Course', 'Hole', 'Par', 'Score', 'Penalties', 'Putts', 'Result']
        st.dataframe(display_hole_summary, use_container_width=True, hide_index=True)

# ============================================================
# TAB: DRIVING
# ============================================================
with tab_driving:
    driving_shots = filtered_df[filtered_df['Shot Type'] == 'Driving'].copy()
    num_drives = len(driving_shots)
    
    if num_drives == 0:
        st.warning("No driving data available for the selected filters.")
    else:
        driving_sg = driving_shots['Strokes Gained'].sum()
        driving_sg_per_round = driving_sg / num_rounds if num_rounds > 0 else 0
        
        end_loc_counts = driving_shots['Ending Location'].value_counts()
        fairway_count = end_loc_counts.get('Fairway', 0)
        rough_count = end_loc_counts.get('Rough', 0)
        sand_count = end_loc_counts.get('Sand', 0)
        recovery_count = end_loc_counts.get('Recovery', 0)
        green_count = end_loc_counts.get('Green', 0)
        
        penalty_drives = driving_shots[driving_shots['Penalty'] == 'Yes']
        penalty_count = len(penalty_drives)
        
        # OB Detection
        drive_holes = driving_shots[['Player', 'Round ID', 'Hole', 'Course', 'Date']].drop_duplicates()
        ob_count = 0
        ob_details = []
        for _, row in drive_holes.iterrows():
            hole_shots = filtered_df[(filtered_df['Player'] == row['Player']) & (filtered_df['Round ID'] == row['Round ID']) & (filtered_df['Hole'] == row['Hole'])].sort_values('Shot')
            if len(hole_shots) >= 2 and hole_shots.iloc[0]['Starting Location'] == 'Tee' and hole_shots.iloc[1]['Starting Location'] == 'Tee':
                ob_count += 1
                ob_details.append({'Player': row['Player'], 'Date': row['Date'], 'Course': row['Course'], 'Hole': row['Hole']})
        
        obstruction_count = sand_count + recovery_count
        obstruction_pct = (obstruction_count / num_drives * 100) if num_drives > 0 else 0
        penalty_total = penalty_count + ob_count
        penalty_rate_pct = (penalty_total / num_drives * 100) if num_drives > 0 else 0
        fairway_pct = (fairway_count / num_drives * 100) if num_drives > 0 else 0

        # Hero Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'''<div class="hero-stat"><div class="hero-value" style="color: {'#2d6a4f' if driving_sg >= 0 else '#E03C31'};">{driving_sg:+.2f}</div><div class="hero-label">Total SG Driving</div><div class="hero-sub">{driving_sg_per_round:+.2f} per round</div></div>''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''<div class="hero-stat" style="border-color: #FFC72C;"><div class="hero-value">{fairway_pct:.0f}%</div><div class="hero-label">Fairways Hit</div><div class="hero-sub">{fairway_count} of {num_drives} drives</div></div>''', unsafe_allow_html=True)
        with col3:
            color = '#E03C31' if obstruction_pct > 10 else '#FFC72C'
            st.markdown(f'''<div class="hero-stat" style="border-color: {color};"><div class="hero-value" style="color: {color};">{obstruction_pct:.1f}%</div><div class="hero-label">Obstruction Rate</div><div class="hero-sub">Sand + Recovery</div></div>''', unsafe_allow_html=True)
        with col4:
            color = '#E03C31' if penalty_rate_pct > 5 else '#FFC72C'
            st.markdown(f'''<div class="hero-stat" style="border-color: {color};"><div class="hero-value" style="color: {color};">{penalty_total}</div><div class="hero-label">Penalties + OB</div><div class="hero-sub">{penalty_rate_pct:.1f}% of drives</div></div>''', unsafe_allow_html=True)

        st.markdown('<p class="section-title">Where Are Your Drives Landing?</p>', unsafe_allow_html=True)
        col_viz, col_table = st.columns([1, 1])
        
        with col_viz:
            loc_labels = ['Fairway', 'Rough', 'Sand', 'Recovery', 'Green']
            loc_values = [fairway_count, rough_count, sand_count, recovery_count, green_count]
            loc_colors = [ODU_GOLD, ODU_DARK_GOLD, ODU_METALLIC_GOLD, ODU_RED, ODU_GREEN]
            chart_data = [(l, v, c) for l, v, c in zip(loc_labels, loc_values, loc_colors) if v > 0]
            
            fig_donut = go.Figure(data=[go.Pie(labels=[d[0] for d in chart_data], values=[d[1] for d in chart_data], hole=0.6, marker_colors=[d[2] for d in chart_data], textinfo='label+percent', textposition='outside', textfont=dict(family='Inter', size=12), pull=[0.02] * len(chart_data))])
            fig_donut.update_layout(showlegend=False, margin=dict(t=40, b=40, l=40, r=40), height=400, annotations=[dict(text=f'<b>{num_drives}</b><br>Drives', x=0.5, y=0.5, font=dict(family='Playfair Display', size=24, color='#000'), showarrow=False)])
            st.plotly_chart(fig_donut, use_container_width=True)
        
        with col_table:
            table_html = f'''
            <table class="driving-table">
                <tr><th style="text-align: left;">Metric</th><th>#</th><th>%</th><th>Per Round</th></tr>
                <tr class="row-primary"><td><strong>Driving</strong></td><td><strong>{num_drives}</strong></td><td>-</td><td><strong>{num_drives/num_rounds:.1f}</strong></td></tr>
                <tr class="row-header"><td colspan="4">Ending Location</td></tr>
                <tr><td class="indent">Fairway</td><td>{fairway_count}</td><td>{fmt_pct(fairway_count, num_drives)}</td><td>{fmt_pr(fairway_count, num_rounds)}</td></tr>
                <tr><td class="indent">Rough</td><td>{rough_count}</td><td>{fmt_pct(rough_count, num_drives)}</td><td>{fmt_pr(rough_count, num_rounds)}</td></tr>
                <tr><td class="indent">Sand</td><td>{sand_count}</td><td>{fmt_pct(sand_count, num_drives)}</td><td>{fmt_pr(sand_count, num_rounds)}</td></tr>
                <tr><td class="indent">Recovery</td><td>{recovery_count}</td><td>{fmt_pct(recovery_count, num_drives)}</td><td>{fmt_pr(recovery_count, num_rounds)}</td></tr>
                <tr class="row-highlight"><td><strong>Obstruction Rate</strong></td><td><strong>{obstruction_count}</strong></td><td><strong>{fmt_pct(obstruction_count, num_drives)}</strong></td><td><strong>{fmt_pr(obstruction_count, num_rounds)}</strong></td></tr>
                <tr class="row-header"><td colspan="4">Penalties</td></tr>
                <tr><td class="indent">Penalty Strokes</td><td>{penalty_count}</td><td>{fmt_pct(penalty_count, num_drives)}</td><td>{fmt_pr(penalty_count, num_rounds)}</td></tr>
                <tr><td class="indent">OB (Re-Tee)</td><td>{ob_count}</td><td>{fmt_pct(ob_count, num_drives)}</td><td>{fmt_pr(ob_count, num_rounds)}</td></tr>
                <tr class="{'row-danger' if penalty_total > 0 else 'row-highlight'}"><td><strong>Penalty Rate</strong></td><td><strong>{penalty_total}</strong></td><td><strong>{fmt_pct(penalty_total, num_drives)}</strong></td><td><strong>{fmt_pr(penalty_total, num_rounds)}</strong></td></tr>
            </table>
            '''
            st.markdown(table_html, unsafe_allow_html=True)

        # SG by Result
        st.markdown('<p class="section-title">Strokes Gained by Result</p>', unsafe_allow_html=True)
        sg_by_result = driving_shots.groupby('Ending Location')['Strokes Gained'].agg(['sum', 'count', 'mean']).reset_index()
        sg_by_result.columns = ['Result', 'Total SG', 'Shots', 'SG/Shot']
        sg_by_result = sg_by_result.sort_values('Total SG', ascending=True)
        colors_bar = [ODU_RED if x < 0 else ODU_GOLD for x in sg_by_result['Total SG']]
        fig_sg_result = go.Figure(data=[go.Bar(y=sg_by_result['Result'], x=sg_by_result['Total SG'], orientation='h', marker_color=colors_bar, text=sg_by_result['Total SG'].apply(lambda x: f'{x:+.2f}'), textposition='outside', textfont=dict(family='Inter', size=12, color='#000'))])
        fig_sg_result.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family='Inter', xaxis=dict(title='Strokes Gained', gridcolor='#e8e8e8', zerolinecolor=ODU_BLACK, zerolinewidth=2), yaxis=dict(title=''), margin=dict(t=20, b=40, l=100, r=80), height=250)
        st.plotly_chart(fig_sg_result, use_container_width=True)

        # Trend
        st.markdown('<p class="section-title">Driving Performance Trend</p>', unsafe_allow_html=True)
        
        # Create round labels
        drive_round_labels = driving_shots.groupby('Round ID').agg(
            Date=('Date', 'first'),
            Course=('Course', 'first')
        ).reset_index()
        drive_round_labels['Label'] = drive_round_labels.apply(lambda r: f"{pd.to_datetime(r['Date']).strftime('%m/%d/%Y')} {r['Course']}", axis=1)
        
        driving_trend = driving_shots.groupby('Round ID').agg(SG=('Strokes Gained', 'sum'), Drives=('Shot', 'count'), Fairways=('Ending Location', lambda x: (x == 'Fairway').sum())).reset_index()
        driving_trend = driving_trend.merge(drive_round_labels[['Round ID', 'Label', 'Date']], on='Round ID')
        driving_trend = driving_trend.sort_values('Date')
        driving_trend['Fairway %'] = (driving_trend['Fairways'] / driving_trend['Drives'] * 100).round(1)
        
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(go.Bar(x=driving_trend['Label'], y=driving_trend['SG'], name='SG Driving', marker_color=[ODU_RED if x < 0 else ODU_GOLD for x in driving_trend['SG']], opacity=0.8), secondary_y=False)
        fig_trend.add_trace(go.Scatter(x=driving_trend['Label'], y=driving_trend['Fairway %'], name='Fairway %', mode='lines+markers', line=dict(color=ODU_BLACK, width=3), marker=dict(size=10, color=ODU_BLACK)), secondary_y=True)
        fig_trend.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family='Inter', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(t=60, b=80, l=60, r=60), height=350, hovermode='x unified', xaxis=dict(tickangle=-45))
        fig_trend.update_yaxes(title_text="Strokes Gained", gridcolor='#e8e8e8', zerolinecolor=ODU_BLACK, zerolinewidth=2, secondary_y=False)
        fig_trend.update_yaxes(title_text="Fairway %", range=[0, 100], showgrid=False, secondary_y=True)
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

        # Detail Tables
        st.markdown('<p class="section-title">Detailed Data</p>', unsafe_allow_html=True)
        with st.expander(f"📋 All Driving Shots ({num_drives} total)"):
            drive_detail = driving_shots[['Player', 'Date', 'Course', 'Hole', 'Starting Distance', 'Ending Distance', 'Ending Location', 'Penalty', 'Strokes Gained']].copy()
            drive_detail['Date'] = pd.to_datetime(drive_detail['Date']).dt.strftime('%m/%d/%Y')
            drive_detail.columns = ['Player', 'Date', 'Course', 'Hole', 'Distance', 'End Dist', 'Result', 'Penalty', 'SG']
            drive_detail['Hole'] = drive_detail['Hole'].astype(int)
            drive_detail['Distance'] = drive_detail['Distance'].round(0).astype(int)
            drive_detail['End Dist'] = drive_detail['End Dist'].round(0).astype(int)
            drive_detail['SG'] = drive_detail['SG'].round(2)
            st.dataframe(drive_detail.sort_values(['Date', 'Hole'], ascending=[False, True]), use_container_width=True, hide_index=True)
        
        if ob_count > 0:
            with st.expander(f"⚠️ OB / Re-Tee Instances ({ob_count} total)"):
                ob_df = pd.DataFrame(ob_details)
                ob_df['Date'] = pd.to_datetime(ob_df['Date']).dt.strftime('%m/%d/%Y')
                ob_df['Hole'] = ob_df['Hole'].astype(int)
                st.dataframe(ob_df, use_container_width=True, hide_index=True)
        
        if obstruction_count > 0:
            with st.expander(f"🏖️ Obstruction Shots ({obstruction_count} total)"):
                obs_shots = driving_shots[driving_shots['Ending Location'].isin(['Sand', 'Recovery'])][['Player', 'Date', 'Course', 'Hole', 'Starting Distance', 'Ending Location', 'Strokes Gained']].copy()
                obs_shots['Date'] = pd.to_datetime(obs_shots['Date']).dt.strftime('%m/%d/%Y')
                obs_shots.columns = ['Player', 'Date', 'Course', 'Hole', 'Distance', 'Result', 'SG']
                obs_shots['Hole'] = obs_shots['Hole'].astype(int)
                obs_shots['Distance'] = obs_shots['Distance'].round(0).astype(int)
                obs_shots['SG'] = obs_shots['SG'].round(2)
                st.dataframe(obs_shots, use_container_width=True, hide_index=True)

# ============================================================
# TAB: APPROACH
# ============================================================
with tab_approach:
    st.markdown('<p class="section-title">Approach Play</p>', unsafe_allow_html=True)

    # Filter to approach shots only
    approach_df = filtered_df[filtered_df['Shot Type'] == 'Approach'].copy()

    # Assign hero buckets
    approach_df['Hero Bucket'] = approach_df['Starting Distance'].apply(approach_bucket)

    # Assign table buckets
    approach_df['Table Bucket'] = approach_df.apply(approach_bucket_table, axis=1)

    # ------------------------------------------------------------
    # HERO CARDS
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Approach Performance by Distance</p>', unsafe_allow_html=True)

    hero_buckets = ["50–100", "100–150", "150–200", ">200"]
    cols = st.columns(4)

    for col, bucket in zip(cols, hero_buckets):
        bucket_df = approach_df[approach_df['Hero Bucket'] == bucket]

        total_sg = bucket_df['Strokes Gained'].sum() if len(bucket_df) > 0 else 0
        sg_per_shot = bucket_df['Strokes Gained'].mean() if len(bucket_df) > 0 else 0
        prox = bucket_df['Ending Distance'].mean() if len(bucket_df) > 0 else 0

        val_class = "positive" if total_sg > 0 else "negative" if total_sg < 0 else ""

        with col:
            st.markdown(f"""
                <div class="hero-stat">
                    <div class="hero-value {val_class}">{total_sg:.2f}</div>
                    <div class="hero-label">{bucket} Yards</div>
                    <div class="hero-sub">SG/Shot: {sg_per_shot:.3f}</div>
                    <div class="hero-sub">Proximity: {prox:.1f} ft</div>
                </div>
            """, unsafe_allow_html=True)

    # ------------------------------------------------------------
    # BUILD DISTANCE BUCKET TABLE (needed for radars + expander)
    # ------------------------------------------------------------
    table_buckets = ["50–100", "100–150", "150–200", ">200", "Rough <150", "Rough >150"]

    rows = []
    for bucket in table_buckets:
        dfb = approach_df[approach_df['Table Bucket'] == bucket]

        if len(dfb) == 0:
            rows.append([bucket, 0, 0, 0, 0, 0, 0, 0, 0])
            continue

        total_sg = dfb['Strokes Gained'].sum()
        shots = len(dfb)
        sg_per_shot = dfb['Strokes Gained'].mean()
        prox = dfb['Ending Distance'].mean()

        green_df = dfb[dfb['Ending Location'] == 'Green']
        prox_green = green_df['Ending Distance'].mean() if len(green_df) > 0 else 0
        gir = len(green_df) / shots * 100

        good = (dfb['Strokes Gained'] > 0.5).sum()
        bad = (dfb['Strokes Gained'] < -0.5).sum()

        rows.append([
            bucket, total_sg, shots, sg_per_shot, prox, prox_green, gir, good, bad
        ])

    bucket_table = pd.DataFrame(rows, columns=[
        "Bucket", "Total SG", "# Shots", "SG/Shot", "Proximity (ft)",
        "Prox on Green Hit (ft)", "GIR %", "Good Shots", "Bad Shots"
    ])

    # ------------------------------------------------------------
    # RADAR CHARTS (SG/Shot, Proximity, GIR%)
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Approach Profile by Distance Bucket</p>', unsafe_allow_html=True)

    radar_buckets = ["50–100", "100–150", "150–200", ">200", "Rough <150", "Rough >150"]

    radar_rows = []
    for bucket in radar_buckets:
        dfb = approach_df[approach_df['Table Bucket'] == bucket]

        if len(dfb) == 0:
            radar_rows.append([bucket, 0, 0, 0])
            continue

        sg_per_shot = dfb['Strokes Gained'].mean()
        prox = dfb['Ending Distance'].mean()
        gir = (dfb['Ending Location'] == 'Green').mean() * 100

        radar_rows.append([bucket, sg_per_shot, prox, gir])

    radar_df = pd.DataFrame(radar_rows, columns=["Bucket", "SG/Shot", "Proximity", "GIR%"])

    # Fixed scales
    sg_min, sg_max = -0.5, 0.5
    prox_min, prox_max = 0, 45
    gir_min, gir_max = 0, 100

    col1, col2, col3 = st.columns(3)

    # Radar 1 — SG per Shot
    with col1:
        fig_radar_sg = px.line_polar(
            radar_df,
            r="SG/Shot",
            theta="Bucket",
            line_close=True,
            range_r=[sg_min, sg_max],
            title="SG per Shot",
            color_discrete_sequence=[ODU_GOLD]
        )
        fig_radar_sg.update_traces(fill='toself')

        fig_radar_sg.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(showgrid=True, gridcolor="#444", color="#FFC72C"),
                angularaxis=dict(showgrid=True, gridcolor="#444", color="#FFC72C")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            font_color="#FFC72C",
            height=350
        )

        fig_radar_sg.add_shape( type="circle", xref="paper", yref="paper", x0=0.48, x1=0.52, y0=0.48, y1=0.52, line=dict(color="#FFC72C", width=3) 
                              )

        st.plotly_chart(fig_radar_sg, use_container_width=True)

    # Radar 2 — Proximity
    with col2:
        # Invert proximity so closer = better (farther out on radar)
        radar_df["Proximity_Inverted"] = prox_max - radar_df["Proximity"]

        fig_radar_prox = px.line_polar(
            radar_df,
            r="Proximity_Inverted",
            theta="Bucket",
            line_close=True,
            range_r=[0, prox_max],   # 0 = worst, 60 = best (inverted)
            title="Proximity (Closer = Better)",
            color_discrete_sequence=[ODU_BLACK]
        )

        fig_radar_prox.update_traces(fill='toself')

        fig_radar_prox.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(showgrid=True, gridcolor="#444", color="#FFC72C"),
                angularaxis=dict(showgrid=True, gridcolor="#444", color="#FFC72C")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            font_color="#FFC72C",
            height=350
        )

        st.plotly_chart(fig_radar_prox, use_container_width=True)

    # Radar 3 — GIR %
    with col3:
        fig_radar_gir = px.line_polar(
            radar_df,
            r="GIR%",
            theta="Bucket",
            line_close=True,
            range_r=[gir_min, gir_max],
            title="GIR %",
            color_discrete_sequence=[ODU_GREEN]
        )
        fig_radar_gir.update_traces(fill='toself')

        fig_radar_gir.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(showgrid=True, gridcolor="#444", color="#FFC72C"),
                angularaxis=dict(showgrid=True, gridcolor="#444", color="#FFC72C")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            font_color="#FFC72C",
            height=350
        )

        st.plotly_chart(fig_radar_gir, use_container_width=True)

    # Collapsible table
    with st.expander("View Full Distance Bucket Table"):
        st.dataframe(bucket_table, use_container_width=True, hide_index=True)

    # ------------------------------------------------------------
    # SCATTER PLOT
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">SG vs Starting Distance</p>', unsafe_allow_html=True)

    fig_scatter = px.scatter(
        approach_df,
        x="Starting Distance",
        y="Strokes Gained",
        color="Starting Location",
        hover_data=["Ending Distance", "Ending Location"],
        color_discrete_map={
            "Fairway": ODU_GOLD,
            "Rough": ODU_RED,
            "Sand": ODU_PURPLE,
            "Tee": ODU_BLACK
        }
    )

    fig_scatter.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Inter',
        height=400
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    # ------------------------------------------------------------
    # BOXPLOT
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Proximity by Distance Bucket</p>', unsafe_allow_html=True)

    fig_box = px.box(
        approach_df.dropna(subset=['Hero Bucket']),
        x="Hero Bucket",
        y="Ending Distance",
        color="Starting Location",
        color_discrete_map={
            "Fairway": ODU_GOLD,
            "Rough": ODU_RED,
            "Sand": ODU_PURPLE,
            "Tee": ODU_BLACK
        }
    )

    fig_box.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Inter',
        height=400
    )

    st.plotly_chart(fig_box, use_container_width=True)

    # ------------------------------------------------------------
    # HEATMAP (Ordered Axes)
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">SG per Shot Heatmap</p>', unsafe_allow_html=True)

    bucket_order = [">200", "150–200", "100–150", "50–100"]
    lie_order = ["Tee", "Fairway", "Rough", "Sand"]

    heat_df = approach_df.dropna(subset=['Hero Bucket']).copy()
    heat_df['Lie'] = heat_df['Starting Location']

    heat_df['Hero Bucket'] = pd.Categorical(heat_df['Hero Bucket'], categories=bucket_order, ordered=True)
    heat_df['Lie'] = pd.Categorical(heat_df['Lie'], categories=lie_order, ordered=True)

    heatmap_data = heat_df.groupby(['Hero Bucket', 'Lie'])['Strokes Gained'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Hero Bucket', columns='Lie', values='Strokes Gained')

    fig_heat = px.imshow(
        heatmap_pivot.loc[bucket_order, lie_order],
        color_continuous_scale='RdYlGn',
        aspect='auto'
    )

    fig_heat.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Inter',
        height=400
    )

    st.plotly_chart(fig_heat, use_container_width=True)

    # ------------------------------------------------------------
    # APPROACH TREND ANALYSIS
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Approach SG Trend by Round</p>', unsafe_allow_html=True)

    round_labels = filtered_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    round_labels['Label'] = round_labels.apply(
        lambda r: f"{pd.to_datetime(r['Date']).strftime('%m/%d/%Y')} {r['Course']}",
        axis=1
    )

    sg_round = approach_df.groupby('Round ID')['Strokes Gained'].sum().reset_index()
    sg_round = sg_round.merge(round_labels[['Round ID', 'Label', 'Date']], on='Round ID')
    sg_round = sg_round.sort_values('Date')

    use_ma = st.checkbox("Apply Moving Average", value=False)

    if use_ma:
        window = st.selectbox("Moving Average Window", [3, 5, 10], index=0)
        sg_round['SG_MA'] = sg_round['Strokes Gained'].rolling(window=window).mean()
        y_col = 'SG_MA'
    else:
        y_col = 'Strokes Gained'

    fig_trend = px.line(
        sg_round,
        x='Label',
        y=y_col,
        markers=True,
        title="SG: Approach Trend",
        color_discrete_sequence=[ODU_BLACK]
    )

    fig_trend.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Inter',
        xaxis_title='',
        yaxis_title='Strokes Gained',
        height=400
    )

    fig_trend.update_xaxes(tickangle=-45)

    st.plotly_chart(fig_trend, use_container_width=True)

# ============================================================
# TAB: SHORT GAME
# ============================================================
with tab_short_game:
    st.markdown('<p class="section-title">Short Game Analysis</p>', unsafe_allow_html=True)
    st.info("⛳ Short game analysis coming soon! This will include up-and-down %, sand save %, and proximity from various lies.")
    
    sg_shots = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()
    if len(sg_shots) > 0:
        sg_total = sg_shots['Strokes Gained'].sum()
        st.metric("Total SG Short Game", f"{sg_total:.2f}")
        
        with st.expander(f"View Short Game Shots ({len(sg_shots)} total)"):
            sg_detail = sg_shots[['Player', 'Date', 'Course', 'Hole', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']].copy()
            sg_detail['Date'] = pd.to_datetime(sg_detail['Date']).dt.strftime('%m/%d/%Y')
            sg_detail.columns = ['Player', 'Date', 'Course', 'Hole', 'Start Dist', 'Start Lie', 'End Dist', 'End Lie', 'SG']
            sg_detail['Hole'] = sg_detail['Hole'].astype(int)
            sg_detail['Start Dist'] = sg_detail['Start Dist'].round(0).astype(int)
            sg_detail['End Dist'] = sg_detail['End Dist'].round(0).astype(int)
            sg_detail['SG'] = sg_detail['SG'].round(2)
            st.dataframe(sg_detail, use_container_width=True, hide_index=True)

# ============================================================
# TAB: PUTTING
# ============================================================
with tab_putting:
    st.markdown('<p class="section-title">Putting Analysis</p>', unsafe_allow_html=True)
    st.info("🕳️ Putting analysis coming soon! This will include make % by distance, 3-putt avoidance, and putt length after approach.")
    
    putt_shots = filtered_df[filtered_df['Shot Type'] == 'Putt'].copy()
    if len(putt_shots) > 0:
        putt_sg = putt_shots['Strokes Gained'].sum()
        st.metric("Total SG Putting", f"{putt_sg:.2f}")
        
        with st.expander(f"View All Putts ({len(putt_shots)} total)"):
            putt_detail = putt_shots[['Player', 'Date', 'Course', 'Hole', 'Starting Distance', 'Ending Distance', 'Strokes Gained']].copy()
            putt_detail['Date'] = pd.to_datetime(putt_detail['Date']).dt.strftime('%m/%d/%Y')
            putt_detail.columns = ['Player', 'Date', 'Course', 'Hole', 'Start (ft)', 'End (ft)', 'SG']
            putt_detail['Hole'] = putt_detail['Hole'].astype(int)
            putt_detail['Start (ft)'] = putt_detail['Start (ft)'].round(0).astype(int)
            putt_detail['End (ft)'] = putt_detail['End (ft)'].round(0).astype(int)
            putt_detail['SG'] = putt_detail['SG'].round(2)
            st.dataframe(putt_detail, use_container_width=True, hide_index=True)
