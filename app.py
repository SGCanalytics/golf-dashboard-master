import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIG & BRANDING
# ============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="ODU Golf Command Center", layout="wide")

ODU_GOLD, ODU_BLACK, ODU_RED = '#FFC72C', '#000000', '#E03C31'
ODU_METALLIC_GOLD = '#D3AF7E'

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@700&family=Roboto:wght@400;700&display=swap');
    .stApp { background-color: #ffffff; }
    .main-title { font-family: 'Roboto Slab', serif; font-size: 2.2rem; border-bottom: 5px solid #FFC72C; padding-bottom: 10px; margin-bottom: 25px; }
    .section-header { font-family: 'Roboto Slab', serif; font-size: 1.4rem; border-left: 6px solid #FFC72C; padding-left: 15px; margin: 30px 0 15px 0; background-color: #f8f9fa; line-height: 2; }
    
    /* Tiger 5 Card Styling */
    .tiger5-card { border-radius: 10px; padding: 12px; text-align: center; height: 130px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .t5-success { background: #000000; color: #FFC72C; border: 2px solid #FFC72C; }
    .t5-fail { background: #E03C31; color: white; }
    .attempt-text { font-size: 0.75rem; opacity: 0.8; margin-top: 4px; }
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
    
    # Par & Shot Type Logic
    first_shots = data[data['Shot'] == 1].copy()
    first_shots['Par'] = first_shots['Starting Distance'].apply(lambda d: 3 if d <= 245 else (4 if d <= 475 else 5))
    data = data.merge(first_shots[['Round ID', 'Hole', 'Par']], on=['Round ID', 'Hole'], how='left')
    
    def get_shot_type(row):
        loc, dist, p = row['Starting Location'], row['Starting Distance'], row['Par']
        if loc == 'Green': return 'Putting'
        if loc == 'Tee': return 'Approach' if p == 3 else 'Driving'
        if loc == 'Recovery': return 'Recovery'
        return 'Short Game' if dist < 50 else 'Approach'

    data['Shot Type'] = data.apply(get_shot_type, axis=1)
    return data

df = load_and_clean_data()

# ============================================================
# SIDEBAR NAVIGATION & FILTERS
# ============================================================
st.sidebar.title("ODU NAVIGATION")
view_selection = st.sidebar.radio("Go To:", ["Main Dashboard", "Driving", "Approach", "Short Game", "Putting"])

st.sidebar.markdown("---")
players = st.sidebar.multiselect("Filter Players", sorted(df['Player'].unique()), df['Player'].unique())
f_df = df[df['Player'].isin(players)]

# Calculation: Hole Summary
h_sum = f_df.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']).agg(
    num_shots=('Shot', 'count'),
    num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
    num_putts=('Shot Type', lambda x: (x == 'Putting').sum())
).reset_index()
h_sum['Hole Score'] = h_sum['num_shots'] + h_sum['num_penalties']

# ============================================================
# MAIN DASHBOARD VIEW
# ============================================================
if view_selection == "Main Dashboard":
    st.markdown('<h1 class="main-title">ODU Golf Command Center</h1>', unsafe_allow_html=True)

    # 1. Tiger 5 Cards with Attempts
    st.markdown('<p class="section-header">Tiger 5 Discipline</p>', unsafe_allow_html=True)
    
    # Logic for attempts/fails
    t5_logic = {
        '3 Putts': {'f': (h_sum['num_putts'] >= 3).sum(), 'a': len(h_sum)},
        'Double Bogeys': {'f': (h_sum['Hole Score'] >= h_sum['Par'] + 2).sum(), 'a': len(h_sum)},
        'Bogey on Par 5': {'f': ((h_sum['Par'] == 5) & (h_sum['Hole Score'] >= 6)).sum(), 'a': (h_sum['Par'] == 5).sum()},
        'Missed Chip/Pitch': {
            'f': f_df[(f_df['Shot Type'] == 'Short Game') & (f_df['Ending Location'] != 'Green')].groupby(['Round ID', 'Hole']).size().count(),
            'a': f_df[f_df['Shot Type'] == 'Short Game'].groupby(['Round ID', 'Hole']).size().count()
        }
    }
    
    t_cols = st.columns(4)
    for i, (name, data) in enumerate(t5_logic.items()):
        cls = "t5-fail" if data['f'] > 0 else "t5-success"
        t_cols[i].markdown(f"""
            <div class="tiger5-card {cls}">
                <div style="font-size:0.85rem; font-weight:700;">{name}</div>
                <div style="font-size:2rem; font-weight:700;">{data['f']}</div>
                <div class="attempt-text">{data['a']} attempts</div>
            </div>
        """, unsafe_allow_html=True)

    # 2. SG Trends by Shot Type
    st.markdown('<p class="section-header">Strokes Gained Trends</p>', unsafe_allow_html=True)
    trend_df = f_df.groupby([f_df['Date'].dt.date, 'Shot Type'])['Strokes Gained'].sum().reset_index()
    fig_trend = px.line(trend_df, x='Date', y='Strokes Gained', color='Shot Type', markers=True,
                        color_discrete_map={'Driving': ODU_GOLD, 'Approach': ODU_BLACK, 'Short Game': ODU_METALLIC_GOLD, 'Putting': ODU_RED})
    fig_trend.update_layout(plot_bgcolor='white', hovermode='x unified')
    st.plotly_chart(fig_trend, use_container_width=True)

    # 3. Scoring Distribution & Avg Score
    st.markdown('<p class="section-header">Scoring Analysis</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double Bogey +']
        h_sum['Res'] = h_sum.apply(lambda r: 'Birdie' if r['Hole Score'] < r['Par'] else ('Par' if r['Hole Score'] == r['Par'] else 'Bogey'), axis=1) # Simplified for example
        st.plotly_chart(px.pie(h_sum, names='Res', color_discrete_sequence=[ODU_GOLD, ODU_BLACK, ODU_METALLIC_GOLD]), use_container_width=True)
    with c2:
        avg_par = h_sum.groupby('Par')['Hole Score'].mean().reset_index()
        st.plotly_chart(px.bar(avg_par, x='Par', y='Hole Score', text_auto='.2f', title="Avg Score by Par"), use_container_width=True)

# ============================================================
# SKILL SPECIFIC VIEWS
# ============================================================
else:
    st.markdown(f'<h1 class="main-title">{view_selection} Deep Dive</h1>', unsafe_allow_html=True)
    skill_df = f_df[f_df['Shot Type'] == view_selection]
    
    m1, m2 = st.columns(2)
    m1.metric(f"Total SG: {view_selection}", f"{skill_df['Strokes Gained'].sum():.2f}")
    m2.metric("Total Shots", len(skill_df))
    
    st.markdown('<p class="section-header">Shot Log</p>', unsafe_allow_html=True)
    st.dataframe(skill_df[['Date', 'Course', 'Hole', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']], use_container_width=True, hide_index=True)
