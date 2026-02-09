# ============================================================
# TAB: COMPARISON — Multi-Group Performance Analysis
# ============================================================
# Compare performance across:
# 1. Player vs Player
# 2. Round Quality (Under Par vs Even - +3 vs >+4)
# 3. Time Period (Recent vs Previous rounds)
# ============================================================

import streamlit as st
import pandas as pd

from ui.theme import (
    CHARCOAL, SLATE, FONT_BODY, FONT_HEADING,
    COMPARISON_GROUP_1, COMPARISON_GROUP_2,
)
from ui.components import (
    section_header, subheader,
    comparison_radar_chart, comparison_grouped_bar, comparison_stacked_bar,
    comparison_stat_row, comparison_mode_selector, comparison_legend,
)
from ui.formatters import format_sg, format_pct


# ============================================================
# CONSTANTS
# ============================================================

SG_CATEGORIES = ["Driving", "Approach", "Short Game", "Putting"]
APPROACH_BUCKETS = ["50–100", "100–150", "150–200", ">200"]
PUTTING_BUCKETS = ["<5", "5-10", "10-20", "20-30", "30+"]
SHORT_GAME_BUCKETS = ["<10", "10-20", "20-30", "30-40", "40-50"]
OUTCOME_LABELS = ["Eagle", "Birdie", "Par", "Bogey", "Double or Worse"]
TIGER5_LABELS = ["3 Putts", "Double Bogey", "Par 5 Bogey", "Missed Green", "125yd Bogey"]


# ============================================================
# SECTION 1: MODE SELECTOR
# ============================================================

def render_mode_selector(players):
    """Render the comparison mode selector."""
    mode, mode_params = comparison_mode_selector(players)
    return mode, mode_params


# ============================================================
# SECTION 1B: GROUP SUMMARY (shown after mode selection)
# ============================================================

def render_group_summary(comparison_data):
    """Render small summary text for each group."""
    group1 = comparison_data['group1']
    group2 = comparison_data['group2']
    g1_label = comparison_data['group1_label']
    g2_label = comparison_data['group2_label']
    
    # Format summary text for each group
    g1_summary = f"""
    <div style="font-family:{FONT_BODY};font-size:0.75rem;color:{CHARCOAL};line-height:1.6;">
        <span style="color:{COMPARISON_GROUP_1};font-weight:600;">{g1_label}:</span>
        {group1['num_rounds']} rounds | Avg: {group1['scoring_avg']:.1f} | 
        SG: {group1['total_sg']:+.1f} ({group1['sg_per_round']:+.2f}/r) |
        Low: {group1['low_score']} | High: {group1['high_score']}
    </div>
    """
    
    g2_summary = f"""
    <div style="font-family:{FONT_BODY};font-size:0.75rem;color:{CHARCOAL};line-height:1.6;">
        <span style="color:{COMPARISON_GROUP_2};font-weight:600;">{g2_label}:</span>
        {group2['num_rounds']} rounds | Avg: {group2['scoring_avg']:.1f} | 
        SG: {group2['total_sg']:+.1f} ({group2['sg_per_round']:+.2f}/r) |
        Low: {group2['low_score']} | High: {group2['high_score']}
    </div>
    """
    
    st.markdown(g1_summary + "<br>" + g2_summary, unsafe_allow_html=True)


# ============================================================
# SECTION 2: RADAR CHARTS
# ============================================================

def render_radar_charts(comparison_data):
    """Render 4 radar charts comparing two groups."""
    section_header("Radar Comparison")
    
    group1 = comparison_data['group1']
    group2 = comparison_data['group2']
    g1_label = comparison_data['group1_label']
    g2_label = comparison_data['group2_label']
    
    comparison_legend(g1_label, g2_label)
    
    # Chart 2a: Major SG Categories
    subheader("Major Strokes Gained Categories")
    g1_sg = [group1['sg_by_category'].get(cat, 0) for cat in SG_CATEGORIES]
    g2_sg = [group2['sg_by_category'].get(cat, 0) for cat in SG_CATEGORIES]
    comparison_radar_chart(
        SG_CATEGORIES, g1_sg, g2_sg,
        g1_label, g2_label,
        "Strokes Gained by Category"
    )
    
    # Chart 2b: Approach by Distance
    subheader("Approach Shots by Distance")
    g1_app = [group1['approach_by_bucket'].get(b, 0) for b in APPROACH_BUCKETS]
    g2_app = [group2['approach_by_bucket'].get(b, 0) for b in APPROACH_BUCKETS]
    comparison_radar_chart(
        APPROACH_BUCKETS, g1_app, g2_app,
        g1_label, g2_label,
        "Approach SG by Distance"
    )
    
    # Chart 2c: Putting by Distance
    subheader("Putting by Distance")
    g1_putt = [group1['putting_by_bucket'].get(b, 0) for b in PUTTING_BUCKETS]
    g2_putt = [group2['putting_by_bucket'].get(b, 0) for b in PUTTING_BUCKETS]
    comparison_radar_chart(
        PUTTING_BUCKETS, g1_putt, g2_putt,
        g1_label, g2_label,
        "Putting SG by Distance"
    )
    
    # Chart 2d: Short Game by Distance
    subheader("Short Game by Distance")
    g1_sg_bucket = [group1['short_game_by_bucket'].get(b, 0) for b in SHORT_GAME_BUCKETS]
    g2_sg_bucket = [group2['short_game_by_bucket'].get(b, 0) for b in SHORT_GAME_BUCKETS]
    comparison_radar_chart(
        SHORT_GAME_BUCKETS, g1_sg_bucket, g2_sg_bucket,
        g1_label, g2_label,
        "Short Game SG by Distance"
    )


# ============================================================
# SECTION 3: HOLE OUTCOMES
# ============================================================

def render_hole_outcomes(comparison_data):
    """Render hole outcome distribution comparison."""
    section_header("Hole Outcome Distribution")
    
    group1 = comparison_data['group1']
    group2 = comparison_data['group2']
    g1_label = comparison_data['group1_label']
    g2_label = comparison_data['group2_label']
    
    # Get counts for each outcome
    g1_outcomes = [group1['hole_outcomes'].get(label, 0) for label in OUTCOME_LABELS]
    g2_outcomes = [group2['hole_outcomes'].get(label, 0) for label in OUTCOME_LABELS]
    
    # Calculate percentages
    g1_total = sum(g1_outcomes) if sum(g1_outcomes) > 0 else 1
    g2_total = sum(g2_outcomes) if sum(g2_outcomes) > 0 else 1
    
    g1_pcts = [c / g1_total * 100 for c in g1_outcomes]
    g2_pcts = [c / g2_total * 100 for c in g2_outcomes]
    
    # Render grouped bar chart
    comparison_grouped_bar(
        OUTCOME_LABELS, g1_outcomes, g2_outcomes,
        g1_label, g2_label,
        "Hole Outcomes (Count)",
    )
    
    # Show summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
            <div style="background:#F8F7F4;padding:1rem;border-radius:10px;
                 text-align:center;border-left:4px solid {COMPARISON_GROUP_1};">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     text-transform:uppercase;letter-spacing:0.08em;">{g1_label}</div>
                <div style="font-family:{FONT_HEADING};font-size:1.2rem;font-weight:600;
                     color:{CHARCOAL};margin:0.5rem 0;">
                     Birdies: {group1['hole_outcomes'].get('Birdie', 0)}</div>
                <div style="font-family:{FONT_BODY};font-size:0.7rem;color:{SLATE};">
                     Bogeys: {group1['hole_outcomes'].get('Bogey', 0)}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
            <div style="background:#F8F7F4;padding:1rem;border-radius:10px;
                 text-align:center;border-left:4px solid {COMPARISON_GROUP_2};">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     text-transform:uppercase;letter-spacing:0.08em;">{g2_label}</div>
                <div style="font-family:{FONT_HEADING};font-size:1.2rem;font-weight:600;
                     color:{CHARCOAL};margin:0.5rem 0;">
                     Birdies: {group2['hole_outcomes'].get('Birdie', 0)}</div>
                <div style="font-family:{FONT_BODY};font-size:0.7rem;color:{SLATE};">
                     Bogeys: {group2['hole_outcomes'].get('Bogey', 0)}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        # Bogey+ percentage
        g1_bogey_pct = g1_pcts[OUTCOME_LABELS.index('Bogey')] + g1_pcts[OUTCOME_LABELS.index('Double or Worse')]
        g2_bogey_pct = g2_pcts[OUTCOME_LABELS.index('Bogey')] + g2_pcts[OUTCOME_LABELS.index('Double or Worse')]
        st.markdown(f'''
            <div style="background:#F8F7F4;padding:1rem;border-radius:10px;
                 text-align:center;">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     text-transform:uppercase;letter-spacing:0.08em;">Bogey+ Rate</div>
                <div style="font-family:{FONT_HEADING};font-size:1rem;font-weight:600;
                     color:{COMPARISON_GROUP_1};margin:0.3rem 0;">{g1_label}: {g1_bogey_pct:.0f}%</div>
                <div style="font-family:{FONT_HEADING};font-size:1rem;font-weight:600;
                     color:{COMPARISON_GROUP_2};margin:0.3rem 0;">{g2_label}: {g2_bogey_pct:.0f}%</div>
            </div>
        ''', unsafe_allow_html=True)


# ============================================================
# SECTION 4: TIGER 5 COMPARISON
# ============================================================

def render_tiger5_comparison(comparison_data):
    """Render Tiger 5 comparison section."""
    section_header("Tiger 5 Comparison")
    
    group1 = comparison_data['group1']
    group2 = comparison_data['group2']
    g1_label = comparison_data['group1_label']
    g2_label = comparison_data['group2_label']
    
    g1_t5 = group1['tiger5']['by_category']
    g2_t5 = group2['tiger5']['by_category']
    
    g1_totals = [g1_t5.get(label, 0) for label in TIGER5_LABELS]
    g2_totals = [g2_t5.get(label, 0) for label in TIGER5_LABELS]
    
    # Grouped bar chart for Tiger 5 categories
    comparison_grouped_bar(
        TIGER5_LABELS, g1_totals, g2_totals,
        g1_label, g2_label,
        "Tiger 5 Failures by Category",
    )
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
            <div style="background:#FFF5F5;padding:1rem;border-radius:10px;
                 text-align:center;border:1px solid #FED7D7;">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     text-transform:uppercase;letter-spacing:0.08em;">{g1_label} Total Fails</div>
                <div style="font-family:{FONT_HEADING};font-size:2rem;font-weight:700;
                     color:{COMPARISON_GROUP_1};">{group1['tiger5']['total_fails']}</div>
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     margin-top:0.3rem;">Grit: {group1['tiger5']['grit_score']:.0f}%</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
            <div style="background:#F8F7F4;padding:1rem;border-radius:10px;
                 text-align:center;border:1px solid #E2E8F0;">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     text-transform:uppercase;letter-spacing:0.08em;">{g2_label} Total Fails</div>
                <div style="font-family:{FONT_HEADING};font-size:2rem;font-weight:700;
                     color:{COMPARISON_GROUP_2};">{group2['tiger5']['total_fails']}</div>
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     margin-top:0.3rem;">Grit: {group2['tiger5']['grit_score']:.0f}%</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        # Biggest difference
        diff = group2['tiger5']['total_fails'] - group1['tiger5']['total_fails']
        diff_color = "#2D6A4F" if diff < 0 else "#C53030"
        diff_text = f"{diff:+.0f}" if diff >= 0 else f"{diff:.0f}"
        st.markdown(f'''
            <div style="background:#F8F7F4;padding:1rem;border-radius:10px;
                 text-align:center;border:1px solid #E2E8F0;">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     text-transform:uppercase;letter-spacing:0.08em;">Difference</div>
                <div style="font-family:{FONT_HEADING};font-size:2rem;font-weight:700;
                     color:{diff_color};">{diff_text}</div>
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     margin-top:0.3rem;">{g2_label} more fails</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        # 3-Putt comparison
        g1_3putt = g1_t5.get('3 Putts', 0)
        g2_3putt = g2_t5.get('3 Putts', 0)
        st.markdown(f'''
            <div style="background:#FFF5F5;padding:1rem;border-radius:10px;
                 text-align:center;border:1px solid #FED7D7;">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                     text-transform:uppercase;letter-spacing:0.08em;">3-Putts</div>
                <div style="display:flex;justify-content:center;gap:1rem;margin-top:0.5rem;">
                    <span style="color:{COMPARISON_GROUP_1};font-weight:600;">{g1_3putt}</span>
                    <span style="color:{SLATE};">vs</span>
                    <span style="color:{COMPARISON_GROUP_2};font-weight:600;">{g2_3putt}</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)


# ============================================================
# SECTION 5: MENTAL CHARACTERISTICS
# ============================================================

def render_mental_comparison(comparison_data):
    """Render mental characteristics comparison."""
    section_header("Mental Characteristics & Round Flow")
    
    group1 = comparison_data['group1']
    group2 = comparison_data['group2']
    g1_label = comparison_data['group1_label']
    g2_label = comparison_data['group2_label']
    
    m1 = group1['mental_metrics']
    m2 = group2['mental_metrics']
    
    # Round Flow metrics row
    subheader("Round Flow")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        comparison_stat_row(
            g1_label, format_pct(m1['bounce_back']['rate']),
            g2_label, format_pct(m2['bounce_back']['rate']),
            "Bounce Back %",
        )
    
    with col2:
        comparison_stat_row(
            g1_label, format_pct(m1['gas_pedal']['rate']),
            g2_label, format_pct(m2['gas_pedal']['rate']),
            "Gas Pedal %",
        )
    
    with col3:
        comparison_stat_row(
            g1_label, format_pct(m1['drop_off']['rate']),
            g2_label, format_pct(m2['drop_off']['rate']),
            "Drop Off %",
        )
    
    with col4:
        comparison_stat_row(
            g1_label, format_pct(m1['bogey_train_rate']['btr']),
            g2_label, format_pct(m2['bogey_train_rate']['btr']),
            "Bogey Train %",
        )
    
    st.markdown("---")
    
    # Detailed breakdown
    subheader("Detailed Mental Metrics")
    
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown(f"**{g1_label}**")
        st.markdown(f"- Bounce Back: {m1['bounce_back']['successes']}/{m1['bounce_back']['opportunities']} ({format_pct(m1['bounce_back']['rate'])})")
        st.markdown(f"- Gas Pedal: {m1['gas_pedal']['successes']}/{m1['gas_pedal']['opportunities']} ({format_pct(m1['gas_pedal']['rate'])})")
        st.markdown(f"- Drop Off: {m1['drop_off']['events']}/{m1['drop_off']['opportunities']} ({format_pct(m1['drop_off']['rate'])})")
        st.markdown(f"- Bogey Trains: Longest streak {m1['bogey_train_rate']['longest']} holes")
    
    with colB:
        st.markdown(f"**{g2_label}**")
        st.markdown(f"- Bounce Back: {m2['bounce_back']['successes']}/{m2['bounce_back']['opportunities']} ({format_pct(m2['bounce_back']['rate'])})")
        st.markdown(f"- Gas Pedal: {m2['gas_pedal']['successes']}/{m2['gas_pedal']['opportunities']} ({format_pct(m2['gas_pedal']['rate'])})")
        st.markdown(f"- Drop Off: {m2['drop_off']['events']}/{m2['drop_off']['opportunities']} ({format_pct(m2['drop_off']['rate'])})")
        st.markdown(f"- Bogey Trains: Longest streak {m2['bogey_train_rate']['longest']} holes")


# ============================================================
# SECTION 6: BASIC STATS
# ============================================================

def render_basic_stats(comparison_data):
    """Render basic stats comparison."""
    section_header("Basic Statistics")
    
    group1 = comparison_data['group1']
    group2 = comparison_data['group2']
    g1_label = comparison_data['group1_label']
    g2_label = comparison_data['group2_label']
    
    s1 = group1['basic_stats']
    s2 = group2['basic_stats']
    
    # Row 1: FW%, GIR%, Penalties
    col1, col2, col3 = st.columns(3)
    
    with col1:
        comparison_stat_row(
            g1_label, format_pct(s1['fw_pct']),
            g2_label, format_pct(s2['fw_pct']),
            "Fairway %",
        )
    
    with col2:
        comparison_stat_row(
            g1_label, format_pct(s1['gir_pct']),
            g2_label, format_pct(s2['gir_pct']),
            "GIR %",
        )
    
    with col3:
        comparison_stat_row(
            g1_label, str(s1['penalties']),
            g2_label, str(s2['penalties']),
            "Penalties",
        )
    
    # Row 2: Rounds and Scoring Average
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown(f'''
            <div style="background:#F8F7F4;padding:1rem;border-radius:10px;
                 border:1px solid #E2E8F0;">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                    <div style="text-align:center;">
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                             text-transform:uppercase;letter-spacing:0.08em;">{g1_label}</div>
                        <div style="font-family:{FONT_HEADING};font-size:1.8rem;font-weight:700;
                             color:{COMPARISON_GROUP_1};">{group1['num_rounds']}</div>
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};">Rounds</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                             text-transform:uppercase;letter-spacing:0.08em;">{g2_label}</div>
                        <div style="font-family:{FONT_HEADING};font-size:1.8rem;font-weight:700;
                             color:{COMPARISON_GROUP_2};">{group2['num_rounds']}</div>
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};">Rounds</div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col5:
        st.markdown(f'''
            <div style="background:#F8F7F4;padding:1rem;border-radius:10px;
                 border:1px solid #E2E8F0;">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                    <div style="text-align:center;">
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                             text-transform:uppercase;letter-spacing:0.08em;">{g1_label}</div>
                        <div style="font-family:{FONT_HEADING};font-size:1.8rem;font-weight:700;
                             color:{COMPARISON_GROUP_1};">{group1['scoring_avg']:.2f}</div>
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};">Scoring Avg</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};
                             text-transform:uppercase;letter-spacing:0.08em;">{g2_label}</div>
                        <div style="font-family:{FONT_HEADING};font-size:1.8rem;font-weight:700;
                             color:{COMPARISON_GROUP_2};">{group2['scoring_avg']:.2f}</div>
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};">Scoring Avg</div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)


# ============================================================
# MAIN TAB RENDERER
# ============================================================

def comparison_tab(filtered_df, hole_summary):
    """
    Main entry point for Comparison tab.
    Renders all 6 sections in order.
    """
    # Get unique players for selector
    players = sorted(filtered_df['Player'].unique()) if not filtered_df.empty else []
    
    # Section 1: Mode Selector
    mode, mode_params = render_mode_selector(players)
    
    # Import comparison engine
    from engines.comparison import build_comparison_data
    
    # Build comparison data
    comparison_data = build_comparison_data(
        filtered_df, hole_summary, mode, mode_params
    )
    
    # Check if we have valid data
    if comparison_data['group1']['num_rounds'] == 0:
        st.warning(f"No data available for {comparison_data['group1_label']}. Please adjust your filters or selection.")
        return
    
    if comparison_data['group2']['num_rounds'] == 0:
        st.warning(f"No data available for {comparison_data['group2_label']}. Please adjust your filters or selection.")
        return
    
    st.markdown("---")
    
    # Group Summary - shown after mode selection, before radar charts
    render_group_summary(comparison_data)
    
    st.markdown("---")
    
    # Section 2: Radar Charts
    render_radar_charts(comparison_data)
    
    st.markdown("---")
    
    # Section 3: Hole Outcomes
    render_hole_outcomes(comparison_data)
    
    st.markdown("---")
    
    # Section 4: Tiger 5 Comparison
    render_tiger5_comparison(comparison_data)
    
    st.markdown("---")
    
    # Section 5: Mental Characteristics
    render_mental_comparison(comparison_data)
    
    st.markdown("---")
    
    # Section 6: Basic Stats
    render_basic_stats(comparison_data)
