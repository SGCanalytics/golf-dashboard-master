import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIG & BRANDING
# ============================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="ODU Golf Command Center", layout="wide")

# ODU Brand Colors
ODU_GOLD, ODU_BLACK, ODU_RED = '#FFC72C', '#000000', '#E03C31'
ODU_METALLIC_GOLD, ODU_DARK_GOLD = '#D3AF7E', '#CC8A00'

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@700&family=Roboto:wght@400;700&display=swap');
    .stApp { background-color: #fcfcfc; }
    .main-title { font-family: 'Roboto Slab', serif; font-size: 2.2rem; font-weight: 700; border-bottom: 5px solid #FFC72C; padding-bottom: 10px; margin-bottom: 20px;}
    .section-header { font-family: 'Roboto Slab', serif; font-size: 1.3rem; font-weight: 600; border-left: 5px solid #000000; padding-left: 12px; margin: 30px 0 15px 0; background-color: #f1f1f1; }
    .tiger5-card {
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        border-radius: 10px; padding: 10px; height: 130px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .t5-success { background: #000000; border: 3px solid #FFC72C; color: #FFC72C; }
    .t5-fail { background: #E03C31; border: 3px solid #E03C31; color: white; }
    .t5-title { font-family: 'Roboto Slab', serif; font-size: 0.85rem; font-weight: 600; margin-bottom: 5px; }
    .t5-value { font-family: 'Roboto Slab', serif; font-size: 2.2rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA ENGINE
# ============================
@st.cache_data(ttl=60)
def load_and_clean_data():
    try:
        data = pd.read_csv(SHEET_URL)
        data['Player'] = data['Player'].fillna('Unknown').str.strip().str.title()
        data['Date'] = pd.to_datetime(data['Date'])
        
        # Calculate Par based on Shot 1
        first_shots = data[data['Shot'] == 1].copy()
        def get_par(dist):
            if dist <= 245: return 3
            if dist <= 475: return 4
            return 5
        first_shots['Par'] = first_shots['Starting Distance'].apply(get_par)
        
        # Merge Par back and determine Shot Type
        data = data.merge(first_shots[['Round ID', 'Hole', 'Par']], on=['Round ID', 'Hole'], how='left')
        
        def get_shot_type(row):
            loc, dist, p = row['Starting Location'], row['Starting Distance'], row['Par']
            if loc == 'Green': return 'Putt'
            if loc == 'Tee': return 'Approach' if p == 3 else 'Driving'
            if loc == 'Recovery': return 'Recovery'
            if dist < 50: return 'Short Game'
            return 'Approach'

        data['Shot Type'] = data.apply(get_shot_type, axis=1)
        return data
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame()

# ============================================================
# LOGIC & FILTERS
# ============================
df = load_and_clean_data()
if df.empty: st.stop()

# Sidebar
st.sidebar.title("ODU Filters")
players = st.sidebar.multiselect("Players", options=sorted(df['Player'].unique()), default=df['Player'].unique())
d_range = st.sidebar.date_input("Date Range", [df['Date'].min().date(), df['Date'].max().date()])

# Apply Filters
f_df = df[(df['Player'].isin(players)) & (df['Date'].dt.date >= d_range[0]) & (df['Date'].dt.date <= d_range[1])]

# Hole Summary
h_sum = f_df.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']).agg(
    num_shots=('Shot', 'count'),
    num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
    num_putts=('Shot Type', lambda x: (x == 'Putt').sum())
).reset_index()
h_sum['Hole Score'] = h_sum['num_shots'] + h_sum['num_penalties']

# Tiger 5 Calculations
t5_stats = {
    '3 Putts': (h_sum['num_putts'] >= 3).sum(),
    'Double Bogeys': (h_sum['Hole Score'] >= h_sum['Par'] + 2).sum(),
    'Bogey on Par 5': ((h_sum['Par'] == 5) & (h_sum['Hole Score'] >= 6)).sum(),
    'Missed Chip/Pitch': f_df[(f_df['Shot Type'] == 'Short Game') & (f_df['Ending Location'] != 'Green')].groupby(['Round ID', 'Hole']).size().count()
}

# 125yd Bogey logic
app_125 = f_df[(f_df['Starting Distance'] <= 125) & (f_df['Shot Type'] == 'Approach')].merge(h_sum[['Round ID', 'Hole', 'Hole Score']], on=['Round ID', 'Hole'])
t5_stats['125yd Bogey'] = (app_125['Hole Score'] > app_125['Par']).sum() if not app_125.empty else 0

total_f = sum(t5_stats.values())
grit = (1 - (total_f / (len(h_sum) * 5 if len(h_sum)>0 else 1))) * 100

# ============================================================
# DASHBOARD LAYOUT
# ============================
st.markdown('<h1 class="main-title">ODU Golf Command Center</h1>', unsafe_allow_html=True)

# 1. TIGER 5 (TOP)
st.markdown('<p class="section-header">Tiger 5 Discipline</p>', unsafe_allow_html=True)
t_cols = st.columns(6)
for i, (name, val) in enumerate(t5_stats.items()):
    cls = "t5-fail" if val > 0 else "t5-success"
    t_cols[i].markdown(f'<div class="tiger5-card {cls}"><div class="t5-title">{name}</div><div class="t5-value">{int(val)}</div></div>', unsafe_allow_html=True)
t_cols[5].markdown(f'<div class="tiger5-card" style="background:linear-gradient(135deg,#FFC72C,#CC8A00);color:black;"><div class="t5-title">Grit Index</div><div class="t5-value">{grit:.0f}%</div></div>', unsafe_allow_html=True)

with st.expander("🚨 View Tiger 5 Failure Details"):
    st.dataframe(h_sum[(h_sum['num_putts'] >= 3) | (h_sum['Hole Score'] >= h_sum['Par'] + 2)], hide_index=True, use_container_width=True)

# 2. KEY SG METRICS
st.markdown('<p class="section-header">Key SG Metrics</p>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total SG", f"{f_df['Strokes Gained'].sum():.2f}")
m2.metric("SG Tee to Green", f"{f_df[f_df['Starting Location'] != 'Green']['Strokes Gained'].sum():.2f}")
m3.metric("SG Putting", f"{f_df[f_df['Shot Type'] == 'Putt']['Strokes Gained'].sum():.2f}")
m4.metric("SG Putting (4-10ft)", f"{f_df[(f_df['Shot Type'] == 'Putt') & (f_df['Starting Distance'].between(4, 10))]['Strokes Gained'].sum():.2f}")

# 3. ANALYSIS & COLLAPSIBLE LOGS
st.markdown('<p class="section-header">Shot Type Performance</p>', unsafe_allow_html=True)
sg_stats = f_df.groupby('Shot Type')['Strokes Gained'].sum().reset_index()
c1, c2 = st.columns([2, 1])
with c1: st.plotly_chart(px.bar(sg_stats, x='Shot Type', y='Strokes Gained', color='Strokes Gained', color_continuous_scale='RdYlGn'), use_container_width=True)
with c2: st.table(sg_stats.set_index('Shot Type'))

st.write("### 📋 Shot Logs by Category")
for stype in ['Driving', 'Approach', 'Short Game', 'Putt']:
    subset = f_df[f_df['Shot Type'] == stype]
    if not subset.empty:
        with st.expander(f"{stype} Details ({len(subset)} shots)"):
            st.dataframe(subset[['Date', 'Hole', 'Starting Distance', 'Starting Location', 'Ending Location', 'Strokes Gained']], hide_index=True, use_container_width=True)

# 4. SCORING & STRATEGY
st.markdown('<p class="section-header">Scoring & Tee Shot Strategy</p>', unsafe_allow_html=True)
c3, c4 = st.columns(2)
with c3:
    st.write("### Scoring Distribution")
    h_sum['Res'] = h_sum.apply(lambda r: "Birdie+" if r['Hole Score'] < r['Par'] else ("Par" if r['Hole Score'] == r['Par'] else "Bogey+"), axis=1)
    st.plotly_chart(px.pie(h_sum, names='Res', color_discrete_sequence=[ODU_GOLD, ODU_BLACK, ODU_RED]), use_container_width=True)
with c4:
    st.write("### Avg Score on Par 4/5 by Tee Shot Outcome")
    tees = f_df[(f_df['Shot'] == 1) & (f_df['Par'].isin([4, 5]))].merge(h_sum[['Round ID', 'Hole', 'Hole Score']], on=['Round ID', 'Hole'])
    if not tees.empty:
        strat = tees.groupby('Ending Location')['Hole Score'].mean().reset_index()
        st.plotly_chart(px.bar(strat, x='Ending Location', y='Hole Score', color='Hole Score', color_continuous_scale='RdYlGn_r'), use_container_width=True)
    else:
        st.info("No Par 4/5 tee data found for this selection.")
