import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# 1. SETUP & BRANDING
# ============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="ODU Golf Command Center", layout="wide")

ODU_GOLD, ODU_BLACK, ODU_RED = '#FFC72C', '#000000', '#E03C31'

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
# 2. DATA LOAD (With Error Protection)
# ============================================================
@st.cache_data(ttl=60)
def load_and_clean_data():
    try:
        data = pd.read_csv(SHEET_URL)
        data['Player'] = data['Player'].fillna('Unknown').str.strip().str.title()
        data['Date'] = pd.to_datetime(data['Date'])
        
        # Basic Par Logic
        def get_par(dist):
            if dist <= 245: return 3
            if dist <= 475: return 4
            return 5

        # Create Par column based on Shot 1 distance
        first_shots = data[data['Shot'] == 1].copy()
        first_shots['Par'] = first_shots['Starting Distance'].apply(get_par)
        
        # Merge Par back to all rows
        data = data.merge(first_shots[['Round ID', 'Hole', 'Par']], on=['Round ID', 'Hole'], how='left')
        
        # Assign Shot Types
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
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# ============================================================
# 3. PROCESSING
# ============================================================
raw_data = load_and_clean_data()

if raw_data.empty:
    st.warning("No data found. Please check your Google Sheets link.")
    st.stop()

# Sidebar
st.sidebar.title("ODU Filters")
p_list = sorted(raw_data['Player'].unique())
sel_players = st.sidebar.multiselect("Players", options=p_list, default=p_list)
d_range = st.sidebar.date_input("Date Range", [raw_data['Date'].min().date(), raw_data['Date'].max().date()])

# Filtered Data
f_df = raw_data[(raw_data['Player'].isin(sel_players)) & 
                (raw_data['Date'].dt.date >= d_range[0]) & 
                (raw_data['Date'].dt.date <= d_range[1])]

# Hole Summary for Scoring
h_sum = f_df.groupby(['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']).agg(
    num_shots=('Shot', 'count'),
    num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
    num_putts=('Shot Type', lambda x: (x == 'Putt').sum())
).reset_index()
h_sum['Hole Score'] = h_sum['num_shots'] + h_sum['num_penalties']

# Tiger 5 Logic
t5_fails = {
    '3 Putts': (h_sum['num_putts'] >= 3).sum(),
    'Double Bogeys': (h_sum['Hole Score'] >= h_sum['Par'] + 2).sum(),
    'Bogey on Par 5': ((h_sum['Par'] == 5) & (h_sum['Hole Score'] >= 6)).sum(),
}
sg_only = f_df[f_df['Shot Type'] == 'Short Game']
t5_fails['Missed Chip/Pitch'] = sg_only[sg_only['Ending Location'] != 'Green'].groupby(['Round ID', 'Hole']).size().count()

# 125yd Bogey
app_125 = f_df[(f_df['Starting Distance'] <= 125) & (f_df['Shot Type'] == 'Approach')]
if not app_125.empty:
    app_125 = app_125.merge(h_sum[['Round ID', 'Hole', 'Hole Score']], on=['Round ID', 'Hole'])
    t5_fails['125yd Bogey'] = (app_125['Hole Score'] > app_125['Par']).sum()
else:
    t5_fails['125yd Bogey'] = 0

# Grit Score calculation
total_f = sum(t5_fails.values())
grit_score = (1 - (total_f / (len(h_sum) * 5 if len(h_sum)>0 else 1))) * 100

# ============================================================
# 4. RENDER DASHBOARD
# ============================================================
st.markdown('<h1 class="main-title">ODU Golf Command Center</h1>', unsafe_allow_html=True)

# T
