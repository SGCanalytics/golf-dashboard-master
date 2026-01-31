import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIG & BRANDING
# ============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="ODU Golf Command Center", layout="wide")

ODU_GOLD, ODU_BLACK, ODU_RED = '#FFC72C', '#000000', '#E03C31'
ODU_METALLIC_GOLD, ODU_GRAY = '#D3AF7E', '#f4f4f4'

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@700&family=Roboto:wght@400;700&display=swap');
    .stApp { background-color: #ffffff; }
    .main-title { font-family: 'Roboto Slab', serif; font-size: 2.5rem; border-bottom: 5px solid #FFC72C; padding-bottom: 10px; margin-bottom: 25px; }
    .section-header { font-family: 'Roboto Slab', serif; font-size: 1.4rem; border-left: 6px solid #FFC72C; padding-left: 15px; margin: 40px 0 20px 0; background-color: #f8f9fa; line-height: 2; }
    
    /* Metrics Styling */
    .metric-container { background-color: #000000; color: #FFC72C; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #ddd; }
    .metric-label { font-size: 0.9rem; font-weight: 400; opacity: 0.8; }
    .metric-value { font-size: 2rem; font-family: 'Roboto Slab', serif; font-weight: 700; }

    /* Tiger 5 Styling */
    .tiger5-card { border-radius: 10px; padding: 15px; text-align: center; height: 140px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .t5-success { background: #000000; color: #FFC72C; border: 2px solid #FFC72C; }
    .t5-fail { background: #E03C31; color: white; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA ENGINE
# ============================================================
@st.cache_data(ttl=60)
def load_and_clean_data():
    data = pd.read_csv(SHEET_URL)
    data['Player'] = data['Player'].fillna('Unknown').str.strip().str.title()
    data['Date'] = pd.to_datetime(data['Date'])
    
    # Par Logic
    first_shots = data[data['Shot'] == 1].copy()
    first_shots['Par'] = first_shots['Starting Distance'].apply(lambda d: 3 if d <= 245 else (4 if d <= 475 else 5))
    data = data.merge(first_shots[['Round ID', 'Hole', 'Par']], on=['Round ID', 'Hole'], how='left')
    
    # Shot Type Classification
    def get_shot_type(row):
        loc, dist, p = row['Starting Location'], row['Starting Distance'], row['Par']
        if loc == 'Green': return 'Putt'
        if loc == 'Tee': return 'Approach' if p == 3 else 'Driving'
        if loc == 'Recovery': return 'Recovery'
        return 'Short Game' if dist < 50 else 'Approach'

    data['Shot Type'] = data.apply(get_shot_type, axis=1)
    return data

# ============================================================
# LOGIC & CALCULATIONS
# ============================================================
df = load_and_clean_data()

# Sidebar
st.sidebar.title("ODU Filters")
players = st.sidebar.multiselect("Players", sorted(df['Player'].unique()), df['Player'].unique())
f_df = df[df['Player'].isin(players)]

# Grouped Summary
h_sum = f_df.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']).agg(
    num_shots=('Shot', 'count'),
    num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
    num_putts=('Shot Type', lambda x: (x == 'Putt').sum())
).reset_index()
h_sum['Hole Score'] = h_sum['num_shots'] + h_sum['num_penalties']

# Score Mapping
def get_score_name(row):
    diff = row['Hole Score'] - row['Par']
    if diff <= -2: return 'Eagle'
    if diff == -1: return 'Birdie'
    if diff == 0: return 'Par'
    if diff == 1: return 'Bogey'
    return 'Double Bogey +'

h_sum['Score Name'] = h_sum.apply(get_score_name, axis=1)

# Tiger 5
t5_stats = {
    '3 Putts': (h_sum['num_putts'] >= 3).sum(),
    'Double Bogeys': (h_sum['Hole Score'] >= h_sum['Par'] + 2).sum(),
    'Bogey on Par 5': ((h_sum['Par'] == 5) & (h_sum['Hole Score'] >= 6)).sum(),
    'Missed Chip/Pitch': f_df[(f_df['Shot Type'] == 'Short Game') & (f_df['Ending Location'] != 'Green')].groupby(['Round ID', 'Hole']).size().count()
}

# Contribution Logic
type_totals = f_df.groupby('Shot Type')['Strokes Gained'].sum().to_dict()
f_df['Type Contribution %'] = f_df.apply(lambda r: (r['Strokes Gained'] / type_totals[r['Shot Type']] * 100) if type_totals.get(r['Shot Type'], 0) != 0 else 0, axis=1)

# ============================================================
# UI RENDERING
# ============================================================
st.markdown('<h1 class="main-title">ODU Golf Command Center</h1>', unsafe_allow_html=True)

# 1. TIGER 5 DISCIPLINE
st.markdown('<p class="section-header">1. Tiger 5 Discipline</p>', unsafe_allow_html=True)
t_cols = st.columns(5)
for i, (name, val) in enumerate(t5_stats.items()):
    cls = "t5-fail" if val > 0 else "t5-success"
    t_cols[i].markdown(f'<div class="tiger5-card {cls}"><h3>{name}</h3><div style="font-size:2.2rem; font-weight:700;">{int(val)}</div></div>', unsafe_allow_html=True)

with st.expander("🔍 View All Shots for Tiger 5 Failures"):
    fail_mask = (h_sum['num_putts'] >= 3) | (h_sum['Hole Score'] >= h_sum['Par'] + 2) | ((h_sum['Par'] == 5) & (h_sum['Hole Score'] >= 6))
    failed_holes = h_sum[fail_mask]
    
    for idx, row in failed_holes.iterrows():
        st.write(f"**{row['Course']} - Hole {row['Hole']} (Par {row['Par']})** | Score: {row['Hole Score']} | Putts: {row['num_putts']}")
        hole_shots = f_df[(f_df['Round ID'] == row['Round ID']) & (f_df['Hole'] == row['Hole'])]
        st.dataframe(hole_shots[['Shot', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']], hide_index=True)

# 2. APPEALING SG METRICS
st.markdown('<p class="section-header">2. Strokes Gained Performance</p>', unsafe_allow_html=True)
m_cols = st.columns(4)
metrics = [
    ("Total SG", f_df['Strokes Gained'].sum()),
    ("Tee to Green", f_df[f_df['Starting Location'] != 'Green']['Strokes Gained'].sum()),
    ("Putting", f_df[f_df['Shot Type'] == 'Putt']['Strokes Gained'].sum()),
    ("4-10ft Putts", f_df[(f_df['Shot Type'] == 'Putt') & (f_df['Starting Distance'].between(4, 10))]['Strokes Gained'].sum())
]

for i, (label, val) in enumerate(metrics):
    with m_cols[i]:
        st.markdown(f"""<div class="metric-container"><div class="metric-label">{label}</div><div class="metric-value">{val:.2f}</div></div>""", unsafe_allow_html=True)

# 3. ADVANCED SHOT LOGS
st.markdown('<p class="section-header">3. Detailed Shot Logs</p>', unsafe_allow_html=True)
for stype in ['Driving', 'Approach', 'Short Game', 'Putt']:
    subset = f_df[f_df['Shot Type'] == stype]
    if not subset.empty:
        with st.expander(f"📂 {stype} Logs ({len(subset)} shots)"):
            display_cols = ['Course', 'Hole', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained', 'Type Contribution %']
            st.dataframe(subset[display_cols].style.format({'Strokes Gained': '{:.2f}', 'Type Contribution %': '{:.1f}%'}), use_container_width=True, hide_index=True)

# 4. SCORING DISTRIBUTION
st.markdown('<p class="section-header">4. Scoring Distribution</p>', unsafe_allow_html=True)
c_pie, c_avg = st.columns(2)

with c_pie:
    order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double Bogey +']
    dist = h_sum['Score Name'].value_counts().reindex(order).fillna(0)
    fig_pie = px.pie(names=dist.index, values=dist.values, color=dist.index, 
                     color_discrete_map={'Eagle': '#753BBD', 'Birdie': ODU_GOLD, 'Par': ODU_METALLIC_GOLD, 'Bogey': ODU_BLACK, 'Double Bogey +': ODU_RED})
    st.plotly_chart(fig_pie, use_container_width=True)

with c_avg:
    avg_scores = h_sum.groupby('Par')['Hole Score'].mean().reset_index()
    fig_avg = px.bar(avg_scores, x='Par', y='Hole Score', text='Hole Score', title="Avg Score by Hole Par")
    fig_avg.update_traces(texttemplate='%{text:.2f}', textposition='outside', marker_color=ODU_GOLD)
    st.plotly_chart(fig_avg, use_container_width=True)
