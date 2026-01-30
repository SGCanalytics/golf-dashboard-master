import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIG
# ============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="ODU Golf Shot Tracker", layout="wide")

# Shot type order
SHOT_TYPE_ORDER = ['Driving', 'Approach', 'Short Game', 'Putt', 'Recovery', 'Other']

# ODU Colors
ODU_GOLD = '#FFC72C'
ODU_BLACK = '#000000'
ODU_METALLIC_GOLD = '#D3AF7E'
ODU_DARK_GOLD = '#CC8A00'
ODU_RED = '#E03C31'
ODU_PURPLE = '#753BBD'
ODU_OLIVE = '#BBB323'

# ============================================================
# CUSTOM CSS - ODU BRANDING
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;600;700&family=Roboto:wght@400;500;600&display=swap');
    
    /* Main background */
    .stApp {
        background-color: #f8f8f8;
    }
    
    /* Headers - using Roboto Slab as Homestead alternative */
    h1, h2, h3 {
        font-family: 'Roboto Slab', serif !important;
        color: #000000 !important;
    }
    
    /* Body text */
    p, span, div, label {
        font-family: 'Roboto', 'Helvetica Neue', sans-serif;
    }
    
    /* Main title styling */
    .main-title {
        font-family: 'Roboto Slab', serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #000000;
        border-bottom: 4px solid #FFC72C;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Section headers */
    .section-header {
        font-family: 'Roboto Slab', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #000000;
        border-left: 4px solid #FFC72C;
        padding-left: 12px;
        margin: 30px 0 20px 0;
    }
    
    /* Center align dataframes */
    .stDataFrame {
        display: flex;
        justify-content: center;
    }
    .stDataFrame > div {
        text-align: center;
    }
    
    /* Tiger 5 cards - no fails (gold/black) */
    .tiger5-card {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        border: 3px solid #FFC72C;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        color: #FFC72C;
        height: 110px;
    }
    
    /* Tiger 5 cards - has fails (red accent) */
    .tiger5-card.has-fails {
        background: linear-gradient(135deg, #E03C31 0%, #c0322a 100%);
        border: 3px solid #E03C31;
        color: white;
    }
    
    .tiger5-card h3 {
        font-family: 'Roboto Slab', serif;
        font-size: 13px;
        margin: 0 0 8px 0;
        font-weight: 600;
    }
    .tiger5-card .fail-count {
        font-family: 'Roboto Slab', serif;
        font-size: 32px;
        font-weight: 700;
        margin: 0;
    }
    .tiger5-card .label {
        font-size: 11px;
        opacity: 0.9;
    }
    
    /* Grit score card (ODU gold) */
    .grit-card {
        background: linear-gradient(135deg, #FFC72C 0%, #CC8A00 100%);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        color: #000000;
        height: 110px;
    }
    .grit-card h3 {
        font-family: 'Roboto Slab', serif;
        font-size: 13px;
        margin: 0 0 8px 0;
        font-weight: 600;
    }
    .grit-card .score {
        font-family: 'Roboto Slab', serif;
        font-size: 32px;
        font-weight: 700;
        margin: 0;
    }
    .grit-card .label {
        font-size: 11px;
        opacity: 0.8;
    }
    
    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        font-family: 'Roboto Slab', serif !important;
        color: #000000 !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Roboto', sans-serif !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #000000;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #FFC72C !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-family: 'Roboto Slab', serif !important;
        background-color: #f0f0f0;
        border-left: 3px solid #FFC72C;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Roboto Slab', serif;
        color: #000000;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFC72C !important;
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
    
    # Tiger 5 #1: 3 Putts
    t5_3putt_attempts = (hole_summary['num_putts'] >= 1).sum()
    t5_3putt_fails = (hole_summary['num_putts'] >= 3).sum()
    three_putt_holes = hole_summary[hole_summary['num_putts'] >= 3][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['3 Putts'] = {'attempts': t5_3putt_attempts, 'fails': t5_3putt_fails, 'detail_holes': three_putt_holes}
    
    # Tiger 5 #2: Double Bogeys
    t5_dbl_bogey_attempts = len(hole_summary)
    dbl_bogey_mask = hole_summary['Hole Score'] >= hole_summary['Par'] + 2
    t5_dbl_bogey_fails = dbl_bogey_mask.sum()
    dbl_bogey_holes = hole_summary[dbl_bogey_mask][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['Double Bogeys'] = {'attempts': t5_dbl_bogey_attempts, 'fails': t5_dbl_bogey_fails, 'detail_holes': dbl_bogey_holes}
    
    # Tiger 5 #3: Bogey on Par 5
    par_5_holes = hole_summary[hole_summary['Par'] == 5]
    t5_bogey_par5_attempts = len(par_5_holes)
    bogey_par5_mask = par_5_holes['Hole Score'] >= 6
    t5_bogey_par5_fails = bogey_par5_mask.sum()
    bogey_par5_holes = par_5_holes[bogey_par5_mask][['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']].copy()
    results['Bogey on Par 5'] = {'attempts': t5_bogey_par5_attempts, 'fails': t5_bogey_par5_fails, 'detail_holes': bogey_par5_holes}
    
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
    results['Missed Chip/Pitch'] = {'attempts': t5_2shot_attempts, 'fails': t5_2shot_fails, 'detail_holes': missed_sg_holes}
    
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

hole_summary = build_hole_summary(filtered_df)
tiger5_results, total_tiger5_fails, grit_score = calculate_tiger5(filtered_df, hole_summary)

# ============================================================
# HEADER
# ============================================================
st.markdown('<h1 class="main-title">ODU Golf Shot Tracker</h1>', unsafe_allow_html=True)
st.markdown(f"**{len(filtered_df)}** shots from **{filtered_df['Round ID'].nunique()}** rounds")

# ============================================================
# TIGER 5 CARDS
# ============================================================
st.markdown('<p class="section-header">Tiger 5</p>', unsafe_allow_html=True)

tiger5_names = ['3 Putts', 'Double Bogeys', 'Bogey on Par 5', 'Missed Chip/Pitch', '125yd Bogey']

col1, col2, col3, col4, col5, col6 = st.columns(6)
cols = [col1, col2, col3, col4, col5, col6]

for i, stat_name in enumerate(tiger5_names):
    fails = tiger5_results[stat_name]['fails']
    card_class = "tiger5-card has-fails" if fails > 0 else "tiger5-card"
    with cols[i]:
        st.markdown(f"""
        <div class="{card_class}">
            <h3>{stat_name}</h3>
            <p class="fail-count">{int(fails)}</p>
            <p class="label">fails</p>
        </div>
        """, unsafe_allow_html=True)

with cols[5]:
    st.markdown(f"""
    <div class="grit-card">
        <h3>Grit Score</h3>
        <p class="score">{grit_score:.1f}%</p>
        <p class="label">success rate</p>
    </div>
    """, unsafe_allow_html=True)

# Tiger 5 Drill-Down
with st.expander("View Tiger 5 Fail Details"):
    for stat_name in tiger5_names:
        detail = tiger5_results[stat_name]
        fail_count = detail['fails']
        
        if fail_count > 0:
            st.markdown(f"### {stat_name} ({int(fail_count)} fails)")
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
                
                if stat_name == '3 Putts':
                    shots = filtered_df[
                        (filtered_df['Player'] == player) &
                        (filtered_df['Round ID'] == round_id) &
                        (filtered_df['Hole'] == hole) &
                        (filtered_df['Shot Type'] == 'Putt')
                    ][['Shot', 'Starting Distance', 'Ending Distance', 'Strokes Gained']].copy()
                    shots.columns = ['Putt #', 'Start (ft)', 'End (ft)', 'SG']
                elif stat_name == 'Missed Chip/Pitch':
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
# STROKES GAINED CARDS
# ============================================================
st.markdown('<p class="section-header">Strokes Gained Summary</p>', unsafe_allow_html=True)

num_rounds = filtered_df['Round ID'].nunique()
total_sg = filtered_df['Strokes Gained'].sum()
sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0
sg_driving = filtered_df[filtered_df['Shot Type'] == 'Driving']['Strokes Gained'].sum()
sg_approach = filtered_df[filtered_df['Shot Type'] == 'Approach']['Strokes Gained'].sum()

putts_5_10 = filtered_df[
    (filtered_df['Shot Type'] == 'Putt') &
    (filtered_df['Starting Distance'] >= 5) &
    (filtered_df['Starting Distance'] <= 10)
]
sg_putts_5_10 = putts_5_10['Strokes Gained'].sum()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total SG", f"{total_sg:.2f}")
with col2:
    st.metric("SG / Round", f"{sg_per_round:.2f}")
with col3:
    st.metric("SG Driving", f"{sg_driving:.2f}")
with col4:
    st.metric("SG Approach", f"{sg_approach:.2f}")
with col5:
    st.metric("SG Putts 5-10ft", f"{sg_putts_5_10:.2f}")

# ============================================================
# SG BY SHOT TYPE CHART
# ============================================================
st.markdown('<p class="section-header">Strokes Gained by Shot Type</p>', unsafe_allow_html=True)

sg_by_type = filtered_df.groupby('Shot Type')['Strokes Gained'].agg(
    Total_SG='sum',
    Num_Shots='count',
    SG_per_Shot='mean'
).reset_index()
sg_by_type.columns = ['Shot Type', 'Total SG', '# Shots', 'SG/Shot']
sg_by_type['Total SG'] = sg_by_type['Total SG'].round(2)
sg_by_type['SG/Shot'] = sg_by_type['SG/Shot'].round(3)

sg_by_type['Shot Type'] = pd.Categorical(sg_by_type['Shot Type'], categories=SHOT_TYPE_ORDER, ordered=True)
sg_by_type = sg_by_type.sort_values('Shot Type')

# ODU color scale: red (negative) -> metallic gold (zero) -> gold (positive)
fig_sg_type = px.bar(
    sg_by_type,
    x='Shot Type',
    y='Total SG',
    color='Total SG',
    color_continuous_scale=[ODU_RED, ODU_METALLIC_GOLD, ODU_GOLD],
    color_continuous_midpoint=0,
    text='Total SG'
)
fig_sg_type.update_traces(textposition='outside', texttemplate='%{text:.2f}')
fig_sg_type.update_layout(
    showlegend=False, 
    coloraxis_showscale=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family='Roboto'
)
fig_sg_type.add_hline(y=0, line_dash="dash", line_color=ODU_BLACK)
st.plotly_chart(fig_sg_type, use_container_width=True)

with st.expander("View Shot Type Details"):
    st.dataframe(sg_by_type, use_container_width=True, hide_index=True)

# ============================================================
# SG TREND BY DATE
# ============================================================
st.markdown('<p class="section-header">Strokes Gained Trend</p>', unsafe_allow_html=True)

sg_trend = filtered_df.groupby([filtered_df['Date'].dt.date, 'Shot Type'])['Strokes Gained'].sum().reset_index()
sg_trend.columns = ['Date', 'Shot Type', 'Total SG']
sg_trend['Shot Type'] = pd.Categorical(sg_trend['Shot Type'], categories=SHOT_TYPE_ORDER, ordered=True)

# ODU-themed line colors
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
    xaxis_title="Date",
    yaxis_title="Total Strokes Gained",
    hovermode="x unified",
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family='Roboto'
)
fig_trend.add_hline(y=0, line_dash="dash", line_color=ODU_BLACK)
st.plotly_chart(fig_trend, use_container_width=True)

# ============================================================
# SG BY STARTING LOCATION
# ============================================================
st.markdown('<p class="section-header">Strokes Gained by Starting Location</p>', unsafe_allow_html=True)

sg_by_lie = filtered_df.groupby('Starting Location')['Strokes Gained'].agg(
    Total_SG='sum',
    Num_Shots='count',
    SG_per_Shot='mean'
).reset_index()
sg_by_lie.columns = ['Starting Location', 'Total SG', '# Shots', 'SG/Shot']
sg_by_lie['Total SG'] = sg_by_lie['Total SG'].round(2)
sg_by_lie['SG/Shot'] = sg_by_lie['SG/Shot'].round(3)
sg_by_lie = sg_by_lie.sort_values('Total SG', ascending=False)

fig_sg_lie = px.bar(
    sg_by_lie,
    x='Starting Location',
    y='Total SG',
    color='Total SG',
    color_continuous_scale=[ODU_RED, ODU_METALLIC_GOLD, ODU_GOLD],
    color_continuous_midpoint=0,
    text='Total SG'
)
fig_sg_lie.update_traces(textposition='outside', texttemplate='%{text:.2f}')
fig_sg_lie.update_layout(
    showlegend=False, 
    coloraxis_showscale=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family='Roboto'
)
fig_sg_lie.add_hline(y=0, line_dash="dash", line_color=ODU_BLACK)
st.plotly_chart(fig_sg_lie, use_container_width=True)

with st.expander("View Starting Location Details"):
    st.dataframe(sg_by_lie, use_container_width=True, hide_index=True)

# ============================================================
# SCORING DISTRIBUTION
# ============================================================
st.markdown('<p class="section-header">Scoring Distribution</p>', unsafe_allow_html=True)

scoring_dist, scoring_pct = calculate_scoring_distribution(hole_summary)
score_order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double or Worse']

overall_dist = hole_summary['Score Name'].value_counts().reindex(score_order, fill_value=0)

# ODU-themed pie colors
fig_pie = px.pie(
    values=overall_dist.values,
    names=overall_dist.index,
    color=overall_dist.index,
    color_discrete_map={
        'Eagle': ODU_PURPLE,
        'Birdie': ODU_GOLD,
        'Par': ODU_METALLIC_GOLD,
        'Bogey': ODU_DARK_GOLD,
        'Double or Worse': ODU_RED
    }
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family='Roboto'
)
st.plotly_chart(fig_pie, use_container_width=True)

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    st.metric("Avg Score", f"{hole_summary['Hole Score'].mean():.2f}")
with col_s2:
    pars_or_better = (hole_summary['Hole Score'] <= hole_summary['Par']).sum()
    pars_or_better_pct = pars_or_better / len(hole_summary) * 100 if len(hole_summary) > 0 else 0
    st.metric("Pars or Better", f"{pars_or_better_pct:.1f}%")
with col_s3:
    st.metric("Total Holes", len(hole_summary))

with st.expander("View Scoring Distribution by Par"):
    tab1, tab2 = st.tabs(["Counts", "Percentages"])
    with tab1:
        st.dataframe(scoring_dist, use_container_width=True)
    with tab2:
        st.dataframe(scoring_pct[score_order], use_container_width=True)

# ============================================================
# RAW DATA
# ============================================================
with st.expander("View Raw Shot Data"):
    st.dataframe(filtered_df, use_container_width=True)

with st.expander("View Hole Summary"):
    st.dataframe(hole_summary, use_container_width=True)
