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
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;700&family=Roboto:wght@400;700&display=swap');
    .stApp { background-color: #fcfcfc; }
    .main-title { font-family: 'Roboto Slab', serif; font-size: 2.2rem; font-weight: 700; border-bottom: 5px solid #FFC72C; margin-bottom: 25px; }
    .section-header { font-family: 'Roboto Slab', serif; font-size: 1.3rem; font-weight: 600; border-left: 5px solid #000000; padding-left: 12px; margin: 35px 0 15px 0; background-color: #f1f1f1; }
    
    .tiger5-card {
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        border-radius: 10px; padding: 10px; height: 135px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .t5-success { background: #000000; border: 3px solid #FFC72C; color: #FFC72C; }
    .t5-fail { background: #E03C31; border: 3px solid #E03C31; color: white; }
    .t5-title { font-family: 'Roboto Slab', serif; font-size: 0.8rem; font-weight: 600; margin-bottom: 5px; }
    .t5-value { font-family: 'Roboto Slab', serif; font-size: 2.2rem; font-weight: 700; line-height: 1; }
    
    [data-testid="stMetricValue"] { font-family: 'Roboto Slab', serif !important; font-size: 1.8rem !important; }
    [data-testid="stTable"] td { text-align: center !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA & LOGIC
# ============================================================
def determine_par(distance):
    if distance <= 245: return 3
    elif distance <= 475: return 4
    return 5

def determine_shot_type(start_loc, start_dist, par):
    if start_dist is None: return 'Other'
    if start_loc == 'Green': return 'Putt'
    if start_loc == 'Tee': return 'Approach' if par == 3 else 'Driving'
    if start_loc == 'Recovery': return 'Recovery'
    if start_dist < 50: return 'Short Game'
    if start_loc in ['Fairway', 'Rough', 'Sand'] and 50 <= start_dist <= 245: return 'Approach'
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
    res = {}
    res['3 Putts'] = {'fails': (hole_summary['num_putts'] >= 3).sum(), 'attempts': len(hole_summary)}
    res['Double Bogeys'] = {'fails': (hole_summary['Hole Score'] >= hole_summary['Par'] + 2).sum(), 'attempts': len(hole_summary)}
    
    p5 = hole_summary[hole_summary['Par'] == 5]
    res['Bogey on Par 5'] = {'fails': (p5['Hole Score'] >= 6).sum(), 'attempts': len(p5)}
    
    sg_shots = filtered_df[filtered_df['Shot Type'] == 'Short Game']
    sg_fails = sg_shots[sg_shots['Ending Location'] != 'Green'].groupby(['Round ID', 'Hole']).size().count()
    res['Missed Chip/Pitch'] = {'fails': sg_fails, 'attempts': sg_shots.groupby(['Round ID', 'Hole']).size().count()}
    
    app_125 = filtered_df[(filtered_df['Starting Distance'] <= 125) & (filtered_df['Shot Type'] == 'Approach')]
    app_125_merged = app_125.merge(hole_summary[['Round ID', 'Hole', 'Hole Score']], on=['Round ID', 'Hole'])
    app_125_fails = (app_125_merged['Hole Score'] > app_125_merged['Par']).sum()
    res['125yd Bogey'] = {'fails': app_125_fails, 'attempts': len(app_125_merged.drop_duplicates(['Round ID', 'Hole']))}

    total_att = sum(r['attempts'] for r in res.values())
    total_f = sum(r['fails'] for r in res.values())
    grit = (total_att - total_f) / total_att * 100 if total_att > 0 else 0
    return res, grit

# ============================================================
# PROCESSING
# ============================================================
df_raw = load_data()

st.sidebar.
