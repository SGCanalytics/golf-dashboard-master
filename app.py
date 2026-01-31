import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# 1. SETUP & BRANDING
# ============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="ODU Golf Command Center", layout="wide")

ODU_GOLD, ODU_BLACK, ODU_RED = '#FFC72C', '#000000', '#E03C31'
ODU_METALLIC_GOLD, ODU_DARK_GOLD = '#D3AF7E', '#CC8A00'

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@700&family=Roboto:wght@400;700&display=swap');
    .stApp { background-color: #fcfcfc; }
    .main-title { font-family: 'Roboto Slab', serif; font-size: 2.2rem; font-weight: 700; border-bottom: 5px solid #FFC72C; padding-bottom: 10px; }
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
# 2. DATA LOAD & HELPER FUNCTIONS
# ============================================================
@st.cache_data(ttl=300)
def load_and_clean_data():
    data = pd.read_csv(SHEET_URL)
    data['Player'] = data['Player'].str.strip().str.title()
    data['Date'] = pd.to_datetime(data['Date'])
    
    # Determine Par and Shot Types
    def get_par(dist):
        if dist <= 245: return 3
        if dist <= 475: return 4
        return 5

    # Merge Par into all shots
    first_shots = data[data['Shot'] == 1].copy()
    first_shots['Par'] = first_shots['Starting Distance'].apply(get_par)
    data = data.merge(first_shots[['Round ID', 'Hole', 'Par']], on=['Round ID', 'Hole'], how='left')

    def get_shot_type(loc, dist, p):
        if loc == 'Green': return 'Putt'
        if loc == 'Tee': return 'Approach' if p == 3 else 'Driving'
        if loc == 'Recovery': return 'Recovery'
        if dist < 50: return 'Short Game'
        return 'Approach'

    data['Shot Type'] = data.apply(lambda r: get_shot_type(r['Starting Location'], r['Starting Distance'], r['Par']), axis=1)
    return data

def get_hole_summary(df):
    summary = df.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']).agg(
        num_shots=('Shot', 'count'),
        num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
        num_putts=('Shot Type', lambda x: (x == 'Putt').sum())
    ).reset_index()
    summary['Hole Score'] = summary['num_shots'] + summary['num_penalties']
    return summary

# ============================================================
# 3. FILTERS & CALCULATIONS
# ============================================================
raw_data = load_and_clean_data()
