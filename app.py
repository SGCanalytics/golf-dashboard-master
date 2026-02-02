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
# HELPER FUNCTIONS
# ============================================================

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
# DATA LOADING
# ============================================================

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(SHEET_URL)

    df['Player'] = df['Player'].str.strip().str.title()
    df['Course'] = df['Course'].str.strip().str.title()
    df['Tournament'] = df['Tournament'].str.strip().str.title()

    first_shots = df[df['Shot'] == 1].copy()
    first_shots['Par'] = first_shots['Starting Distance'].apply(determine_par)

    df = df.merge(
        first_shots[['Round ID', 'Hole', 'Par']],
        on=['Round ID', 'Hole'],
        how='left'
    )

    df['Shot ID'] = (
        df['Round ID'] +
        '-H' + df['Hole'].astype(str) +
        '-S' + df['Shot'].astype(str)
    )

    df['Date'] = pd.to_datetime(df['Date'])

    return df


# ============================================================
# TAB: OVERVIEW
# ============================================================

def overview_tab(
    filtered_df,
    hole_summary,
    num_rounds,
    driving_results,
    approach_results,
    short_game_results,
    putting_results,
    tiger5_results
):
    
    # ------------------------------------------------------------
    # TIGER 5 SUMMARY (ENGINE-POWERED)
    # ------------------------------------------------------------
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
        grit_score = tiger5_results["grit_score"]
        st.markdown(f'''
            <div class="grit-card">
                <div class="card-label">Grit Score</div>
                <div class="card-value">{grit_score:.1f}%</div>
                <div class="card-unit">success rate</div>
            </div>
        ''', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # TIGER 5 TREND CHART
    # ------------------------------------------------------------
    with st.expander("View Tiger 5 Trend by Round"):
        t5_df = tiger5_results["by_round"]

        if not t5_df.empty:
            # your existing chart code goes here unchanged
            pass

    # ------------------------------------------------------------
    # TIGER 5 FAIL DETAILS
    # ------------------------------------------------------------
    with st.expander("View Tiger 5 Fail Details"):
        for stat_name in tiger5_names:
            detail = tiger5_results[stat_name]
            if detail['fails'] > 0:
                # your existing fail detail UI goes here unchanged
                pass

    # ------------------------------------------------------------
    # SG SUMMARY CARDS
    # ------------------------------------------------------------
    st.markdown('<p class="section-title">Strokes Gained Summary</p>', unsafe_allow_html=True)

    # Replace inline SG logic with overview engine output
    overview = overview_engine(
        filtered_df,
        hole_summary,
        driving_results,
        approach_results,
        short_game_results,
        putting_results,
        tiger5_results
    )

    total_sg = overview["total_sg"]
    sg_per_round = overview["sg_per_round"]
    sg_tee_to_green = overview["sg_tee_to_green"]
    sg_putts_over_30 = overview["sg_putts_over_30"]
    sg_putts_5_10 = overview["sg_putts_5_10"]

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

# ============================================================
# TAB: DRIVING 
# ============================================================

def driving_tab(drive, num_rounds):

    if drive["num_drives"] == 0:
        st.warning("No driving data available for the selected filters.")
        return

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
            f'''
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
            ''',
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

def approach_tab(approach, num_rounds):
    if approach["empty"]:
        st.warning("No approach data available for the selected filters.")
        return

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
    # DISTANCE BUCKET TABLE
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
        st.plotly_chart(fig_radar_sg, use_container_width=True)

    # Radar 2 — Proximity
    with col2:
        fig_radar_prox = px.line_polar(
            radar_df,
            r="Proximity",
            theta="Bucket",
            line_close=True,
            range_r=[prox_max, prox_min],
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

def short_game_tab(sg, num_rounds):

    if sg["empty"]:
        st.warning("No short game data available for the selected filters.")
        return

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

def putting_tab(putting, num_rounds):

    if putting["empty"]:
        st.warning("No putting data available for the selected filters.")
        return

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

    use_ma = st.checkbox("Apply Moving Average", value=False, key="putting_ma")

    if use_ma:
        window = st.selectbox("Moving Average Window", [3, 5, 10], index=0, key="putting_ma_window")
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

def coachs_corner_tab(cc):

    st.markdown('<p class="section-title">Coach\'s Corner</p>', unsafe_allow_html=True)

    # ============================================================
    # COACH SUMMARY
    # ============================================================
    st.markdown('<p class="subsection-title">Coach Summary</p>', unsafe_allow_html=True)

    summary = cc["coach_summary"]
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
    # 4. ROUND FLOW
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

# ============================================================
# MAIN APP — CONTROLLER
# ============================================================

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

num_rounds = filtered_df['Round ID'].nunique()

# ---------- HOLE SUMMARY ----------
hole_summary = build_hole_summary(filtered_df)

# ---------- ENGINE CALLS ----------
driving_results = driving_engine(filtered_df, num_rounds)
approach_results = approach_engine(filtered_df, num_rounds)
short_game_results = short_game_engine(filtered_df, num_rounds)
putting_results = putting_engine(filtered_df, num_rounds)

tiger5_results, total_tiger5_fails, grit_score = calculate_tiger5(filtered_df, hole_summary)

coachs_corner_results = coachs_corner_engine(
    filtered_df,
    tiger5_results,
    driving_results,
    approach_results,
    putting_results,
    short_game_results
)

# ============================================================
# TABS
# ============================================================

tab_overview, tab_driving, tab_approach, tab_short_game, tab_putting, tab_coach = st.tabs(
    ["Overview", "Driving", "Approach", "Short Game", "Putting", "Coach's Corner"]
)

with tab_overview:
    overview_tab(
        filtered_df,
        hole_summary,
        num_rounds,
        driving_results,
        approach_results,
        short_game_results,
        putting_results,
        tiger5_results
    )

with tab_driving:
    driving_tab(driving_results, num_rounds)

with tab_approach:
    approach_tab(approach_results, num_rounds)

with tab_short_game:
    short_game_tab(short_game_results, num_rounds)

with tab_putting:
    putting_tab(putting_results, num_rounds)

with tab_coach:
    coachs_corner_tab(coachs_corner_results)

# ============================================================
# SEGMENT 6 — UI LAYOUT (TABS)
# ============================================================

tab_overview, tab_driving, tab_approach, tab_short_game, tab_putting, tab_coach = st.tabs(
    ["Overview", "Driving", "Approach", "Short Game", "Putting", "Coach's Corner"]
)

# ============================================================
# TAB: OVERVIEW
# ============================================================

def overview_tab(filtered_df, hole_summary, num_rounds,
                 driving_results, approach_results,
                 short_game_results, putting_results,
                 tiger5_results):


def overview_tab(
    filtered_df,
    hole_summary,
    num_rounds,
    driving_results,
    approach_results,
    short_game_results,
    putting_results,
    tiger5_results
):
