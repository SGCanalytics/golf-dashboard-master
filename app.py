import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIG & BRANDING
# ============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="ODU Golf Shot Tracker", layout="wide")

SHOT_TYPE_ORDER = ['Driving', 'Approach', 'Short Game', 'Putt', 'Recovery', 'Other']
ODU_GOLD, ODU_BLACK, ODU_METALLIC_GOLD, ODU_RED = '#FFC72C', '#000000', '#D3AF7E', '#E03C31'

# ============================================================
# REFINED CSS - FIXED ALIGNMENT
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;700&family=Roboto:wght@400;700&display=swap');
    .stApp { background-color: #fcfcfc; }
    .main-title { font-family: 'Roboto Slab', serif; font-size: 2.2rem; font-weight: 700; border-bottom: 5px solid #FFC72C; margin-bottom: 25px; }
    .section-header { font-family: 'Roboto Slab', serif; font-size: 1.3rem; font-weight: 600; border-left: 5px solid #000000; padding-left: 12px; margin: 35px 0 15px 0; background-color: #f1f1f1; }
    
    /* Center Aligned Tiger 5 Cards */
    .tiger5-card {
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        border-radius: 10px; padding: 10px; height: 135px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .t5-success { background: #000000; border: 3px solid #FFC72C; color: #FFC72C; }
    .t5-fail { background: #E03C31; border: 3px solid #E03C31; color: white; }
    .t5-title { font-family: 'Roboto Slab', serif; font-size: 0.8rem; font-weight: 600; margin-bottom: 5px; }
    .t5-value { font-family: 'Roboto Slab', serif; font-size: 2.2rem; font-weight: 700; line-height: 1; }
    .t5-label { font-size: 0.7rem; opacity: 0.8; text-transform: uppercase; }

    /* Centering Dataframes and Tables */
    .stDataFrame, [data-testid="stTable"], .centered-table { 
        margin: auto; 
        display: flex; 
        justify-content: center; 
    }
    
    /* Ensure table text is centered */
    [data-testid="stTable"] td { text-align: center !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOGIC FUNCTIONS
# ============================================================
def determine_par(distance):
    if distance <= 245: return 3
    elif distance <= 475: return 4
    return 5

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
    return 'Double or Worse'

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df['Player'] = df['Player'].str.strip().str.title()
    df['Date'] = pd.to_datetime(df['Date'])
    first_shots = df[df['Shot'] == 1].copy()
    first_shots['Par'] = first_shots['Starting Distance'].apply(determine_par)
    df = df.merge(first_shots[['Round ID', 'Hole', 'Par']], on=['Round ID', 'Hole'], how='left')
    df['Shot Type'] = df.apply(lambda r: determine_shot_type(r['Starting Location'], r['Starting Distance'], r['Par']), axis=1)
    return df

def build_hole_summary(df):
    summary = df.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']).agg(
        num_shots=('Shot', 'count'),
        num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
        num_putts=('Shot Type', lambda x: (x == 'Putt').sum())
    ).reset_index()
    summary['Hole Score'] = summary['num_shots'] + summary['num_penalties']
    summary['Score Name'] = summary.apply(lambda r: score_to_name(r['Hole Score'], r['Par']), axis=1)
    return summary

def calculate_tiger5(filtered_df, hole_summary):
    results = {}
    # 1. 3 Putts
    results['3 Putts'] = {'fails': (hole_summary['num_putts'] >= 3).sum(), 'attempts': len(hole_summary)}
    # 2. Double Bogeys
    results['Double Bogeys'] = {'fails': (hole_summary['Hole Score'] >= hole_summary['Par'] + 2).sum(), 'attempts': len(hole_summary)}
    # 3. Bogey on Par 5
    p5 = hole_summary[hole_summary['Par'] == 5]
    results['Bogey on Par 5'] = {'fails': (p5['Hole Score'] >= 6).sum(), 'attempts': len(p5)}
    # 4. Missed Chip/Pitch
    sg = filtered_df[filtered_df['Shot Type'] == 'Short Game']
    sg_fails = sg[sg['Ending Location'] != 'Green'].groupby(['Round ID', 'Hole']).size().count()
    results['Missed Chip/Pitch'] = {'fails': sg_fails, 'attempts': sg.groupby(['Round ID', 'Hole']).size().count()}
    # 5. 125yd Bogey (FIXED: removed Par from merge to avoid KeyError)
    app_125 = filtered_df[(filtered_df['Starting Distance'] <= 125) & (filtered_df['Shot Type'] == 'Approach')]
    app_125_merged = app_125.merge(hole_summary[['Round ID', 'Hole', 'Hole Score']], on=['Round ID', 'Hole'])
    app_125_fails = (app_125_merged['Hole Score'] > app_125_merged['Par']).sum()
    results['125yd Bogey'] = {'fails': app_125_fails, 'attempts': len(app_125_merged.drop_duplicates(['Round ID', 'Hole']))}

    total_att = sum(r['attempts'] for r in results.values())
    total_f = sum(r['fails'] for r in results.values())
    grit = (total_att - total_f) / total_att * 100 if total_att > 0 else 0
    return results, grit

# ============================================================
# DATA EXECUTION
# ============================================================
df_raw = load_data()

# Sidebar
st.sidebar.title("ODU Golf Filters")
selected_players = st.sidebar.multiselect("Select Player(s)", options=sorted(df_raw['Player'].unique()), default=df_raw['Player'].unique())
date_range = st.sidebar.date_input("Date Range", value=(df_raw['Date'].min(), df_raw['Date'].max()))
benchmark = st.sidebar.selectbox("Goal Benchmark (SG/Round)", options=["PGA Tour (0.0)", "Scratch Golfer (-2.0)", "10 Handicap (-5.0)"])
benchmark_val = float(benchmark.split('(')[1].split(')')[0])

# Filter current view
filtered_df = df_raw[(df_raw['Player'].isin(selected_players)) & (df_raw['Date'].dt.date >= date_range[0]) & (df_raw['Date'].dt.date <= date_range[1])]
hole_summary = build_hole_summary(filtered_df)
tiger5_results, current_grit = calculate_tiger5(filtered_df, hole_summary)

# Baseline for Trend: Filter ALL data for only the SELECTED players
baseline_df = df_raw[df_raw['Player'].isin(selected_players)]
baseline_hole_summary = build_hole_summary(baseline_df)
_, baseline_grit = calculate_tiger5(baseline_df, baseline_hole_summary)

# ============================================================
# DASHBOARD UI
# ============================================================
st.markdown('<h1 class="main-title">ODU Golf Command Center</h1>', unsafe_allow_html=True)

# Main KPI Row
m1, m2, m3, m4 = st.columns(4)
total_sg = filtered_df['Strokes Gained'].sum()
num_rounds = filtered_df['Round ID'].nunique()
sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0

m1.metric("Grit Score", f"{current_grit:.1f}%", delta=f"{current_grit - baseline_grit:.1f}% vs Career Avg")
m2.metric("SG / Round", f"{sg_per_round:.2f}", delta=f"{sg_per_round - benchmark_val:.2f} vs Goal")
m3.metric("Total SG", f"{total_sg:.2f}")
m4.metric("Rounds Played", num_rounds)

# Tiger 5 Row
st.markdown('<p class="section-header">Tiger 5 Discipline</p>', unsafe_allow_html=True)
t_cols = st.columns(6)
for i, name in enumerate(['3 Putts', 'Double Bogeys', 'Bogey on Par 5', 'Missed Chip/Pitch', '125yd Bogey']):
    res = tiger5_results.get(name, {'fails': 0})
    card_style = "t5-fail" if res['fails'] > 0 else "t5-success"
    with t_cols[i]:
        st.markdown(f'<div class="tiger5-card {card_style}"><div class="t5-title">{name}</div><div class="t5-value">{int(res["fails"])}</div><div class="t5-label">Total Fails</div></div>', unsafe_allow_html=True)

with t_cols[5]:
    st.markdown(f'<div class="tiger5-card" style="background:linear-gradient(135deg,#FFC72C,#CC8A00);color:black;"><div class="t5-title">Success Rate</div><div class="t5-value">{current_grit:.0f}%</div><div class="t5-label">Grit Index</div></div>', unsafe_allow_html=True)

# Tabs for Analytics
tab_sg, tab_scoring, tab_raw = st.tabs(["📊 Strokes Gained Analysis", "🎯 Scoring Distribution", "📋 Raw Shot Logs"])

with tab_sg:
    sg_type = filtered_df.groupby('Shot Type')['Strokes Gained'].sum().reindex(SHOT_TYPE_ORDER).fillna(0).reset_index()
    fig_sg = px.bar(sg_type, x='Shot Type', y='Strokes Gained', color='Strokes Gained', 
                    color_continuous_scale=[ODU_RED, ODU_METALLIC_GOLD, ODU_GOLD], color_continuous_midpoint=0)
    
    # Add Goal Line (Estimated 1/4 of round goal per category)
    target_per_cat = benchmark_val / 4
    fig_sg.add_hline(y=target_per_cat, line_dash="dot", line_color="blue", annotation_text=f"Target: {target_per_cat:.2f}")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.plotly_chart(fig_sg, use_container_width=True)
    with c2:
        st.write("### Shot Type Performance")
        st.table(sg_type.set_index('Shot Type').style.format('{:.2f}'))

with tab_scoring:
    c1, c2 = st.columns(2)
    with c1:
        dist = hole_summary['Score Name'].value_counts()
        fig_pie = px.pie(names=dist.index, values=dist.values, color_discrete_sequence=[ODU_GOLD, ODU_BLACK, ODU_METALLIC_GOLD, ODU_RED])
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.write("### Scoring Averages by Par")
        avg_stats = hole_summary.groupby('Par')['Hole Score'].mean().reset_index()
        st.table(avg_stats.set_index('Par').style.format('{:.2f}'))

with tab_raw:
    with st.expander("Click to view full shot logs"):
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
