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

# ============================================================
# DRIVING ENGINE
# ============================================================

def build_driving_df(df):
    """
    Return a driving-only DataFrame with consistent columns.
    Driving = Shot Type == 'Driving'
    """
    driving_df = df[df['Shot Type'] == 'Driving'].copy()

    if driving_df.empty:
        return driving_df

    # Normalize lie categories for accuracy
    driving_df['Fairway Hit'] = (driving_df['Ending Location'] == 'Fairway').astype(int)
    driving_df['Miss Left'] = (driving_df['Ending Location'].isin(['Left Rough', 'Left Trees', 'Left Sand'])).astype(int)
    driving_df['Miss Right'] = (driving_df['Ending Location'].isin(['Right Rough', 'Right Trees', 'Right Sand'])).astype(int)

    return driving_df


def driving_summary(driving_df, num_rounds):
    """
    Compute driving metrics:
        - SG Driving
        - Fairway %
        - Miss Left %
        - Miss Right %
        - Avg Distance (if available)
    """
    metrics = {
        'sg_driving': 0.0,
        'fairway_pct': "-",
        'miss_left_pct': "-",
        'miss_right_pct': "-",
        'avg_distance': "-"
    }

    if driving_df.empty or num_rounds == 0:
        return metrics

    metrics['sg_driving'] = driving_df['Strokes Gained'].sum()

    attempts = len(driving_df)
    metrics['fairway_pct'] = fmt_pct(driving_df['Fairway Hit'].sum(), attempts)
    metrics['miss_left_pct'] = fmt_pct(driving_df['Miss Left'].sum(), attempts)
    metrics['miss_right_pct'] = fmt_pct(driving_df['Miss Right'].sum(), attempts)

    if 'Starting Distance' in driving_df.columns:
        metrics['avg_distance'] = f"{driving_df['Starting Distance'].mean():.1f} ft"

    return metrics


# ============================================================
# APPROACH ENGINE
# ============================================================

def approach_bucket(dist):
    """Return hero bucket for approach shots."""
    if dist < 50:
        return None
    if 50 <= dist < 100:
        return "50–100"
    if 100 <= dist < 150:
        return "100–150"
    if 150 <= dist < 200:
        return "150–200"
    return ">200"


def approach_bucket_table(row):
    """Return table bucket for approach shots (lie‑restricted)."""
    dist = row['Starting Distance']
    lie = row['Starting Location']

    if lie not in ['Fairway', 'Rough', 'Sand']:
        return None

    if dist < 50:
        return None
    if 50 <= dist < 75:
        return "50–75"
    if 75 <= dist < 100:
        return "75–100"
    if 100 <= dist < 125:
        return "100–125"
    if 125 <= dist < 150:
        return "125–150"
    if 150 <= dist < 175:
        return "150–175"
    if 175 <= dist < 200:
        return "175–200"
    return "200+"


def build_approach_df(df):
    """
    Return an approach-only DataFrame with consistent columns.
    Approach = Shot Type == 'Approach'
    """
    approach_df = df[df['Shot Type'] == 'Approach'].copy()

    if approach_df.empty:
        return approach_df

    # Correct: apply bucket function row-by-row
    approach_df['Hero Bucket'] = approach_df['Starting Distance'].apply(approach_bucket)

    # Table bucket also applied row-by-row
    approach_df['Table Bucket'] = approach_df.apply(approach_bucket_table, axis=1)

    return approach_df

def approach_hero_metrics(approach_df):
    """
    Compute hero card metrics for each distance bucket:
        - Total SG
        - SG per Shot
        - Avg Proximity
    """
    buckets = ["50–100", "100–150", "150–200", ">200"]
    results = {b: {'total_sg': 0, 'sg_per_shot': 0, 'avg_prox': "-"} for b in buckets}

    if approach_df.empty:
        return results

    for b in buckets:
        subset = approach_df[approach_df['Hero Bucket'] == b]
        if subset.empty:
            continue

        total_sg = subset['Strokes Gained'].sum()
        shots = len(subset)
        avg_prox = subset['Ending Distance'].mean()

        results[b] = {
            'total_sg': total_sg,
            'sg_per_shot': total_sg / shots if shots > 0 else 0,
            'avg_prox': f"{avg_prox:.1f} ft"
        }

    return results


def approach_table(approach_df):
    """
    Build approach table grouped by lie‑restricted buckets.
    """
    if approach_df.empty:
        return pd.DataFrame(columns=['Bucket', 'Shots', 'Avg Proximity', 'Total SG', 'SG/Shot'])

    grouped = approach_df.groupby('Table Bucket').agg(
        Shots=('Strokes Gained', 'count'),
        Avg_Proximity=('Ending Distance', 'mean'),
        Total_SG=('Strokes Gained', 'sum')
    ).reset_index()

    grouped['SG/Shot'] = grouped['Total_SG'] / grouped['Shots']
    grouped['Avg_Proximity'] = grouped['Avg_Proximity'].apply(lambda x: f"{x:.1f} ft")
    grouped.rename(columns={'Table Bucket': 'Bucket'}, inplace=True)

    return grouped


def approach_sg_trend(approach_df):
    """
    SG Approach per round for trendline chart.
    """
    if approach_df.empty:
        return pd.DataFrame(columns=['Round ID', 'Date', 'Course', 'SG Approach'])

    grouped = approach_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        SG_Approach=('Strokes Gained', 'sum')
    ).reset_index()

    grouped['Date'] = pd.to_datetime(grouped['Date'])
    grouped = grouped.sort_values('Date')

    return grouped

# ============================================================
# SEGMENT 4B — SHORT GAME ENGINE
# ============================================================

def build_short_game_df(df):
    """
    Return a short-game-only DataFrame.
    Short Game = Shot Type == 'Short Game'
    """
    sg_df = df[df['Shot Type'] == 'Short Game'].copy()

    if sg_df.empty:
        return sg_df

    sg_df['Missed Green'] = (sg_df['Ending Location'] != 'Green').astype(int)
    sg_df['Proximity'] = sg_df['Ending Distance']

    return sg_df


def short_game_summary(sg_df):
    """
    Compute short game metrics:
        - Total SG
        - SG per Shot
        - Avg Proximity
        - Missed Green %
    """
    metrics = {
        'total_sg': 0.0,
        'sg_per_shot': 0.0,
        'avg_prox': "-",
        'miss_green_pct': "-"
    }

    if sg_df.empty:
        return metrics

    total_sg = sg_df['Strokes Gained'].sum()
    shots = len(sg_df)
    avg_prox = sg_df['Proximity'].mean()
    miss_pct = fmt_pct(sg_df['Missed Green'].sum(), shots)

    metrics['total_sg'] = total_sg
    metrics['sg_per_shot'] = total_sg / shots if shots > 0 else 0
    metrics['avg_prox'] = f"{avg_prox:.1f} ft"
    metrics['miss_green_pct'] = miss_pct

    return metrics


def short_game_sg_trend(sg_df):
    """
    SG Short Game per round for trendline chart.
    """
    if sg_df.empty:
        return pd.DataFrame(columns=['Round ID', 'Date', 'Course', 'SG Short Game'])

    grouped = sg_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        SG_SG=('Strokes Gained', 'sum')
    ).reset_index()

    grouped['Date'] = pd.to_datetime(grouped['Date'])
    grouped = grouped.sort_values('Date')

    return grouped

# ============================================================
# SEGMENT 5 — COACH'S CORNER ENGINE
# ============================================================

def sg_category_breakdown(df):
    """
    Compute SG totals by shot type:
        Driving, Approach, Short Game, Putting
    Returns a sorted list of (category, total_sg).
    """
    if df.empty:
        return []

    grouped = df.groupby('Shot Type')['Strokes Gained'].sum().reset_index()
    grouped = grouped[grouped['Shot Type'].isin(['Driving', 'Approach', 'Short Game', 'Putt'])]

    results = list(zip(grouped['Shot Type'], grouped['Strokes Gained']))
    results.sort(key=lambda x: x[1], reverse=True)

    return results


def tiger5_risk_profile(tiger5_results):
    """
    Convert Tiger 5 results into a coach-friendly risk profile.
    Returns a list of dicts:
        { 'name': '3 Putts', 'fails': X, 'attempts': Y, 'risk': % }
    """
    profile = []

    for name, data in tiger5_results.items():
        attempts = data['attempts']
        fails = data['fails']
        risk = (fails / attempts * 100) if attempts > 0 else 0

        profile.append({
            'name': name,
            'fails': fails,
            'attempts': attempts,
            'risk': risk
        })

    profile.sort(key=lambda x: x['risk'], reverse=True)
    return profile


def putting_red_flags(putting_df):
    """
    Identify putting issues:
        - Long lag misses
        - Low make % inside 10 ft
        - Excessive 3-putts
    Returns a dict of red flags.
    """
    flags = {
        'lag_miss_rate': "-",
        'inside_10_make_pct': "-",
        'three_putt_count': 0
    }

    if putting_df.empty:
        return flags

    # Lag misses: start >= 30 ft, end > 3 ft
    lag_mask = (putting_df['Starting Distance'] >= 30) & (putting_df['Ending Distance'] > 3)
    lag_misses = putting_df[lag_mask]
    flags['lag_miss_rate'] = fmt_pct(len(lag_misses), len(putting_df))

    # Inside 10 ft make %
    inside10 = putting_df[putting_df['Starting Distance'] <= 10]
    if not inside10.empty:
        flags['inside_10_make_pct'] = fmt_pct(inside10['Made'].sum(), len(inside10))

    # 3-putts
    hole_putts = putting_df.groupby('Hole Key').agg(
        putts=('Score', 'max')
    ).reset_index()
    flags['three_putt_count'] = (hole_putts['putts'] >= 3).sum()

    return flags


def approach_dispersion_summary(approach_df):
    """
    Summarize approach proximity by bucket:
        - Avg proximity
        - SG per shot
    Returns a list of dicts.
    """
    if approach_df.empty:
        return []

    grouped = approach_df.groupby('Hero Bucket').agg(
        avg_prox=('Ending Distance', 'mean'),
        total_sg=('Strokes Gained', 'sum'),
        shots=('Strokes Gained', 'count')
    ).reset_index()

    grouped['sg_per_shot'] = grouped['total_sg'] / grouped['shots']

    results = []
    for _, row in grouped.iterrows():
        results.append({
            'bucket': row['Hero Bucket'],
            'avg_prox': row['avg_prox'],
            'sg_per_shot': row['sg_per_shot']
        })

    results.sort(key=lambda x: x['sg_per_shot'])
    return results


def generate_practice_priorities(
    sg_breakdown,
    tiger5_profile,
    putting_flags,
    approach_dispersion
):
    """
    Generate coach-friendly practice priorities based on:
        - SG weaknesses
        - Tiger 5 risks
        - Putting red flags
        - Approach dispersion
    Returns a list of strings.
    """
    priorities = []

    # SG Weakest Category
    if sg_breakdown:
        weakest = sg_breakdown[-1]
        priorities.append(f"Improve {weakest[0]} performance (lowest SG category).")

    # Tiger 5 highest risk
    if tiger5_profile:
        highest_risk = tiger5_profile[0]
        if highest_risk['risk'] > 0:
            priorities.append(
                f"Reduce {highest_risk['name']} (risk {highest_risk['risk']:.1f}%)."
            )

    # Putting red flags
    if putting_flags['inside_10_make_pct'] != "-":
        pct = float(putting_flags['inside_10_make_pct'].replace('%', ''))
        if pct < 60:
            priorities.append("Increase make rate inside 10 feet.")

    if putting_flags['lag_miss_rate'] != "-":
        lag_pct = float(putting_flags['lag_miss_rate'].replace('%', ''))
        if lag_pct > 25:
            priorities.append("Improve long-distance lag control (>30 ft).")

    if putting_flags['three_putt_count'] > 0:
        priorities.append("Reduce 3-putts through speed control practice.")

    # Approach dispersion
    if approach_dispersion:
        worst_bucket = approach_dispersion[0]
        priorities.append(
            f"Focus on approach shots from {worst_bucket['bucket']} (lowest SG/shot)."
        )

    return priorities


# ============================================================
# MASTER COACH'S CORNER ENGINE
# ============================================================

def build_coachs_corner(
    df,
    tiger5_results,
    putting_df,
    approach_df
):
    """
    Build all insights for the Coach's Corner tab.

    Returns:
        dict containing:
            - strengths
            - weaknesses
            - tiger5_risks
            - putting_flags
            - approach_dispersion
            - practice_priorities
    """
    sg_breakdown = sg_category_breakdown(df)
    tiger5_profile = tiger5_risk_profile(tiger5_results)
    putting_flags = putting_red_flags(putting_df)
    approach_disp = approach_dispersion_summary(approach_df)

    priorities = generate_practice_priorities(
        sg_breakdown,
        tiger5_profile,
        putting_flags,
        approach_disp
    )

    return {
        'strengths': sg_breakdown[:2],
        'weaknesses': sg_breakdown[-2:],
        'tiger5_risks': tiger5_profile,
        'putting_flags': putting_flags,
        'approach_dispersion': approach_disp,
        'practice_priorities': priorities
    }
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
driving_df = build_driving_df(filtered_df)
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
# TAB: OVERVIEW (REBUILT, CLEAN, ENGINE-POWERED)
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
    # Here you can keep your existing driving layout.
    # Replace any ad-hoc groupbys with:
    #   driving_metrics = driving_summary(driving_df, num_rounds)
    # and use driving_df directly for tables/plots.
    st.write("Use driving_df and driving_summary(driving_df, num_rounds) in your existing layout.")

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

        # Force a tick at 0.0 so the ring exists
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
                angularaxis=dict(
                    showgrid=True,
                    gridcolor="#444",
                    color="#FFC72C"
                )
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            font_color="#FFC72C",
            height=350
        )

    # ⭐ Bold 0.0 ring using a polar-sector shape
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
            range_r=[prox_max, prox_min],  # flip scale: closer = farther out
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
                angularaxis=dict(
                    showgrid=True,
                    gridcolor="#444",
                    color="#FFC72C"
                )
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

    st.write("Use approach_df, approach_hero_metrics, approach_table, approach_sg_trend in your existing layout.")

# ============================================================
# TAB: SHORT GAME
# ============================================================
with tab_short_game:
    # Keep your existing layout.
    # Use:
    #   sg_metrics = short_game_summary(short_game_df)
    #   sg_trend_df = short_game_sg_trend(short_game_df)
    st.write("Use short_game_df, short_game_summary, short_game_sg_trend in your existing layout.")

# ============================================================
# TAB: PUTTING
# ============================================================
with tab_putting:
    # Keep your existing layout and visuals.
    # Replace broken table logic with:
    #   putting_metrics = putting_hero_metrics(putting_df, num_rounds)
    #   make_table_df = putting_make_pct_by_distance(putting_df)
    #   lag_scatter_df = putting_lag_scatter_data(putting_df)
    #   putting_trend_df = putting_sg_by_round(putting_df)
    #   clutch_val = putting_clutch_index(putting_df)
    st.write("Use putting_df and the putting_* engine functions in your existing Putting tab layout.")

# ============================================================
# TAB: COACH'S CORNER
# ============================================================
with tab_coach:
    st.markdown('<p class="section-title">Coach\'s Corner</p>', unsafe_allow_html=True)

    strengths = coachs_corner_data['strengths']
    weaknesses = coachs_corner_data['weaknesses']
    tiger5_risks = coachs_corner_data['tiger5_risks']
    putting_flags = coachs_corner_data['putting_flags']
    approach_disp = coachs_corner_data['approach_dispersion']
    priorities = coachs_corner_data['practice_priorities']

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Strengths")
        if strengths:
            for cat, val in strengths:
                st.markdown(f"- **{cat}:** {val:.2f} SG")
        else:
            st.write("No strengths identified (insufficient data).")

        st.subheader("Weaknesses")
        if weaknesses:
            for cat, val in weaknesses:
                st.markdown(f"- **{cat}:** {val:.2f} SG")
        else:
            st.write("No weaknesses identified (insufficient data).")

        st.subheader("Practice Priorities")
        if priorities:
            for p in priorities:
                st.markdown(f"- {p}")
        else:
            st.write("No specific priorities generated.")

    with col_right:
        st.subheader("Tiger 5 Risk Profile")
        if tiger5_risks:
            for item in tiger5_risks:
                st.markdown(
                    f"- **{item['name']}** — {item['fails']} fails in {item['attempts']} attempts "
                    f"({item['risk']:.1f}% risk)"
                )
        else:
            st.write("No Tiger 5 data available.")

        st.subheader("Putting Red Flags")
        st.markdown(f"- **Lag Miss Rate:** {putting_flags['lag_miss_rate']}")
        st.markdown(f"- **Make % Inside 10 ft:** {putting_flags['inside_10_make_pct']}")
        st.markdown(f"- **3-Putt Holes:** {putting_flags['three_putt_count']}")

        st.subheader("Approach Dispersion")
        if approach_disp:
            for item in approach_disp:
                st.markdown(
                    f"- **{item['bucket']}** — Avg Prox: {item['avg_prox']:.1f} ft, "
                    f"SG/Shot: {item['sg_per_shot']:.3f}"
                )
        else:
            st.write("No approach dispersion data available.")
