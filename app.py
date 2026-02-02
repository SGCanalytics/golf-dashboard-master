# ============================================================
# DATA ENGINE — CLEAN, CONSOLIDATED, DEDUPED
# ============================================================

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
# HELPER FUNCTIONS — CLEANED & CONSOLIDATED
# ============================================================

def determine_par(distance):
    """Assign par based on starting distance of tee shot."""
    if distance <= 245:
        return 3
    elif distance <= 475:
        return 4
    return 5

def determine_shot_type(start_location, start_distance, par):
    """Unified shot type logic."""
    if start_distance is None:
        return 'Other'
    if start_location == 'Green':
        return 'Putt'
    if start_location == 'Tee':
        return 'Approach' if par == 3 else 'Driving'
    if start_location == 'Recovery':
        return 'Recovery'
    if start_distance < 50:
        return 'Short Game'
    if start_location in ['Fairway', 'Rough', 'Sand'] and 50 <= start_distance <= 245:
        return 'Approach'
    return 'Other'

def score_to_name(hole_score, par):
    """Convert numeric score vs par into a label."""
    diff = hole_score - par
    if diff <= -2:
        return 'Eagle'
    elif diff == -1:
        return 'Birdie'
    elif diff == 0:
        return 'Par'
    elif diff == 1:
        return 'Bogey'
    return 'Double or Worse'

def sg_value_class(val):
    """CSS class for SG color coding."""
    if val > 0:
        return "positive"
    elif val < 0:
        return "negative"
    return ""

def fmt_pct(count, total):
    """Format percentage safely."""
    return f"{count/total*100:.1f}%" if total > 0 else "-"

def fmt_pr(count, rounds):
    """Format per-round metric safely."""
    return f"{count/rounds:.1f}" if rounds > 0 else "-"

# ============================================================
# DISTANCE BUCKETS — UNIFIED
# ============================================================

def approach_bucket(distance):
    """Buckets for hero cards (all lies)."""
    if 50 <= distance < 100:
        return "50–100"
    elif 100 <= distance < 150:
        return "100–150"
    elif 150 <= distance < 200:
        return "150–200"
    elif distance >= 200:
        return ">200"
    return None

def approach_bucket_table(row):
    """Buckets for table (lie‑restricted)."""
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
        return "Rough <150" if d < 150 else "Rough >150"

    return None

# ============================================================
# DATA LOADING — CLEANED & CONSOLIDATED
# ============================================================

@st.cache_data(ttl=300)
def load_data():
    """Load, clean, and enrich the dataset."""
    df = pd.read_csv(SHEET_URL)

    # Clean strings
    df['Player'] = df['Player'].str.strip().str.title()
    df['Course'] = df['Course'].str.strip().str.title()
    df['Tournament'] = df['Tournament'].str.strip().str.title()

    # Compute par from first shot
    first_shots = df[df['Shot'] == 1].copy()
    first_shots['Par'] = first_shots['Starting Distance'].apply(determine_par)

    df = df.merge(
        first_shots[['Round ID', 'Hole', 'Par']],
        on=['Round ID', 'Hole'],
        how='left'
    )

    # Shot type
    df['Shot Type'] = df.apply(
        lambda row: determine_shot_type(
            row['Starting Location'],
            row['Starting Distance'],
            row['Par']
        ),
        axis=1
    )

    # Unique shot ID
    df['Shot ID'] = (
        df['Round ID'] +
        '-H' + df['Hole'].astype(str) +
        '-S' + df['Shot'].astype(str)
    )

    return df

# ============================================================
# HOLE SUMMARY ENGINE — CENTRALIZED
# ============================================================

def build_hole_summary(df):
    """Compute per-hole summary used across multiple tabs."""
    hole_summary = df.groupby(
        ['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']
    ).agg(
        num_shots=('Shot', 'count'),
        num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
        num_putts=('Shot Type', lambda x: (x == 'Putt').sum()),
        total_sg=('Strokes Gained', 'sum')
    ).reset_index()

    hole_summary['Hole Score'] = (
        hole_summary['num_shots'] + hole_summary['num_penalties']
    )

    hole_summary['Score Name'] = hole_summary.apply(
        lambda row: score_to_name(row['Hole Score'], row['Par']),
        axis=1
    )

    return hole_summary

# ============================================================
# TIGER 5 ENGINE — CENTRALIZED & REUSABLE
# ============================================================

def _tiger5_three_putts(hole_summary):
    """3 Putts: any hole with ≥3 putts."""
    attempts = (hole_summary['num_putts'] >= 1).sum()
    fails = (hole_summary['num_putts'] >= 3).sum()
    detail = hole_summary[hole_summary['num_putts'] >= 3][
        ['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']
    ].copy()
    return attempts, fails, detail

def _tiger5_double_bogey(hole_summary):
    """Double Bogey: score ≥ par + 2."""
    attempts = len(hole_summary)
    mask = hole_summary['Hole Score'] >= hole_summary['Par'] + 2
    fails = mask.sum()
    detail = hole_summary[mask][
        ['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']
    ].copy()
    return attempts, fails, detail

def _tiger5_par5_bogey(hole_summary):
    """Par 5 Bogey: par 5 holes with score ≥ 6."""
    par5 = hole_summary[hole_summary['Par'] == 5]
    attempts = len(par5)
    mask = par5['Hole Score'] >= 6
    fails = mask.sum()
    detail = par5[mask][
        ['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']
    ].copy()
    return attempts, fails, detail

def _tiger5_missed_green_short_game(df, hole_summary):
    """
    Missed Green: any short game shot (Shot Type == 'Short Game')
    that does NOT end on the green, counted per hole.
    """
    sg_shots = df[df['Shot Type'] == 'Short Game'].copy()
    if sg_shots.empty:
        return 0, 0, sg_shots

    sg_shots['missed_green'] = sg_shots['Ending Location'] != 'Green'
    by_hole = sg_shots.groupby(
        ['Player', 'Round ID', 'Date', 'Course', 'Hole']
    ).agg(
        any_missed=('missed_green', 'any')
    ).reset_index()

    attempts = len(by_hole)
    fails = by_hole['any_missed'].sum()
    detail = by_hole[by_hole['any_missed']][
        ['Player', 'Round ID', 'Date', 'Course', 'Hole']
    ].copy()

    if not detail.empty:
        detail = detail.merge(
            hole_summary[['Player', 'Round ID', 'Hole', 'Par', 'Hole Score']],
            on=['Player', 'Round ID', 'Hole'],
            how='left'
        )

    return attempts, fails, detail

def _tiger5_approach_125_bogey(df, hole_summary):
    """
    125yd Bogey:
    - Starting Distance <= 125
    - Not Recovery
    - 'Scoring shot' based on par:
        * Par 5: Shot 3
        * Par 4: Shot 2
        * Par 3: Shot 1
    - Fail if Hole Score > Par
    """
    cond = (
        (df['Starting Distance'] <= 125) &
        (df['Starting Location'] != 'Recovery') &
        (
            ((df['Shot'] == 3) & (df['Par'] == 5)) |
            ((df['Shot'] == 2) & (df['Par'] == 4)) |
            ((df['Shot'] == 1) & (df['Par'] == 3))
        )
    )

    candidates = df[cond][
        ['Player', 'Round ID', 'Date', 'Course', 'Hole']
    ].drop_duplicates()

    if candidates.empty:
        return 0, 0, candidates

    with_score = candidates.merge(
        hole_summary[['Player', 'Round ID', 'Hole', 'Hole Score', 'Par']],
        on=['Player', 'Round ID', 'Hole'],
        how='left'
    )

    attempts = len(with_score)
    mask = with_score['Hole Score'] > with_score['Par']
    fails = mask.sum()
    detail = with_score[mask].copy()

    return attempts, fails, detail

def calculate_tiger5(df, hole_summary):
    """
    Master Tiger 5 calculator.
    Returns:
        - results: dict of each Tiger 5 category with attempts, fails, detail_holes
        - total_fails: total Tiger 5 fails
        - grit_score: success rate %
    """
    results = {}

    # 3 Putts
    a_3p, f_3p, d_3p = _tiger5_three_putts(hole_summary)
    results['3 Putts'] = {
        'attempts': a_3p,
        'fails': f_3p,
        'detail_holes': d_3p
    }

    # Double Bogey
    a_db, f_db, d_db = _tiger5_double_bogey(hole_summary)
    results['Double Bogey'] = {
        'attempts': a_db,
        'fails': f_db,
        'detail_holes': d_db
    }

    # Par 5 Bogey
    a_p5, f_p5, d_p5 = _tiger5_par5_bogey(hole_summary)
    results['Par 5 Bogey'] = {
        'attempts': a_p5,
        'fails': f_p5,
        'detail_holes': d_p5
    }

    # Missed Green (Short Game)
    a_mg, f_mg, d_mg = _tiger5_missed_green_short_game(df, hole_summary)
    results['Missed Green'] = {
        'attempts': a_mg,
        'fails': f_mg,
        'detail_holes': d_mg
    }

    # 125yd Bogey
    a_125, f_125, d_125 = _tiger5_approach_125_bogey(df, hole_summary)
    results['125yd Bogey'] = {
        'attempts': a_125,
        'fails': f_125,
        'detail_holes': d_125
    }

    total_attempts = sum(r['attempts'] for r in results.values())
    total_fails = sum(r['fails'] for r in results.values())
    grit_score = (
        ((total_attempts - total_fails) / total_attempts * 100)
        if total_attempts > 0 else 0
    )

    return results, total_fails, grit_score

# ============================================================
# TIGER 5 BY ROUND — FOR TREND CHART
# ============================================================

def tiger5_by_round(df, hole_summary):
    """
    Build per-round Tiger 5 breakdown + total score.
    Returns a DataFrame with:
        Round ID, Label, Date,
        3 Putts, Double Bogey, Par 5 Bogey,
        Missed Green, 125yd Bogey,
        Total Score, Total Fails
    """
    round_info = df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    rows = []

    for _, r in round_info.iterrows():
        rid = r['Round ID']
        date_obj = pd.to_datetime(r['Date'])
        label = f"{date_obj.strftime('%m/%d/%Y')} {r['Course']}"

        round_df = df[df['Round ID'] == rid]
        round_holes = hole_summary[hole_summary['Round ID'] == rid]

        # Reuse the same Tiger 5 logic but scoped to this round
        a_3p, f_3p, _ = _tiger5_three_putts(round_holes)
        a_db, f_db, _ = _tiger5_double_bogey(round_holes)
        a_p5, f_p5, _ = _tiger5_par5_bogey(round_holes)
        a_mg, f_mg, _ = _tiger5_missed_green_short_game(round_df, round_holes)
        a_125, f_125, _ = _tiger5_approach_125_bogey(round_df, round_holes)

        total_score = round_holes['Hole Score'].sum()

        rows.append({
            'Round ID': rid,
            'Label': label,
            'Date': date_obj,
            '3 Putts': f_3p,
            'Double Bogey': f_db,
            'Par 5 Bogey': f_p5,
            'Missed Green': f_mg,
            '125yd Bogey': f_125,
            'Total Score': total_score
        })

    t5_df = pd.DataFrame(rows)
    if not t5_df.empty:
        t5_df = t5_df.sort_values('Date')
        t5_df['Total Fails'] = (
            t5_df['3 Putts'] +
            t5_df['Double Bogey'] +
            t5_df['Par 5 Bogey'] +
            t5_df['Missed Green'] +
            t5_df['125yd Bogey']
        )

    return t5_df

# ============================================================
# PUTTING ENGINE — CENTRALIZED, WITH FIXED TABLE LOGIC
# ============================================================

def build_putting_df(df):
    """
    Return a putting-only DataFrame with consistent, ready-to-use columns.
    Assumes:
        - Shot Type == 'Putt'
        - 'Score' represents number of putts on the hole context
          (used where you previously referenced 'Putts').
    """
    putting_df = df[df['Shot Type'] == 'Putt'].copy()

    # Ensure distances are numeric
    putting_df['Starting Distance'] = pd.to_numeric(
        putting_df['Starting Distance'], errors='coerce'
    )
    putting_df['Ending Distance'] = pd.to_numeric(
        putting_df['Ending Distance'], errors='coerce'
    )

    # Make flag: 1 if holed (Ending Distance == 0), else 0
    putting_df['Made'] = (putting_df['Ending Distance'] == 0).astype(int)

    # Hole-level identifier
    putting_df['Hole Key'] = (
        putting_df['Player'].astype(str) + '|' +
        putting_df['Round ID'].astype(str) + '|' +
        putting_df['Hole'].astype(str)
    )

    return putting_df


# ============================================================
# PUTTING SUMMARY METRICS
# ============================================================

def putting_hero_metrics(putting_df, num_rounds):
    """
    Compute high-level putting hero metrics:
        - Total SG Putting
        - Make % 4–5 ft
        - SG 5–10 ft
        - 3-Putts per round
        - Lag misses (e.g., >3 ft left after long putts) per round
    Returns a dict of metrics for easy card rendering.
    """
    metrics = {
        'total_sg_putting': 0.0,
        'make_pct_4_5': "-",
        'sg_5_10': 0.0,
        'three_putts_per_round': "-",
        'lag_misses_per_round': "-"
    }

    if putting_df.empty or num_rounds == 0:
        return metrics

    # Total SG Putting
    metrics['total_sg_putting'] = putting_df['Strokes Gained'].sum()

    # Make % 4–5 ft
    mask_4_5 = (putting_df['Starting Distance'] >= 4) & (putting_df['Starting Distance'] <= 5)
    subset_4_5 = putting_df[mask_4_5]
    if not subset_4_5.empty:
        attempts_4_5 = len(subset_4_5)
        makes_4_5 = subset_4_5['Made'].sum()
        metrics['make_pct_4_5'] = fmt_pct(makes_4_5, attempts_4_5)

    # SG 5–10 ft
    mask_5_10 = (putting_df['Starting Distance'] >= 5) & (putting_df['Starting Distance'] <= 10)
    subset_5_10 = putting_df[mask_5_10]
    if not subset_5_10.empty:
        metrics['sg_5_10'] = subset_5_10['Strokes Gained'].sum()

    # 3-Putts per round:
    # Count holes where number of putts (Score) >= 3
    # NOTE: this assumes 'Score' is the number of putts on that hole context.
    hole_putt_counts = putting_df.groupby('Hole Key').agg(
        putts=('Score', 'max')  # or 'sum' depending on how Score is stored
    ).reset_index()

    three_putt_holes = hole_putt_counts[hole_putt_counts['putts'] >= 3]
    metrics['three_putts_per_round'] = fmt_pr(len(three_putt_holes), num_rounds)

    # Lag misses per round:
    # Define "lag miss" as: starting distance >= 30 ft and ending distance > 3 ft
    lag_mask = (putting_df['Starting Distance'] >= 30) & (putting_df['Ending Distance'] > 3)
    lag_misses = putting_df[lag_mask]
    metrics['lag_misses_per_round'] = fmt_pr(len(lag_misses), num_rounds)

    return metrics


# ============================================================
# PUTTING MAKE % TABLES
# ============================================================

def putting_make_pct_by_distance(putting_df, bins=None, labels=None):
    """
    Build a make % table by distance buckets.
    bins: list of bucket edges in feet
    labels: list of labels for each bucket
    Returns a DataFrame with:
        - Distance Bucket
        - Attempts
        - Makes
        - Make %
    """
    if putting_df.empty:
        return pd.DataFrame(columns=['Distance Bucket', 'Attempts', 'Makes', 'Make %'])

    if bins is None:
        bins = [0, 3, 5, 8, 10, 15, 20, 30, 1000]
    if labels is None:
        labels = ['0–3', '3–5', '5–8', '8–10', '10–15', '15–20', '20–30', '30+']

    df = putting_df.copy()
    df['Distance Bucket'] = pd.cut(
        df['Starting Distance'],
        bins=bins,
        labels=labels,
        right=False
    )

    grouped = df.groupby('Distance Bucket').agg(
        Attempts=('Made', 'count'),
        Makes=('Made', 'sum')
    ).reset_index()

    grouped['Make %'] = grouped.apply(
        lambda row: fmt_pct(row['Makes'], row['Attempts']),
        axis=1
    )

    return grouped


# ============================================================
# PUTTING LAG SCATTER DATA
# ============================================================

def putting_lag_scatter_data(putting_df):
    """
    Prepare data for lag putting scatter:
        x = Starting Distance
        y = Ending Distance
        color = Strokes Gained or Made
    """
    if putting_df.empty:
        return putting_df

    # You can add any derived flags here if needed
    return putting_df[['Starting Distance', 'Ending Distance', 'Strokes Gained', 'Made']].copy()


# ============================================================
# PUTTING SG TREND BY ROUND
# ============================================================

def putting_sg_by_round(putting_df):
    """
    Compute SG Putting per round for trendline chart.
    Returns DataFrame with:
        Round ID, Date, Course, SG Putting
    """
    if putting_df.empty:
        return pd.DataFrame(columns=['Round ID', 'Date', 'Course', 'SG Putting'])

    grouped = putting_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        SG_Putting=('Strokes Gained', 'sum')
    ).reset_index()

    grouped['Date'] = pd.to_datetime(grouped['Date'])
    grouped = grouped.sort_values('Date')

    return grouped


# ============================================================
# PUTTING "CLUTCH INDEX" (EXAMPLE)
# ============================================================

def putting_clutch_index(putting_df):
    """
    Example clutch index:
        - Focus on putts inside 10 ft
        - Weight makes more when SG is high
    Returns a single float (can be scaled or normalized as desired).
    """
    if putting_df.empty:
        return 0.0

    close_putts = putting_df[putting_df['Starting Distance'] <= 10].copy()
    if close_putts.empty:
        return 0.0

    # Simple version: average SG on made putts inside 10 ft
    made_close = close_putts[close_putts['Made'] == 1]
    if made_close.empty:
        return 0.0

    clutch = made_close['Strokes Gained'].mean()
    return clutch

# ============================================================
# SEGMENT 4 — DRIVING / APPROACH / SHORT GAME ENGINES
# ============================================================

# ============================================================
# SEGMENT 4A — DRIVING + APPROACH ENGINE
# ============================================================

def driving_engine(filtered_df, num_rounds):
    """Compute all driving analytics for the Driving tab."""

    # Filter to driving shots
    df = filtered_df[filtered_df['Shot Type'] == 'Driving'].copy()
    num_drives = len(df)

    if num_drives == 0:
        return {"num_drives": 0}

    # -----------------------------
    # BASIC SG METRICS
    # -----------------------------
    driving_sg = df['Strokes Gained'].sum()
    driving_sg_per_round = driving_sg / num_rounds if num_rounds > 0 else 0

    # -----------------------------
    # ENDING LOCATION COUNTS
    # -----------------------------
    end_loc_counts = df['Ending Location'].value_counts()
    fairway = end_loc_counts.get('Fairway', 0)
    rough = end_loc_counts.get('Rough', 0)
    sand = end_loc_counts.get('Sand', 0)
    recovery = end_loc_counts.get('Recovery', 0)
    green = end_loc_counts.get('Green', 0)

    # -----------------------------
    # PENALTIES
    # -----------------------------
    penalty_count = len(df[df['Penalty'] == 'Yes'])

    # -----------------------------
    # OB DETECTION (RE-TEE)
    # -----------------------------
    ob_count = 0
    ob_details = []

    drive_holes = df[['Player', 'Round ID', 'Hole', 'Course', 'Date']].drop_duplicates()

    for _, row in drive_holes.iterrows():
        hole_shots = filtered_df[
            (filtered_df['Player'] == row['Player']) &
            (filtered_df['Round ID'] == row['Round ID']) &
            (filtered_df['Hole'] == row['Hole'])
        ].sort_values('Shot')

        # Re-tee detection
        if len(hole_shots) >= 2:
            if hole_shots.iloc[0]['Starting Location'] == 'Tee' and hole_shots.iloc[1]['Starting Location'] == 'Tee':
                ob_count += 1
                ob_details.append({
                    'Player': row['Player'],
                    'Date': row['Date'],
                    'Course': row['Course'],
                    'Hole': row['Hole']
                })

    # -----------------------------
    # RATES
    # -----------------------------
    obstruction_count = sand + recovery
    obstruction_pct = (obstruction_count / num_drives * 100) if num_drives > 0 else 0

    penalty_total = penalty_count + ob_count
    penalty_rate_pct = (penalty_total / num_drives * 100) if num_drives > 0 else 0

    fairway_pct = (fairway / num_drives * 100) if num_drives > 0 else 0

    # -----------------------------
    # SG BY RESULT
    # -----------------------------
    sg_by_result = (
        df.groupby('Ending Location')['Strokes Gained']
        .agg(['sum', 'count', 'mean'])
        .reset_index()
        .rename(columns={'sum': 'Total SG', 'count': 'Shots', 'mean': 'SG/Shot'})
    )

    # -----------------------------
    # TREND DATA
    # -----------------------------
    round_labels = df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    round_labels['Label'] = round_labels.apply(
        lambda r: f"{pd.to_datetime(r['Date']).strftime('%m/%d/%Y')} {r['Course']}",
        axis=1
    )

    trend = df.groupby('Round ID').agg(
        SG=('Strokes Gained', 'sum'),
        Drives=('Shot', 'count'),
        Fairways=('Ending Location', lambda x: (x == 'Fairway').sum())
    ).reset_index()

    trend = trend.merge(round_labels[['Round ID', 'Label', 'Date']], on='Round ID')
    trend = trend.sort_values('Date')
    trend['Fairway %'] = (trend['Fairways'] / trend['Drives'] * 100).round(1)

    # -----------------------------
    # RETURN EVERYTHING CLEANLY
    # -----------------------------
    return {
        "df": df,
        "num_drives": num_drives,
        "driving_sg": driving_sg,
        "driving_sg_per_round": driving_sg_per_round,

        "fairway": fairway,
        "rough": rough,
        "sand": sand,
        "recovery": recovery,
        "green": green,

        "fairway_pct": fairway_pct,
        "obstruction_count": obstruction_count,
        "obstruction_pct": obstruction_pct,

        "penalty_count": penalty_count,
        "ob_count": ob_count,
        "penalty_total": penalty_total,
        "penalty_rate_pct": penalty_rate_pct,

        "ob_details": ob_details,
        "sg_by_result": sg_by_result,
        "trend": trend,
    }

# ============================================================
# APPROACH ENGINE (Unified + UI-ready)
# ============================================================

def approach_engine(filtered_df):
    """Compute all approach analytics for the Approach tab."""

    # ------------------------------------------------------------
    # 1. Filter + Buckets
    # ------------------------------------------------------------
    df = filtered_df[filtered_df['Shot Type'] == 'Approach'].copy()

    if df.empty:
        return {"df": df, "empty": True}

    df['Hero Bucket'] = df['Starting Distance'].apply(approach_bucket)
    df['Table Bucket'] = df.apply(approach_bucket_table, axis=1)

    # ------------------------------------------------------------
    # 2. HERO METRICS
    # ------------------------------------------------------------
    hero_buckets = ["50–100", "100–150", "150–200", ">200"]
    hero_metrics = {}

    for b in hero_buckets:
        subset = df[df['Hero Bucket'] == b]

        if subset.empty:
            hero_metrics[b] = {
                "total_sg": 0,
                "sg_per_shot": 0,
                "prox": 0
            }
            continue

        hero_metrics[b] = {
            "total_sg": subset['Strokes Gained'].sum(),
            "sg_per_shot": subset['Strokes Gained'].mean(),
            "prox": subset['Ending Distance'].mean()
        }

    # ------------------------------------------------------------
    # 3. DISTANCE BUCKET TABLE (for expanders + radars)
    # ------------------------------------------------------------
    table_buckets = ["50–100", "100–150", "150–200", ">200", "Rough <150", "Rough >150"]
    table_rows = []

    for bucket in table_buckets:
        dfb = df[df['Table Bucket'] == bucket]

        if dfb.empty:
            table_rows.append([bucket, 0, 0, 0, 0, 0, 0, 0, 0])
            continue

        total_sg = dfb['Strokes Gained'].sum()
        shots = len(dfb)
        sg_per_shot = dfb['Strokes Gained'].mean()
        prox = dfb['Ending Distance'].mean()

        green_df = dfb[dfb['Ending Location'] == 'Green']
        prox_green = green_df['Ending Distance'].mean() if len(green_df) > 0 else 0
        gir = (len(green_df) / shots * 100) if shots > 0 else 0

        good = (dfb['Strokes Gained'] > 0.5).sum()
        bad = (dfb['Strokes Gained'] < -0.5).sum()

        table_rows.append([
            bucket, total_sg, shots, sg_per_shot, prox,
            prox_green, gir, good, bad
        ])

    bucket_table = pd.DataFrame(table_rows, columns=[
        "Bucket", "Total SG", "# Shots", "SG/Shot", "Proximity (ft)",
        "Prox on Green Hit (ft)", "GIR %", "Good Shots", "Bad Shots"
    ])

    # ------------------------------------------------------------
    # 4. RADAR METRICS
    # ------------------------------------------------------------
    radar_buckets = ["50–100", "100–150", "150–200", ">200", "Rough <150", "Rough >150"]
    radar_rows = []

    for bucket in radar_buckets:
        dfb = df[df['Table Bucket'] == bucket]

        if dfb.empty:
            radar_rows.append([bucket, 0, 0, 0])
            continue

        sg_per_shot = dfb['Strokes Gained'].mean()
        prox = dfb['Ending Distance'].mean()
        gir = (dfb['Ending Location'] == 'Green').mean() * 100

        radar_rows.append([bucket, sg_per_shot, prox, gir])

    radar_df = pd.DataFrame(radar_rows, columns=["Bucket", "SG/Shot", "Proximity", "GIR%"])

    # ------------------------------------------------------------
    # 5. HEATMAP DATA
    # ------------------------------------------------------------
    bucket_order = [">200", "150–200", "100–150", "50–100"]
    lie_order = ["Tee", "Fairway", "Rough", "Sand"]

    heat_df = df.dropna(subset=['Hero Bucket']).copy()
    heat_df['Lie'] = heat_df['Starting Location']

    heat_df['Hero Bucket'] = pd.Categorical(heat_df['Hero Bucket'], categories=bucket_order, ordered=True)
    heat_df['Lie'] = pd.Categorical(heat_df['Lie'], categories=lie_order, ordered=True)

    heatmap_data = heat_df.groupby(['Hero Bucket', 'Lie'])['Strokes Gained'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Hero Bucket', columns='Lie', values='Strokes Gained')

    # ------------------------------------------------------------
    # 6. TREND DATA
    # ------------------------------------------------------------
    round_labels = filtered_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    round_labels['Label'] = round_labels.apply(
        lambda r: f"{pd.to_datetime(r['Date']).strftime('%m/%d/%Y')} {r['Course']}",
        axis=1
    )

    trend_df = df.groupby('Round ID')['Strokes Gained'].sum().reset_index()
    trend_df = trend_df.merge(round_labels[['Round ID', 'Label', 'Date']], on='Round ID')
    trend_df = trend_df.sort_values('Date')

    # ------------------------------------------------------------
    # 7. SCATTER DATA
    # ------------------------------------------------------------
    scatter_df = df.copy()

    # ------------------------------------------------------------
    # RETURN EVERYTHING
    # ------------------------------------------------------------
    return {
        "empty": False,
        "df": df,
        "hero_metrics": hero_metrics,
        "bucket_table": bucket_table,
        "radar_df": radar_df,
        "heatmap_pivot": heatmap_pivot,
        "trend_df": trend_df,
        "scatter_df": scatter_df,
        "round_labels": round_labels
    }

# ============================================================
# SHORT GAME ENGINE
# ============================================================

def sg_bucket(dist):
    """Distance bucket for short game shots."""
    if dist <= 10:
        return "0–10"
    if 10 < dist <= 20:
        return "10–20"
    if 20 < dist <= 30:
        return "20–30"
    return "30–50"   # No 50+ bucket


def short_game_engine(filtered_df):
    """Compute all short game analytics for the Short Game tab."""

    df = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()

    if df.empty:
        return {"empty": True}

    # ------------------------------------------------------------
    # 1. Buckets + Flags
    # ------------------------------------------------------------
    df['SG Bucket'] = df['Starting Distance'].apply(sg_bucket)
    df['Green Hit'] = df['Ending Location'] == 'Green'
    df['Leave Dist'] = df['Ending Distance']

    # Shots inside 8 ft
    df['Inside 8ft'] = df['Ending Distance'] <= 8

    # ------------------------------------------------------------
    # 2. HERO METRICS
    # ------------------------------------------------------------

    # SG: Around the Green
    total_sg = df['Strokes Gained'].sum()

    # Shots inside 8 ft (Fairway + Rough)
    fr_df = df[df['Starting Location'].isin(['Fairway', 'Rough'])]
    inside_8_fr = fr_df['Inside 8ft'].sum()

    # Shots inside 8 ft (Sand)
    sand_df = df[df['Starting Location'] == 'Sand']
    inside_8_sand = sand_df['Inside 8ft'].sum()

    # Avg proximity
    avg_prox = df['Ending Distance'].mean()

    hero_metrics = {
        "sg_total": total_sg,
        "inside_8_fr": inside_8_fr,
        "inside_8_sand": inside_8_sand,
        "avg_proximity": avg_prox
    }

    # ------------------------------------------------------------
    # 3. DISTANCE × LIE TABLE
    # ------------------------------------------------------------
    distance_buckets = ["0–10", "10–20", "20–30", "30–50"]
    lie_types = ["Fairway", "Rough", "Sand"]

    rows = []

    for bucket in distance_buckets:
        for lie in lie_types:
            dfb = df[(df['SG Bucket'] == bucket) & (df['Starting Location'] == lie)]

            if dfb.empty:
                rows.append([bucket, lie, 0, 0, 0, 0, 0])
                continue

            attempts = len(dfb)
            sg_total = dfb['Strokes Gained'].sum()
            sg_per = sg_total / attempts
            prox = dfb['Ending Distance'].mean()
            green_hits = dfb['Green Hit'].sum()

            rows.append([
                bucket, lie, attempts, sg_total, sg_per, prox, green_hits
            ])

    distance_lie_table = pd.DataFrame(rows, columns=[
        "Bucket", "Lie", "Attempts", "SG Total", "SG/Shot",
        "Avg Proximity", "Green Hits"
    ])

    # ------------------------------------------------------------
    # 4. TREND DATA
    # ------------------------------------------------------------
    round_labels = filtered_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    round_labels['Label'] = round_labels.apply(
        lambda r: f"{pd.to_datetime(r['Date']).strftime('%m/%d/%Y')} {r['Course']}",
        axis=1
    )

    trend_df = df.groupby('Round ID').agg(
        SG=('Strokes Gained', 'sum'),
        Inside8=('Inside 8ft', 'sum'),
        Attempts=('Inside 8ft', 'count')
    ).reset_index()

    trend_df['Inside8 %'] = trend_df['Inside8'] / trend_df['Attempts'] * 100
    trend_df = trend_df.merge(round_labels[['Round ID', 'Label', 'Date']], on='Round ID')
    trend_df = trend_df.sort_values('Date')

    # ------------------------------------------------------------
    # RETURN EVERYTHING
    # ------------------------------------------------------------
    return {
        "empty": False,
        "df": df,
        "hero_metrics": hero_metrics,
        "distance_lie_table": distance_lie_table,
        "trend_df": trend_df
    }


# ============================================================
# PUTTING ENGINE
# ============================================================

def putting_bucket(dist):
    """Distance bucket for putting."""
    if dist <= 3:
        return "0–3"
    if 4 <= dist <= 10:
        return "4–10"
    if 11 <= dist <= 20:
        return "11–20"
    if 21 <= dist <= 30:
        return "21–30"
    return "31+"


def putting_engine(filtered_df):
    """Compute all putting analytics for the Putting tab."""

    df = filtered_df[filtered_df['Shot Type'] == 'Putting'].copy()

    if df.empty:
        return {"empty": True}

    # ------------------------------------------------------------
    # 1. Buckets + Flags
    # ------------------------------------------------------------
    df['Putt Bucket'] = df['Starting Distance'].apply(putting_bucket)
    df['Make'] = df['Ending Location'] == 'Hole'
    df['Leave Dist'] = df['Ending Distance']

    # First putt of each hole
    df['First Putt'] = df.groupby(['Round ID', 'Hole'])['Shot'].transform('min') == df['Shot']

    # 3-putt detection
    putt_counts = df.groupby(['Round ID', 'Hole'])['Shot'].count().rename("Putt Count")
    df = df.merge(putt_counts, on=['Round ID', 'Hole'], how='left')
    df['Three Putt'] = df['Putt Count'] >= 3

    # ------------------------------------------------------------
    # 2. HERO METRICS
    # ------------------------------------------------------------

    # Make % (4–5 ft)
    hero_45 = df[(df['Starting Distance'] >= 4) & (df['Starting Distance'] <= 5)]
    hero_make_pct = (hero_45['Make'].mean() * 100) if len(hero_45) > 0 else 0

    # SG (5–10 ft)
    sg_510 = df[(df['Starting Distance'] >= 5) & (df['Starting Distance'] <= 10)]
    hero_sg_510 = sg_510['Strokes Gained'].sum() if len(sg_510) > 0 else 0

    # Total 3-putts
    total_three_putts = df[df['Three Putt']].groupby(['Round ID', 'Hole']).ngroups

    # Lag misses (>5 ft leave)
    lag_miss = df[df['First Putt']]['Leave Dist'] > 5
    lag_miss_pct = lag_miss.mean() * 100 if len(lag_miss) > 0 else 0

    # Clutch index (birdie putts inside 10 ft)
    clutch_df = df[(df['First Putt']) & (df['Starting Distance'] <= 10)]
    clutch_makes = clutch_df['Make'].sum()
    clutch_attempts = len(clutch_df)
    clutch_pct = (clutch_makes / clutch_attempts * 100) if clutch_attempts > 0 else 0

    hero_metrics = {
        "make_45_pct": hero_make_pct,
        "sg_510": hero_sg_510,
        "three_putts": total_three_putts,
        "lag_miss_pct": lag_miss_pct,
        "clutch_pct": clutch_pct
    }

    # ------------------------------------------------------------
    # 3. DISTANCE BUCKET TABLE (with 3-putt %)
    # ------------------------------------------------------------
    bucket_rows = []

    for bucket in ["0–3", "4–10", "11–20", "21–30", "31+"]:
        dfb = df[df['Putt Bucket'] == bucket]

        if dfb.empty:
            bucket_rows.append([bucket, 0, 0, 0, 0, 0, 0, 0])
            continue

        attempts = len(dfb)
        makes = dfb['Make'].sum()
        make_pct = makes / attempts * 100

        total_sg = dfb['Strokes Gained'].sum()
        sg_per = total_sg / attempts

        avg_leave = dfb[dfb['First Putt']]['Leave Dist'].mean()

        # 3-putt %
        three_putt_holes = dfb[dfb['Three Putt']].groupby(['Round ID', 'Hole']).ngroups
        three_putt_pct = (three_putt_holes / attempts * 100) if attempts > 0 else 0

        bucket_rows.append([
            bucket, attempts, makes, make_pct,
            total_sg, sg_per, avg_leave, three_putt_pct
        ])

    bucket_table = pd.DataFrame(bucket_rows, columns=[
        "Bucket", "Attempts", "Makes", "Make %", "Total SG",
        "SG/Shot", "Avg Leave (ft)", "3-Putt %"
    ])

    # ------------------------------------------------------------
    # 4. TREND DATA
    # ------------------------------------------------------------
    round_labels = filtered_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    round_labels['Label'] = round_labels.apply(
        lambda r: f"{pd.to_datetime(r['Date']).strftime('%m/%d/%Y')} {r['Course']}",
        axis=1
    )

    trend_df = df.groupby('Round ID').agg(
        SG=('Strokes Gained', 'sum'),
        Makes=('Make', 'sum'),
        Attempts=('Make', 'count'),
        ThreePutts=('Three Putt', 'sum')
    ).reset_index()

    trend_df['Make %'] = trend_df['Makes'] / trend_df['Attempts'] * 100
    trend_df = trend_df.merge(round_labels[['Round ID', 'Label', 'Date']], on='Round ID')
    trend_df = trend_df.sort_values('Date')

    # ------------------------------------------------------------
    # 5. LAG METRICS
    # ------------------------------------------------------------
    first_putts = df[df['First Putt']]
    avg_leave = first_putts['Leave Dist'].mean()
    pct_inside_3 = (first_putts['Leave Dist'] <= 3).mean() * 100
    pct_over_5 = (first_putts['Leave Dist'] > 5).mean() * 100

    lag_metrics = {
        "avg_leave": avg_leave,
        "pct_inside_3": pct_inside_3,
        "pct_over_5": pct_over_5
    }

    # ------------------------------------------------------------
    # RETURN EVERYTHING
    # ------------------------------------------------------------
    return {
        "empty": False,
        "df": df,
        "hero_metrics": hero_metrics,
        "bucket_table": bucket_table,
        "trend_df": trend_df,
        "lag_metrics": lag_metrics
    }

# ============================================================
# COACH'S CORNER ENGINE (engine-powered)
# ============================================================

def classify_light(row):
    """DECADE-style Green/Yellow/Red classification."""
    if row['Shot Type'] not in ['Driving', 'Approach', 'Short Game']:
        return None

    dist = row['Starting Distance']
    lie = row.get('Starting Location', None)

    if lie == 'Fairway' and dist < 150:
        return 'Green'
    if lie == 'Rough' and 100 <= dist <= 175:
        return 'Yellow'
    if lie in ['Sand', 'Recovery'] or dist > 175:
        return 'Red'

    return 'Yellow'


def compute_gir_red_flags(approach):
    """GIR buckets < 50%."""
    table = approach.get("bucket_table")
    if table is None or table.empty or "GIR %" not in table.columns:
        return []

    gir_flags = table[table["GIR %"] < 50].copy()
    gir_flags = gir_flags.sort_values("GIR %")

    return [
        {"bucket": row["Bucket"], "gir_pct": row["GIR %"]}
        for _, row in gir_flags.iterrows()
    ]


def compute_short_game_flags(short_game):
    """Short game inside-8ft % by lie type."""
    df = short_game.get("df")
    hero = short_game.get("hero_metrics", {})

    if df is None or df.empty:
        return {}

    inside_8_fr = hero.get("inside_8_fr", 0)
    inside_8_sand = hero.get("inside_8_sand", 0)

    fr_df = df[df['Starting Location'].isin(['Fairway', 'Rough'])]
    sand_df = df[df['Starting Location'] == 'Sand']

    fr_attempts = len(fr_df)
    sand_attempts = len(sand_df)

    return {
        "inside8_fr_pct": (inside_8_fr / fr_attempts * 100) if fr_attempts > 0 else 0,
        "inside8_sand_pct": (inside_8_sand / sand_attempts * 100) if sand_attempts > 0 else 0,
        "fr_attempts": fr_attempts,
        "sand_attempts": sand_attempts
    }


def compute_putting_flags(putting):
    """Putting red flags including 3-putts inside 20 ft."""
    df = putting.get("df")
    hero = putting.get("hero_metrics", {})
    table = putting.get("bucket_table")

    flags = {
        "make_45_pct": hero.get("make_45_pct", 0),
        "sg_510": hero.get("sg_510", 0),
        "lag_miss_pct": hero.get("lag_miss_pct", 0),
        "three_putt_buckets": [],
        "three_putts_inside_20": 0
    }

    if table is not None and not table.empty and "3-Putt %" in table.columns:
        for _, row in table.iterrows():
            flags["three_putt_buckets"].append({
                "bucket": row["Bucket"],
                "three_putt_pct": row["3-Putt %"]
            })

    if df is not None and not df.empty:
        first_putts = df[df['First Putt']]
        inside20 = first_putts[first_putts['Starting Distance'] <= 20]
        flags["three_putts_inside_20"] = inside20[inside20['Three Putt']].groupby(
            ['Round ID', 'Hole']
        ).ngroups

    return flags


def compute_green_yellow_red_sg(df):
    """SG by Green/Yellow/Red light."""
    temp = df.copy()
    temp['Light'] = temp.apply(classify_light, axis=1)
    temp = temp[temp['Light'].notna()]

    if temp.empty:
        return []

    grouped = temp.groupby('Light')['Strokes Gained'].sum().reset_index()

    order = {"Green": 0, "Yellow": 1, "Red": 2}
    return sorted(
        [{"light": r["Light"], "total_sg": r["Strokes Gained"]} for _, r in grouped.iterrows()],
        key=lambda x: order.get(x["light"], 99)
    )


def compute_bogey_avoidance(df):
    """Bogey avoidance by par type."""
    if df.empty or "Score" not in df.columns or "Par" not in df.columns:
        return {}

    holes = df.groupby(['Round ID', 'Hole']).agg(
        Score=('Score', 'max'),
        Par=('Par', 'max')
    ).reset_index()
    holes['Rel'] = holes['Score'] - holes['Par']

    results = {}
    for par_val in [3, 4, 5]:
        subset = holes[holes['Par'] == par_val]
        if subset.empty:
            results[f"Par{par_val}"] = {"bogey_rate": None}
            continue

        bogey_rate = (subset['Rel'] >= 1).mean() * 100
        results[f"Par{par_val}"] = {"bogey_rate": bogey_rate}

    results["Overall"] = {"bogey_rate": (holes['Rel'] >= 1).mean() * 100}
    return results


def compute_birdie_opportunities(df):
    """Birdie opportunities + conversion."""
    if df.empty or "Score" not in df.columns or "Par" not in df.columns:
        return {"opportunities": 0, "conversions": 0, "conversion_pct": 0}

    holes = df.groupby(['Round ID', 'Hole']).agg(
        Score=('Score', 'max'),
        Par=('Par', 'max')
    ).reset_index()
    holes['Rel'] = holes['Score'] - holes['Par']
    holes['BirdieOrBetter'] = holes['Rel'] <= -1

    mask = (
        df['Shot Type'].isin(['Approach', 'Short Game']) &
        (df['Ending Location'] == 'Green') &
        (df['Ending Distance'] <= 20)
    )
    opp_shots = df[mask]

    if opp_shots.empty:
        return {"opportunities": 0, "conversions": 0, "conversion_pct": 0}

    opp_holes = opp_shots[['Round ID', 'Hole']].drop_duplicates()
    merged = opp_holes.merge(holes, on=['Round ID', 'Hole'], how='left')

    opportunities = len(merged)
    conversions = merged['BirdieOrBetter'].sum()

    return {
        "opportunities": opportunities,
        "conversions": conversions,
        "conversion_pct": conversions / opportunities * 100 if opportunities > 0 else 0
    }


def compute_flow_metrics(df):
    """Bounce Back, Drop Off, Gas Pedal, Bogey Trains."""
    if df.empty or "Score" not in df.columns or "Par" not in df.columns:
        return {}

    holes = df.groupby(['Round ID', 'Hole']).agg(
        Score=('Score', 'max'),
        Par=('Par', 'max')
    ).reset_index()
    holes['Rel'] = holes['Score'] - holes['Par']
    holes = holes.sort_values(['Round ID', 'Hole']).reset_index(drop=True)

    bounce_numer = bounce_denom = 0
    drop_numer = drop_denom = 0
    gas_numer = gas_denom = 0
    bogey_trains = []

    for i in range(1, len(holes)):
        prev_rel = holes.loc[i-1, 'Rel']
        curr_rel = holes.loc[i, 'Rel']

        prev_bogey = prev_rel >= 1
        curr_bogey = curr_rel >= 1

        prev_birdie = prev_rel <= -1
        curr_birdie = curr_rel <= -1

        if prev_bogey:
            bounce_denom += 1
            if curr_rel <= 0:
                bounce_numer += 1

            drop_denom += 1
            if curr_bogey:
                drop_numer += 1

        if prev_birdie:
            gas_denom += 1
            if curr_birdie:
                gas_numer += 1

    # Bogey trains
    for _, group in holes.groupby('Round ID'):
        train_len = 0
        for _, row in group.iterrows():
            if row['Rel'] >= 1:
                train_len += 1
            else:
                if train_len >= 2:
                    bogey_trains.append(train_len)
                train_len = 0
        if train_len >= 2:
            bogey_trains.append(train_len)

    return {
        "bounce_back_pct": bounce_numer / bounce_denom * 100 if bounce_denom > 0 else 0,
        "drop_off_pct": drop_numer / drop_denom * 100 if drop_denom > 0 else 0,
        "gas_pedal_pct": gas_numer / gas_denom * 100 if gas_denom > 0 else 0,
        "bogey_trains": bogey_trains,
        "bogey_train_count": len(bogey_trains),
        "longest_bogey_train": max(bogey_trains) if bogey_trains else 0
    }


def compute_sg_category_breakdown(df):
    """SG totals by shot type."""
    if df.empty:
        return []

    grouped = df.groupby('Shot Type')['Strokes Gained'].sum().reset_index()
    grouped['Shot Type'] = grouped['Shot Type'].replace({'Putt': 'Putting'})

    results = list(zip(grouped['Shot Type'], grouped['Strokes Gained']))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def generate_practice_priorities(
    sg_breakdown,
    gir_flags,
    short_flags,
    putting_flags,
    green_yellow_red,
    bogey_avoid,
    birdie_opp,
    flow_metrics
):
    priorities = []

    if sg_breakdown:
        weakest = sg_breakdown[-1]
        priorities.append(f"Improve {weakest[0]} performance (lowest SG category).")

    for gf in gir_flags:
        priorities.append(
            f"Increase GIR from {gf['bucket']} (currently {gf['gir_pct']:.0f}% GIR)."
        )

    if short_flags.get("inside8_fr_pct", 100) < 40:
        priorities.append(
            f"Improve short game proximity from Fairway/Rough (only {short_flags['inside8_fr_pct']:.0f}% inside 8 ft)."
        )

    if short_flags.get("inside8_sand_pct", 100) < 30:
        priorities.append(
            f"Improve bunker play (only {short_flags['inside8_sand_pct']:.0f}% inside 8 ft)."
        )

    if putting_flags.get("three_putts_inside_20", 0) > 0:
        priorities.append(
            f"Reduce 3-putts inside 20 ft ({putting_flags['three_putts_inside_20']} occurrences)."
        )

    for gy in green_yellow_red:
        if gy["light"] == "Red" and gy["total_sg"] < 0:
            priorities.append(
                f"Improve decision-making in Red Light situations (losing {gy['total_sg']:.1f} SG)."
            )

    overall_bogey = bogey_avoid.get("Overall", {}).get("bogey_rate", None)
    if overall_bogey is not None and overall_bogey > 20:
        priorities.append(
            f"Reduce bogey rate (currently {overall_bogey:.0f}%)."
        )

    if birdie_opp["opportunities"] > 0 and birdie_opp["conversion_pct"] < 25:
        priorities.append(
            f"Convert more birdie opportunities (only {birdie_opp['conversion_pct']:.0f}% conversion)."
        )

    if flow_metrics["bounce_back_pct"] < 30:
        priorities.append("Improve bounce back after bogeys.")

    if flow_metrics["drop_off_pct"] > 50:
        priorities.append("Reduce bogey streaks and mistake stacking.")

    return priorities


# ============================================================
# MASTER COACH'S CORNER ENGINE
# ============================================================

def coachs_corner_engine(
    filtered_df,
    tiger5_results,
    driving,
    approach,
    putting,
    short_game
):
    sg_breakdown = compute_sg_category_breakdown(filtered_df)
    gir_flags = compute_gir_red_flags(approach)
    short_flags = compute_short_game_flags(short_game)
    putting_flags = compute_putting_flags(putting)
    green_yellow_red = compute_green_yellow_red_sg(filtered_df)
    bogey_avoid = compute_bogey_avoidance(filtered_df)
    birdie_opp = compute_birdie_opportunities(filtered_df)
    flow_metrics = compute_flow_metrics(filtered_df)

    priorities = generate_practice_priorities(
        sg_breakdown,
        gir_flags,
        short_flags,
        putting_flags,
        green_yellow_red,
        bogey_avoid,
        birdie_opp,
        flow_metrics
    )

    
    return {
        "sg_breakdown": sg_breakdown,
        "strengths": sg_breakdown[:2],
        "weaknesses": sg_breakdown[-2:],
        "gir_flags": gir_flags,
        "short_game_flags": short_flags,
        "putting_flags": putting_flags,
        "green_yellow_red": green_yellow_red,
        "bogey_avoidance": bogey_avoid,
        "birdie_opportunities": birdie_opp,
        "flow_metrics": flow_metrics,
        "practice_priorities": priorities,
        "tiger5_results": tiger5_results
    }

#Coach Summary
def generate_coach_summary(cc):
    """
    Create a natural-language coaching summary from Coach's Corner metrics.
    """

    parts = []

    # --- Strengths ---
    if cc["strengths"]:
        best_cat, best_sg = cc["strengths"][0]
        parts.append(
            f"Your strongest area recently has been {best_cat.lower()}, gaining {best_sg:+.1f} strokes in that category."
        )

    # --- Weaknesses ---
    if cc["weaknesses"]:
        worst_cat, worst_sg = cc["weaknesses"][-1]
        parts.append(
            f"The biggest opportunity for improvement is {worst_cat.lower()}, where you're losing {abs(worst_sg):.1f} strokes."
        )

    # --- GIR Red Flags ---
    if cc["gir_flags"]:
        worst_gir = cc["gir_flags"][0]
        parts.append(
            f"Approach play from {worst_gir['bucket']} is a concern with only {worst_gir['gir_pct']:.0f}% GIR."
        )

    # --- Short Game ---
    sgf = cc["short_game_flags"]
    if sgf["inside8_fr_pct"] < 40:
        parts.append(
            f"Short game from fairway and rough is leaving too many long putts, with only {sgf['inside8_fr_pct']:.0f}% finishing inside 8 feet."
        )
    if sgf["inside8_sand_pct"] < 30:
        parts.append(
            f"Bunker play needs attention, with just {sgf['inside8_sand_pct']:.0f}% of shots finishing inside 8 feet."
        )

    # --- Putting ---
    pf = cc["putting_flags"]
    if pf["three_putts_inside_20"] > 0:
        parts.append(
            f"Putting inside 20 feet is costing strokes, with {pf['three_putts_inside_20']} three-putt situations from makeable range."
        )
    if pf["lag_miss_pct"] > 30:
        parts.append(
            f"Lag putting is also an issue, with {pf['lag_miss_pct']:.0f}% of first putts finishing outside 5 feet."
        )

    # --- Decision Making (Green/Yellow/Red SG) ---
    for gy in cc["green_yellow_red"]:
        if gy["light"] == "Red" and gy["total_sg"] < 0:
            parts.append(
                f"You're losing {abs(gy['total_sg']):.1f} strokes in Red Light situations, suggesting decision-making or target selection needs refinement."
            )

    # --- Bogey Avoidance ---
    ba = cc["bogey_avoidance"]["Overall"]["bogey_rate"]
    if ba > 20:
        parts.append(
            f"Bogey avoidance is a key area, with a {ba:.0f}% bogey rate across all holes."
        )

    # --- Birdie Opportunities ---
    bo = cc["birdie_opportunities"]
    if bo["opportunities"] > 0 and bo["conversion_pct"] < 25:
        parts.append(
            f"You're creating birdie chances but converting only {bo['conversion_pct']:.0f}% of them."
        )

    # --- Flow Metrics ---
    fm = cc["flow_metrics"]
    if fm["bounce_back_pct"] < 30:
        parts.append(
            f"Bounce-back performance is low at {fm['bounce_back_pct']:.0f}%, indicating missed chances to recover after mistakes."
        )
    if fm["drop_off_pct"] > 50:
        parts.append(
            f"Drop-off rate after bogeys is high at {fm['drop_off_pct']:.0f}%, showing a tendency for mistakes to compound."
        )
    if fm["bogey_train_count"] > 0:
        parts.append(
            f"You had {fm['bogey_train_count']} bogey train(s), with the longest lasting {fm['longest_bogey_train']} holes."
        )

    # Combine into a single paragraph
    summary = " ".join(parts)
    return summary if summary else "No significant trends detected."


# ============================================================
# MAIN APP — WIRING ENGINES INTO TABS
# ============================================================

# ---------- LOAD DATA ----------
df = load_data()

# ---------- SIDEBAR FILTERS ----------
with st.sidebar:
    st.markdown('<p class="sidebar-title">ODU Golf</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-label">Filters</p>', unsafe_allow_html=True)

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
    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()

    st.markdown('<p class="sidebar-label">Date Range</p>', unsafe_allow_html=True)
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )

# ---------- APPLY FILTERS ----------
filtered_df = df[
    (df['Player'].isin(players)) &
    (df['Course'].isin(courses)) &
    (df['Tournament'].isin(tournaments)) &
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1])
].copy()

hole_summary = build_hole_summary(filtered_df)
num_rounds = filtered_df['Round ID'].nunique()

# ---------- BUILD CATEGORY DATAFRAMES ----------
putting_df = build_putting_df(filtered_df)
approach_df = build_approach_df(filtered_df)
drive = driving_engine(filtered_df, num_rounds)
short_game_df = build_short_game_df(filtered_df)

# ---------- TIGER 5 + COACH'S CORNER DATA ----------
tiger5_results, total_tiger5_fails, grit_score = calculate_tiger5(filtered_df, hole_summary)
t5_round_df = tiger5_by_round(filtered_df, hole_summary)

coachs_corner_data = build_coachs_corner(
    filtered_df,
    tiger5_results,
    putting_df,
    approach_df
)

# ============================================================
# HEADER
# ============================================================
st.markdown('<p class="main-title">ODU Golf Analytics</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="main-subtitle">{len(filtered_df)} shots from {num_rounds} rounds</p>',
    unsafe_allow_html=True
)

# ============================================================
# SEGMENT 6 — UI LAYOUT (TABS)
# ============================================================

tab_overview, tab_driving, tab_approach, tab_short_game, tab_putting, tab_coach = st.tabs(
    ["Overview", "Driving", "Approach", "Short Game", "Putting", "Coach's Corner"]
)

# ============================================================
# TAB: OVERVIEW
# ============================================================
with tab_overview:

    # ------------------------------------------------------------
    # TIGER 5 SUMMARY (ENGINE-POWERED)
    # ------------------------------------------------------------
    tiger5_results, total_tiger5_fails, grit_score = calculate_tiger5(filtered_df, hole_summary)

    st.markdown('<p class="section-title">Tiger 5 Performance</p>', unsafe_allow_html=True)

    tiger5_names = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # Tiger 5 Cards
    for col, stat_name in zip([col1, col2, col3, col4, col5], tiger5_names):
        fails = int(tiger5_results[stat_name]['fails'])
        attempts = int(tiger5_results[stat_name]['attempts'])
        card_class = "tiger-card-fail" if fails > 0 else "tiger-card-success"

        with col:
            st.markdown(f'''
                <div class="{card_class}">
                    <div class="card-label">{stat_name}</div>
                    <div class="card-value">{fails}</div>
                    <div class="card-unit">of {attempts}</div>
                </div>
            ''', unsafe_allow_html=True)

    # Grit Score Card
    with col6:
        grit_html = f'''
            <div class="grit-card">
                <div class="card-label">Grit Score</div>
                <div class="card-value">{grit_score:.1f}%</div>
                <div class="card-unit">success rate</div>
            </div>
        '''
        st.markdown(grit_html, unsafe_allow_html=True)

    # ------------------------------------------------------------
    # TIGER 5 TREND CHART (ENGINE-POWERED)
    # ------------------------------------------------------------
    with st.expander("View Tiger 5 Trend by Round"):
        t5_df = tiger5_by_round(filtered_df, hole_summary)

        if not t5_df.empty:
            fig_t5 = make_subplots(specs=[[{"secondary_y": True}]])

            t5_categories = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']
            t5_colors = [ODU_RED, ODU_DARK_GOLD, ODU_METALLIC_GOLD, ODU_PURPLE, ODU_BLACK]

            for cat, color in zip(t5_categories, t5_colors):
                fig_t5.add_trace(
                    go.Bar(
                        name=cat,
                        x=t5_df['Label'],
                        y=t5_df[cat],
                        marker_color=color
                    ),
                    secondary_y=False
                )

            fig_t5.add_trace(
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

            fig_t5.update_layout(
                barmode='stack',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family='Inter',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
                margin=dict(t=60, b=80, l=60, r=60),
                height=400,
                hovermode='x unified'
            )

            fig_t5.update_xaxes(tickangle=-45)
            fig_t5.update_yaxes(title_text='Tiger 5 Fails', gridcolor='#e8e8e8', secondary_y=False)
            fig_t5.update_yaxes(title_text='Total Score', showgrid=False, secondary_y=True)

            st.plotly_chart(fig_t5, use_container_width=True, config={'displayModeBar': False})

    # ------------------------------------------------------------
    # TIGER 5 FAIL DETAILS
    # ------------------------------------------------------------
    with st.expander("View Tiger 5 Fail Details"):
        for stat_name in tiger5_names:
            detail = tiger5_results[stat_name]
            if detail['fails'] > 0:
                st.markdown(f"**{stat_name}** ({int(detail['fails'])} fails)")

                for _, row in detail['detail_holes'].iterrows():
                    st.caption(
                        f"{row['Player']} | {row['Date']} | {row['Course']} | "
                        f"Hole {row['Hole']} (Par {int(row['Par'])}) | Score: {int(row['Hole Score'])}"
                    )

                    # Show shot-level detail
                    if stat_name == '3 Putts':
                        shots = filtered_df[
                            (filtered_df['Player'] == row['Player']) &
                            (filtered_df['Round ID'] == row['Round ID']) &
                            (filtered_df['Hole'] == row['Hole']) &
                            (filtered_df['Shot Type'] == 'Putt')
                        ][['Shot', 'Starting Distance', 'Ending Distance', 'Strokes Gained']].copy()
                        shots.columns = ['Putt', 'Start (ft)', 'End (ft)', 'SG']
                    else:
                        shots = filtered_df[
                            (filtered_df['Player'] == row['Player']) &
                            (filtered_df['Round ID'] == row['Round ID']) &
                            (filtered_df['Hole'] == row['Hole'])
                        ][['Shot', 'Starting Distance', 'Starting Location', 'Ending Distance', 'Ending Location', 'Strokes Gained']].copy()
                        shots.columns = ['Shot', 'Start', 'Lie', 'End', 'Result', 'SG']

                    shots['SG'] = shots['SG'].round(2)
                    st.dataframe(shots, use_container_width=True, hide_index=True)

                st.divider()

    # ------------------------------------------------------------
    # SG SUMMARY CARDS
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Strokes Gained Summary</p>', unsafe_allow_html=True)

    total_sg = filtered_df['Strokes Gained'].sum()
    sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0
    sg_tee_to_green = filtered_df[filtered_df['Shot Type'] != 'Putt']['Strokes Gained'].sum()

    putts_over_30 = filtered_df[(filtered_df['Shot Type'] == 'Putt') & (filtered_df['Starting Distance'] > 30)]
    sg_putts_over_30 = putts_over_30['Strokes Gained'].sum()

    putts_5_10 = filtered_df[(filtered_df['Shot Type'] == 'Putt') &
                             (filtered_df['Starting Distance'] >= 5) &
                             (filtered_df['Starting Distance'] <= 10)]
    sg_putts_5_10 = putts_5_10['Strokes Gained'].sum()

    metrics = [
        ('Total SG', total_sg),
        ('SG / Round', sg_per_round),
        ('SG Tee to Green', sg_tee_to_green),
        ('SG Putting >30ft', sg_putts_over_30),
        ('SG Putts 5–10ft', sg_putts_5_10)
    ]

    col1, col2, col3, col4, col5 = st.columns(5)
    for col, (label, val) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            val_class = sg_value_class(val)
            st.markdown(f"""
                <div class="sg-card">
                    <div class="card-label">{label}</div>
                    <div class="card-value {val_class}">{val:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

    # ------------------------------------------------------------
    # SG BY SHOT TYPE (BAR + TABLE)
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Performance by Shot Type</p>', unsafe_allow_html=True)

    sg_by_type = filtered_df.groupby('Shot Type')['Strokes Gained'].agg(
        Total_SG='sum',
        Shots='count',
        SG_per_Shot='mean'
    ).reset_index()

    sg_by_type['Total_SG'] = sg_by_type['Total_SG'].round(2)
    sg_by_type['SG_per_Shot'] = sg_by_type['SG_per_Shot'].round(3)
    sg_by_type = sg_by_type[sg_by_type['Shots'] > 0]

    colors = [ODU_RED if x < 0 else ODU_GOLD for x in sg_by_type['Total_SG']]

    fig_sg_type = go.Figure(
        data=[go.Bar(
            x=sg_by_type['Shot Type'],
            y=sg_by_type['Total_SG'],
            marker_color=colors,
            text=sg_by_type['Total_SG'].apply(lambda x: f'{x:.2f}'),
            textposition='outside'
        )]
    )

    fig_sg_type.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Inter',
        yaxis=dict(title='Total Strokes Gained', gridcolor='#e8e8e8'),
        margin=dict(t=40, b=40, l=60, r=40),
        height=400
    )

    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig_sg_type, use_container_width=True)
    with col_table:
        st.dataframe(
            sg_by_type[['Shot Type', 'Shots', 'SG_per_Shot']],
            use_container_width=True,
            hide_index=True,
            height=400
        )

    # ------------------------------------------------------------
    # SG TREND LINE
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Strokes Gained Trend</p>', unsafe_allow_html=True)

    round_labels = filtered_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    round_labels['Label'] = round_labels.apply(
        lambda r: f"{pd.to_datetime(r['Date']).strftime('%m/%d/%Y')} {r['Course']}",
        axis=1
    )

    sg_trend = filtered_df[
        ~filtered_df['Shot Type'].isin(['Recovery', 'Other'])
    ].groupby(['Round ID', 'Shot Type'])['Strokes Gained'].sum().reset_index()

    sg_trend = sg_trend.merge(round_labels[['Round ID', 'Label', 'Date']], on='Round ID')
    sg_trend = sg_trend.sort_values('Date')

    odu_line_colors = {
        'Driving': ODU_GOLD,
        'Approach': ODU_BLACK,
        'Short Game': ODU_PURPLE,
        'Putt': ODU_GREEN
    }

    fig_trend = px.line(
        sg_trend,
        x='Label',
        y='Strokes Gained',
        color='Shot Type',
        markers=True,
        color_discrete_map=odu_line_colors
    )

    fig_trend.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Inter',
        yaxis=dict(title='Total Strokes Gained', gridcolor='#e8e8e8'),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(t=60, b=80, l=60, r=40),
        height=400
    )

    fig_trend.update_xaxes(tickangle=-45)

    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

    # ------------------------------------------------------------
    # SCORING DISTRIBUTION
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Scoring Distribution</p>', unsafe_allow_html=True)

    score_order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double or Worse']
    overall_dist = hole_summary['Score Name'].value_counts().reindex(score_order, fill_value=0)

    fig_pie = go.Figure(
        data=[go.Pie(
            labels=overall_dist.index,
            values=overall_dist.values,
            hole=0.5,
            marker_colors=[ODU_PURPLE, ODU_GOLD, ODU_METALLIC_GOLD, ODU_DARK_GOLD, ODU_RED],
            textinfo='percent+label'
        )]
    )

    fig_pie.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        margin=dict(t=40, b=40, l=40, r=40),
        height=400
    )

    col_chart, col_metrics = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_metrics:
        st.markdown("**Average Score by Par**")
        avg_by_par = hole_summary.groupby('Par')['Hole Score'].mean()
        sg_by_par = hole_summary.groupby('Par')['total_sg'].sum()

        for par in [3, 4, 5]:
            if par in avg_by_par.index:
                st.markdown(
                    f"""
                    <div class="par-score-card">
                        <span class="par-label">Par {par}</span>
                        <span class="par-value">{avg_by_par[par]:.2f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("**Total SG by Par**")
        for par in [3, 4, 5]:
            if par in sg_by_par.index:
                sg_val = sg_by_par[par]
                border_color = ODU_GREEN if sg_val >= 0 else ODU_RED

                st.markdown(
                    f"""
                    <div class="par-score-card" style="border-left-color: {border_color};">
                        <span class="par-label">Par {par}</span>
                        <span class="par-value" style="color: {border_color};">{sg_val:+.2f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ------------------------------------------------------------
    # RAW DATA EXPANDERS
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Data</p>', unsafe_allow_html=True)

    with st.expander("View Raw Shot Data"):
        st.dataframe(filtered_df, use_container_width=True)

    with st.expander("View Hole Summary"):
        display_hole_summary = hole_summary[
            ['Player', 'Course', 'Hole', 'Par', 'Hole Score', 'num_penalties', 'num_putts', 'Score Name']
        ].copy()

        display_hole_summary.columns = [
            'Player', 'Course', 'Hole', 'Par', 'Score', 'Penalties', 'Putts', 'Result'
        ]

        st.dataframe(display_hole_summary, use_container_width=True, hide_index=True)


# ============================================================
# TAB: DRIVING 
# ============================================================
with tab_driving:

    drive = driving_engine(filtered_df, num_rounds)

    if drive["num_drives"] == 0:
        st.warning("No driving data available for the selected filters.")
        st.stop()

    # ------------------------------------------------------------
    # HERO CARDS
    # ------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value" style="color: {'#2d6a4f' if drive['driving_sg'] >= 0 else '#E03C31'};">
                    {drive['driving_sg']:+.2f}
                </div>
                <div class="hero-label">Total SG Driving</div>
                <div class="hero-sub">{drive['driving_sg_per_round']:+.2f} per round</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="hero-stat" style="border-color: #FFC72C;">
                <div class="hero-value">{drive['fairway_pct']:.0f}%</div>
                <div class="hero-label">Fairways Hit</div>
                <div class="hero-sub">{drive['fairway']} of {drive['num_drives']} drives</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        color = '#E03C31' if drive['obstruction_pct'] > 10 else '#FFC72C'
        st.markdown(
            f"""
            <div class="hero-stat" style="border-color: {color};">
                <div class="hero-value" style="color: {color};">{drive['obstruction_pct']:.1f}%</div>
                <div class="hero-label">Obstruction Rate</div>
                <div class="hero-sub">Sand + Recovery</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        color = '#E03C31' if drive['penalty_rate_pct'] > 5 else '#FFC72C'
        st.markdown(
            f"""
            <div class="hero-stat" style="border-color: {color};">
                <div class="hero-value" style="color: {color};">{drive['penalty_total']}</div>
                <div class="hero-label">Penalties + OB</div>
                <div class="hero-sub">{drive['penalty_rate_pct']:.1f}% of drives</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------------------
    # LANDING LOCATION DONUT + TABLE
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Where Are Your Drives Landing?</p>', unsafe_allow_html=True)

    col_viz, col_table = st.columns([1, 1])

    with col_viz:
        labels = ['Fairway', 'Rough', 'Sand', 'Recovery', 'Green']
        values = [
            drive['fairway'], drive['rough'], drive['sand'],
            drive['recovery'], drive['green']
        ]
        colors = [ODU_GOLD, ODU_DARK_GOLD, ODU_METALLIC_GOLD, ODU_RED, ODU_GREEN]

        chart_data = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]

        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=[d[0] for d in chart_data],
                    values=[d[1] for d in chart_data],
                    hole=0.6,
                    marker_colors=[d[2] for d in chart_data],
                    textinfo='label+percent',
                    textposition='outside',
                    textfont=dict(family='Inter', size=12),
                    pull=[0.02] * len(chart_data)
                )
            ]
        )

        fig_donut.update_layout(
            showlegend=False,
            margin=dict(t=40, b=40, l=40, r=40),
            height=400,
            annotations=[
                dict(
                    text=f'<b>{drive["num_drives"]}</b><br>Drives',
                    x=0.5, y=0.5,
                    font=dict(family='Playfair Display', size=24, color='#000'),
                    showarrow=False
                )
            ]
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    with col_table:
        st.markdown(
            f"""
            <table class="driving-table">
                <tr><th style="text-align: left;">Metric</th><th>#</th><th>%</th><th>Per Round</th></tr>

                <tr class="row-primary">
                    <td><strong>Driving</strong></td>
                    <td><strong>{drive['num_drives']}</strong></td>
                    <td>-</td>
                    <td><strong>{drive['num_drives']/num_rounds:.1f}</strong></td>
                </tr>

                <tr class="row-header"><td colspan="4">Ending Location</td></tr>

                <tr><td class="indent">Fairway</td><td>{drive['fairway']}</td><td>{fmt_pct(drive['fairway'], drive['num_drives'])}</td><td>{fmt_pr(drive['fairway'], num_rounds)}</td></tr>
                <tr><td class="indent">Rough</td><td>{drive['rough']}</td><td>{fmt_pct(drive['rough'], drive['num_drives'])}</td><td>{fmt_pr(drive['rough'], num_rounds)}</td></tr>
                <tr><td class="indent">Sand</td><td>{drive['sand']}</td><td>{fmt_pct(drive['sand'], drive['num_drives'])}</td><td>{fmt_pr(drive['sand'], num_rounds)}</td></tr>
                <tr><td class="indent">Recovery</td><td>{drive['recovery']}</td><td>{fmt_pct(drive['recovery'], drive['num_drives'])}</td><td>{fmt_pr(drive['recovery'], num_rounds)}</td></tr>

                <tr class="row-highlight">
                    <td><strong>Obstruction Rate</strong></td>
                    <td><strong>{drive['obstruction_count']}</strong></td>
                    <td><strong>{fmt_pct(drive['obstruction_count'], drive['num_drives'])}</strong></td>
                    <td><strong>{fmt_pr(drive['obstruction_count'], num_rounds)}</strong></td>
                </tr>

                <tr class="row-header"><td colspan="4">Penalties</td></tr>

                <tr><td class="indent">Penalty Strokes</td><td>{drive['penalty_count']}</td><td>{fmt_pct(drive['penalty_count'], drive['num_drives'])}</td><td>{fmt_pr(drive['penalty_count'], num_rounds)}</td></tr>
                <tr><td class="indent">OB (Re-Tee)</td><td>{drive['ob_count']}</td><td>{fmt_pct(drive['ob_count'], drive['num_drives'])}</td><td>{fmt_pr(drive['ob_count'], num_rounds)}</td></tr>

                <tr class="{ 'row-danger' if drive['penalty_total'] > 0 else 'row-highlight' }">
                    <td><strong>Penalty Rate</strong></td>
                    <td><strong>{drive['penalty_total']}</strong></td>
                    <td><strong>{fmt_pct(drive['penalty_total'], drive['num_drives'])}</strong></td>
                    <td><strong>{fmt_pr(drive['penalty_total'], num_rounds)}</strong></td>
                </tr>
            </table>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------------------
    # SG BY RESULT
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Strokes Gained by Result</p>', unsafe_allow_html=True)

    sg_df = drive["sg_by_result"].sort_values("Total SG", ascending=True)
    colors_bar = [ODU_RED if x < 0 else ODU_GOLD for x in sg_df['Total SG']]

    fig_sg_result = go.Figure(
        data=[
            go.Bar(
                y=sg_df['Result'],
                x=sg_df['Total SG'],
                orientation='h',
                marker_color=colors_bar,
                text=sg_df['Total SG'].apply(lambda x: f'{x:+.2f}'),
                textposition='outside',
                textfont=dict(family='Inter', size=12, color='#000')
            )
        ]
    )

    fig_sg_result.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Inter',
        xaxis=dict(
            title='Strokes Gained',
            gridcolor='#e8e8e8',
            zerolinecolor=ODU_BLACK,
            zerolinewidth=2
        ),
        yaxis=dict(title=''),
        margin=dict(t=20, b=40, l=100, r=80),
        height=250
    )

    st.plotly_chart(fig_sg_result, use_container_width=True)

    # ------------------------------------------------------------
    # DRIVING TREND
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Driving Performance Trend</p>', unsafe_allow_html=True)

    trend = drive["trend"]

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

    fig_trend.add_trace(
        go.Bar(
            x=trend['Label'],
            y=trend['SG'],
            name='SG Driving',
            marker_color=[ODU_RED if x < 0 else ODU_GOLD for x in trend['SG']],
            opacity=0.8
        ),
        secondary_y=False
    )

    fig_trend.add_trace(
        go.Scatter(
            x=trend['Label'],
            y=trend['Fairway %'],
            name='Fairway %',
            mode='lines+markers',
            line=dict(color=ODU_BLACK, width=3),
            marker=dict(size=10, color=ODU_BLACK)
        ),
        secondary_y=True
    )

    fig_trend.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Inter',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(t=60, b=80, l=60, r=60),
        height=350,
        hovermode='x unified',
        xaxis=dict(tickangle=-45)
    )

    fig_trend.update_yaxes(
        title_text="Strokes Gained",
        gridcolor='#e8e8e8',
        zerolinecolor=ODU_BLACK,
        zerolinewidth=2,
        secondary_y=False
    )

    fig_trend.update_yaxes(
        title_text="Fairway %",
        range=[0, 100],
        showgrid=False,
        secondary_y=True
    )

    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

    # ------------------------------------------------------------
    # DETAIL TABLES
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Detailed Data</p>', unsafe_allow_html=True)

    with st.expander(f"📋 All Driving Shots ({drive['num_drives']} total)"):

        detail = drive["df"][[
            'Player', 'Date', 'Course', 'Hole',
            'Starting Distance', 'Ending Distance',
            'Ending Location', 'Penalty', 'Strokes Gained'
        ]].copy()

        detail['Date'] = pd.to_datetime(detail['Date']).dt.strftime('%m/%d/%Y')

        detail.columns = [
            'Player', 'Date', 'Course', 'Hole',
            'Distance', 'End Dist', 'Result', 'Penalty', 'SG'
        ]

        detail['Hole'] = detail['Hole'].astype(int)
        detail['Distance'] = detail['Distance'].round(0).astype(int)
        detail['End Dist'] = detail['End Dist'].round(0).astype(int)
        detail['SG'] = detail['SG'].round(2)

        st.dataframe(
            detail.sort_values(['Date', 'Hole'], ascending=[False, True]),
            use_container_width=True,
            hide_index=True
        )

    if drive['ob_count'] > 0:
        with st.expander(f"⚠️ OB / Re-Tee Instances ({drive['ob_count']} total)"):

            ob_df = pd.DataFrame(drive['ob_details'])
            ob_df['Date'] = pd.to_datetime(ob_df['Date']).dt.strftime('%m/%d/%Y')
            ob_df['Hole'] = ob_df['Hole'].astype(int)

            st.dataframe(ob_df, use_container_width=True, hide_index=True)

    if drive['obstruction_count'] > 0:
        with st.expander(f"🏖️ Obstruction Shots ({drive['obstruction_count']} total)"):

            obs = drive["df"][
                drive["df"]['Ending Location'].isin(['Sand', 'Recovery'])
            ][[
                'Player', 'Date', 'Course', 'Hole',
                'Starting Distance', 'Ending Location', 'Strokes Gained'
            ]].copy()

            obs['Date'] = pd.to_datetime(obs['Date']).dt.strftime('%m/%d/%Y')

            obs.columns = [
                'Player', 'Date', 'Course', 'Hole',
                'Distance', 'Result', 'SG'
            ]

            obs['Hole'] = obs['Hole'].astype(int)
            obs['Distance'] = obs['Distance'].round(0).astype(int)
            obs['SG'] = obs['SG'].round(2)

            st.dataframe(obs, use_container_width=True, hide_index=True)


# ============================================================
# TAB: APPROACH
# ============================================================
with tab_approach:

    approach = approach_engine(filtered_df)

    if approach["empty"]:
        st.warning("No approach data available for the selected filters.")
        st.stop()

    df = approach["df"]

    st.markdown('<p class="section-title">Approach Play</p>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # HERO CARDS
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Approach Performance by Distance</p>', unsafe_allow_html=True)

    hero_buckets = ["50–100", "100–150", "150–200", ">200"]
    cols = st.columns(4)

    for col, bucket in zip(cols, hero_buckets):
        m = approach["hero_metrics"][bucket]

        val_class = "positive" if m["total_sg"] > 0 else "negative" if m["total_sg"] < 0 else ""

        with col:
            st.markdown(
                f"""
                <div class="hero-stat">
                    <div class="hero-value {val_class}">{m['total_sg']:.2f}</div>
                    <div class="hero-label">{bucket} Yards</div>
                    <div class="hero-sub">SG/Shot: {m['sg_per_shot']:.3f}</div>
                    <div class="hero-sub">Proximity: {m['prox']:.1f} ft</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ------------------------------------------------------------
    # DISTANCE BUCKET TABLE (expander)
    # ------------------------------------------------------------
    with st.expander("View Full Distance Bucket Table"):
        st.dataframe(
            approach["bucket_table"],
            use_container_width=True,
            hide_index=True
        )

    # ------------------------------------------------------------
    # RADAR CHARTS
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Approach Profile by Distance Bucket</p>', unsafe_allow_html=True)

    radar_df = approach["radar_df"]

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
                radialaxis=dict(
                    showgrid=True,
                    gridcolor="#444",
                    color="#FFC72C",
                    tickvals=[sg_min, 0, sg_max],
                    ticktext=["", "0.0", ""]
                ),
                angularaxis=dict(showgrid=True, gridcolor="#444", color="#FFC72C")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            font_color="#FFC72C",
            height=350
        )

        # Bold 0.0 ring
        fig_radar_sg.add_shape(
            type="path",
            path="M 0 0 L 1 0 A 1 1 0 1 1 -1 0 Z",
            xref="paper",
            yref="paper",
            line=dict(color="#FFC72C", width=4),
            layer="below"
        )

        st.plotly_chart(fig_radar_sg, use_container_width=True)

    # Radar 2 — Proximity
    with col2:
        fig_radar_prox = px.line_polar(
            radar_df,
            r="Proximity",
            theta="Bucket",
            line_close=True,
            range_r=[prox_max, prox_min],  # flipped scale
            title="Proximity (Closer = Better)",
            color_discrete_sequence=[ODU_BLACK]
        )
        fig_radar_prox.update_traces(fill='toself')

        fig_radar_prox.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    showgrid=True,
                    gridcolor="#444",
                    color="#FFC72C",
                    tickvals=[0, 30, 60],
                    ticktext=["0", "30", "60"]
                ),
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
            r="GGIR%",
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

    # ------------------------------------------------------------
    # SCATTER PLOT
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">SG vs Starting Distance</p>', unsafe_allow_html=True)

    fig_scatter = px.scatter(
        approach["scatter_df"],
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
    # HEATMAP
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">SG per Shot Heatmap</p>', unsafe_allow_html=True)

    fig_heat = px.imshow(
        approach["heatmap_pivot"],
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
    # TREND
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Approach SG Trend by Round</p>', unsafe_allow_html=True)

    trend_df = approach["trend_df"]

    use_ma = st.checkbox("Apply Moving Average", value=False)

    if use_ma:
        window = st.selectbox("Moving Average Window", [3, 5, 10], index=0)
        trend_df["SG_MA"] = trend_df["Strokes Gained"].rolling(window=window).mean()
        y_col = "SG_MA"
    else:
        y_col = "Strokes Gained"

    fig_trend = px.line(
        trend_df,
        x="Label",
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

    sg = short_game_engine(filtered_df)

    if sg["empty"]:
        st.warning("No short game data available for the selected filters.")
        st.stop()

    df = sg["df"]
    hero = sg["hero_metrics"]

    st.markdown('<p class="section-title">Short Game Performance</p>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # HERO CARDS
    # ------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    # SG: Around the Green
    with col1:
        color = "#2d6a4f" if hero["sg_total"] >= 0 else "#E03C31"
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value" style="color:{color};">{hero['sg_total']:+.2f}</div>
                <div class="hero-label">SG: Around the Green</div>
                <div class="hero-sub">Total</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Shots inside 8 ft (Fairway + Rough)
    with col2:
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value">{hero['inside_8_fr']}</div>
                <div class="hero-label">Inside 8 ft</div>
                <div class="hero-sub">Fairway + Rough</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Shots inside 8 ft (Sand)
    with col3:
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value">{hero['inside_8_sand']}</div>
                <div class="hero-label">Inside 8 ft</div>
                <div class="hero-sub">Sand</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Avg Proximity
    with col4:
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value">{hero['avg_proximity']:.1f} ft</div>
                <div class="hero-label">Avg Proximity</div>
                <div class="hero-sub">All Short Game Shots</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------------------
    # DISTANCE × LIE TABLE
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Performance by Distance & Lie</p>', unsafe_allow_html=True)

    st.dataframe(
        sg["distance_lie_table"],
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------------------------
    # TREND CHART
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Short Game Trend by Round</p>', unsafe_allow_html=True)

    trend_df = sg["trend_df"]

    use_ma = st.checkbox("Apply Moving Average", value=False, key="sg_ma")

    if use_ma:
        window = st.selectbox("Moving Average Window", [3, 5, 10], index=0, key="sg_ma_window")
        trend_df["SG_MA"] = trend_df["SG"].rolling(window=window).mean()
        trend_df["Inside8_MA"] = trend_df["Inside8 %"].rolling(window=window).mean()
        y1 = "SG_MA"
        y2 = "Inside8_MA"
    else:
        y1 = "SG"
        y2 = "Inside8 %"

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

    # SG bar chart
    fig_trend.add_trace(
        go.Bar(
            x=trend_df["Label"],
            y=trend_df[y1],
            name="SG: Short Game",
            marker_color=ODU_GOLD,
            opacity=0.85
        ),
        secondary_y=False
    )

    # Inside 8 ft line
    fig_trend.add_trace(
        go.Scatter(
            x=trend_df["Label"],
            y=trend_df[y2],
            name="% Inside 8 ft",
            mode="lines+markers",
            line=dict(color=ODU_BLACK, width=3),
            marker=dict(size=9, color=ODU_BLACK)
        ),
        secondary_y=True
    )

    fig_trend.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="Inter",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=60, b=80, l=60, r=60),
        height=350,
        hovermode="x unified",
        xaxis=dict(tickangle=-45)
    )

    fig_trend.update_yaxes(
        title_text="Strokes Gained",
        gridcolor="#e8e8e8",
        zerolinecolor=ODU_BLACK,
        zerolinewidth=2,
        secondary_y=False
    )

    fig_trend.update_yaxes(
        title_text="% Inside 8 ft",
        range=[0, 100],
        showgrid=False,
        secondary_y=True
    )

    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})


# ============================================================
# TAB: PUTTING
# ============================================================

with tab_putting:

    putting = putting_engine(filtered_df)

    if putting["empty"]:
        st.warning("No putting data available for the selected filters.")
        st.stop()

    df = putting["df"]
    hero = putting["hero_metrics"]

    st.markdown('<p class="section-title">Putting Performance</p>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # HERO CARDS
    # ------------------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)

    # Make % (4–5 ft)
    with col1:
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value">{hero['make_45_pct']:.0f}%</div>
                <div class="hero-label">Make %</div>
                <div class="hero-sub">4–5 ft</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # SG (5–10 ft)
    with col2:
        color = "#2d6a4f" if hero["sg_510"] >= 0 else "#E03C31"
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value" style="color:{color};">{hero['sg_510']:+.2f}</div>
                <div class="hero-label">SG Putting</div>
                <div class="hero-sub">5–10 ft</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Total 3-putts
    with col3:
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value">{hero['three_putts']}</div>
                <div class="hero-label">3-Putts</div>
                <div class="hero-sub">Total</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Lag Miss %
    with col4:
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value">{hero['lag_miss_pct']:.0f}%</div>
                <div class="hero-label">Lag Miss %</div>
                <div class="hero-sub">Leaves >5 ft</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Clutch %
    with col5:
        st.markdown(
            f"""
            <div class="hero-stat">
                <div class="hero-value">{hero['clutch_pct']:.0f}%</div>
                <div class="hero-label">Clutch Index</div>
                <div class="hero-sub">Birdie Putts ≤10 ft</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------------------
    # DISTANCE BUCKET TABLE
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Putting by Distance Bucket</p>', unsafe_allow_html=True)

    st.dataframe(
        putting["bucket_table"],
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------------------------
    # LAG METRICS
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Lag Putting</p>', unsafe_allow_html=True)

    lag = putting["lag_metrics"]

    colA, colB, colC = st.columns(3)

    with colA:
        st.metric("Avg Leave Distance", f"{lag['avg_leave']:.1f} ft")

    with colB:
        st.metric("Leaves Inside 3 ft", f"{lag['pct_inside_3']:.0f}%")

    with colC:
        st.metric("Leaves Over 5 ft", f"{lag['pct_over_5']:.0f}%")

    # ------------------------------------------------------------
    # TREND CHART
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Putting Trend by Round</p>', unsafe_allow_html=True)

    trend_df = putting["trend_df"]

    use_ma = st.checkbox("Apply Moving Average", value=False)

    if use_ma:
        window = st.selectbox("Moving Average Window", [3, 5, 10], index=0)
        trend_df["SG_MA"] = trend_df["SG"].rolling(window=window).mean()
        y_col = "SG_MA"
    else:
        y_col = "SG"

    fig_trend = px.line(
        trend_df,
        x="Label",
        y=y_col,
        markers=True,
        title="SG: Putting Trend",
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
# TAB: COACH'S CORNER
# ============================================================

with tab_coachs_corner:

    cc = coachs_corner_engine(
        filtered_df,
        tiger5_results,
        driving,
        approach,
        putting,
        short_game
    )

    st.markdown('<p class="section-title">Coach\'s Corner</p>', unsafe_allow_html=True)

    # ============================================================
    # COACH SUMMARY
    # ============================================================
    st.markdown('<p class="subsection-title">Coach Summary</p>', unsafe_allow_html=True)

    summary = generate_coach_summary(cc)
    st.markdown(f"<div class='coach-summary'>{summary}</div>", unsafe_allow_html=True)

    st.markdown("---")

    
    # ============================================================
    # 1. STRENGTHS & WEAKNESSES
    # ============================================================
    st.markdown('<p class="subsection-title">Strengths & Weaknesses</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Strengths")
        for cat, sg in cc["strengths"]:
            st.markdown(f"- **{cat}**: {sg:+.2f} SG")

    with col2:
        st.markdown("### Weaknesses")
        for cat, sg in cc["weaknesses"]:
            st.markdown(f"- **{cat}**: {sg:+.2f} SG")

    st.markdown("---")

    # ============================================================
    # 2. RED FLAGS
    # ============================================================
    st.markdown('<p class="subsection-title">Red Flags</p>', unsafe_allow_html=True)

    # --- Approach Red Flags ---
    st.markdown("### Approach (GIR < 50%)")
    gir_flags = cc["gir_flags"]
    if gir_flags:
        for gf in gir_flags:
            st.markdown(f"- **{gf['bucket']}**: {gf['gir_pct']:.0f}% GIR")
    else:
        st.markdown("*No GIR red flags.*")

    # --- Short Game Red Flags ---
    st.markdown("### Short Game (Inside 8 ft)")
    sgf = cc["short_game_flags"]
    st.markdown(f"- **Fairway/Rough**: {sgf['inside8_fr_pct']:.0f}% inside 8 ft")
    st.markdown(f"- **Sand**: {sgf['inside8_sand_pct']:.0f}% inside 8 ft")

    # --- Putting Red Flags ---
    st.markdown("### Putting")
    pf = cc["putting_flags"]
    st.markdown(f"- **Make % (4–5 ft)**: {pf['make_45_pct']:.0f}%")
    st.markdown(f"- **SG (5–10 ft)**: {pf['sg_510']:+.2f}")
    st.markdown(f"- **Lag Miss % (>5 ft)**: {pf['lag_miss_pct']:.0f}%")
    st.markdown(f"- **3-Putts Inside 20 ft**: {pf['three_putts_inside_20']}")

    st.markdown("---")

    # ============================================================
    # 3. DECISION MAKING (DECADE-style)
    # ============================================================
    st.markdown('<p class="subsection-title">Decision Making</p>', unsafe_allow_html=True)

    # --- Green / Yellow / Red SG ---
    st.markdown("### Green / Yellow / Red SG")
    for gy in cc["green_yellow_red"]:
        st.markdown(f"- **{gy['light']} Light**: {gy['total_sg']:+.2f} SG")

    # --- Bogey Avoidance ---
    st.markdown("### Bogey Avoidance")
    ba = cc["bogey_avoidance"]
    st.markdown(f"- **Overall**: {ba['Overall']['bogey_rate']:.0f}% bogey rate")
    st.markdown(f"- **Par 3**: {ba['Par3']['bogey_rate']:.0f}%")
    st.markdown(f"- **Par 4**: {ba['Par4']['bogey_rate']:.0f}%")
    st.markdown(f"- **Par 5**: {ba['Par5']['bogey_rate']:.0f}%")

    # --- Birdie Opportunities ---
    st.markdown("### Birdie Opportunities")
    bo = cc["birdie_opportunities"]
    st.markdown(f"- **Opportunities**: {bo['opportunities']}")
    st.markdown(f"- **Conversions**: {bo['conversions']}")
    st.markdown(f"- **Conversion %**: {bo['conversion_pct']:.0f}%")

    st.markdown("---")

    # ============================================================
    # 4. ROUND FLOW (Bounce Back, Drop Off, Gas Pedal, Bogey Trains)
    # ============================================================
    st.markdown('<p class="subsection-title">Round Flow</p>', unsafe_allow_html=True)

    fm = cc["flow_metrics"]

    colA, colB, colC, colD = st.columns(4)

    with colA:
        st.metric("Bounce Back %", f"{fm['bounce_back_pct']:.0f}%")

    with colB:
        st.metric("Drop Off %", f"{fm['drop_off_pct']:.0f}%")

    with colC:
        st.metric("Gas Pedal %", f"{fm['gas_pedal_pct']:.0f}%")

    with colD:
        st.metric("Bogey Trains", f"{fm['bogey_train_count']}")

    if fm["bogey_train_count"] > 0:
        st.markdown(f"- **Longest Train**: {fm['longest_bogey_train']} holes")
        st.markdown(f"- **Train Lengths**: {fm['bogey_trains']}")

    st.markdown("---")

    # ============================================================
    # 5. PRACTICE PRIORITIES
    # ============================================================
    st.markdown('<p class="subsection-title">Practice Priorities</p>', unsafe_allow_html=True)

    for p in cc["practice_priorities"]:
        st.markdown(f"- {p}")

