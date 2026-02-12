# ============================================================
# TAB: SCORING PERFORMANCE
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from ui.theme import (
    CHARCOAL, POSITIVE, NEGATIVE, ACCENT_PRIMARY, ACCENT_SECONDARY,
    CHART_PUTTING, CHART_PALETTE, DONUT_SEQUENCE,
)
from ui.chart_config import CHART_LAYOUT, sg_bar_color
from ui.components import (
    section_header, premium_hero_card, premium_stat_card, sg_sentiment,
)
from ui.formatters import format_sg, format_pct, format_date


def scoring_perf_tab(filtered_df, hole_summary, scoring_perf_results):
    """
    Scoring Performance tab showing root cause analysis for:
    - Double Bogey+ holes
    - Bogey holes
    - Underperformance holes (par or better with 3-putt or short game miss)
    """

    root_cause_names = ['Short Putts', 'Lag Putts', 'Driving', 'Approach', 'Short Game', 'Recovery and Other']

    # ------------------------------------------------------------
    # HERO CARDS — ROOT CAUSE COUNTS
    # ------------------------------------------------------------
    section_header("Scoring Issues by Root Cause")

    total_fails = scoring_perf_results['total_fails']
    total_counts = scoring_perf_results['total_counts']

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # Colors for each root cause category (using theme colors)
    rc_colors = [
        CHART_PALETTE[4],  # Short Putts (purple)
        CHART_PALETTE[5],  # Lag Putts (gold)
        ACCENT_PRIMARY,    # Driving
        CHARCOAL,          # Approach
        POSITIVE,          # Short Game
        NEGATIVE           # Recovery and Other
    ]

    for col, rc_name, color in zip([col1, col2, col3, col4, col5, col6], root_cause_names, rc_colors):
        count = total_counts[rc_name]
        pct = (count / total_fails * 100) if total_fails > 0 else 0

        with col:
            st.markdown(f'''
                <div style="background:linear-gradient(135deg,{color} 0%,{color}dd 100%);
                     border-radius:12px;padding:1.25rem 1rem;text-align:center;
                     border:none;margin-bottom:1rem;">
                    <div style="font-family:Inter;font-size:0.7rem;font-weight:600;
                         color:rgba(255,255,255,0.9);text-transform:uppercase;
                         letter-spacing:0.08em;margin-bottom:0.5rem;">{rc_name}</div>
                    <div style="font-family:Playfair Display,serif;font-size:2.25rem;
                         font-weight:700;color:#ffffff;line-height:1;margin-bottom:0.25rem;">
                        {count}</div>
                    <div style="font-family:Inter;font-size:0.65rem;
                         color:rgba(255,255,255,0.7);text-transform:uppercase;
                         letter-spacing:0.05em;">{pct:.0f}% of fails</div>
                </div>
            ''', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # TREND CHART (stacked bar by round + line overlay)
    # ------------------------------------------------------------
    with st.expander("View Scoring Issues Trend by Round"):
        by_round = scoring_perf_results['by_round']

        if not by_round.empty:
            by_round = by_round.copy()

            fig_sp = go.Figure()

            # Add stacked bars for each root cause
            for rc_name, color in zip(root_cause_names, rc_colors):
                fig_sp.add_trace(go.Bar(
                    x=by_round['Label'],
                    y=by_round[rc_name],
                    name=rc_name,
                    marker_color=color
                ))

            # Add line for total fails
            fig_sp.add_trace(go.Scatter(
                x=by_round['Label'],
                y=by_round['Total Fails'],
                name='Total Fails',
                mode='lines+markers',
                line=dict(color=CHARCOAL, width=3),
                marker=dict(size=8, color=CHARCOAL),
                yaxis='y2'
            ))

            fig_sp.update_layout(
                **CHART_LAYOUT,
                barmode='stack',
                xaxis_title='',
                yaxis_title='Issues by Root Cause',
                yaxis2=dict(
                    title='Total Fails',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                height=400,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                margin=dict(t=60, b=80, l=60, r=60),
                xaxis=dict(tickangle=-45),
                hovermode='x unified'
            )

            st.plotly_chart(fig_sp, use_container_width=True,
                            config={'displayModeBar': False})
        else:
            st.info("No data available for scoring issues trend.")

    # ------------------------------------------------------------
    # PENALTY ANALYSIS
    # ------------------------------------------------------------
    section_header("Penalty Impact Analysis")

    penalty_stats = scoring_perf_results['penalty_stats']

    p1, p2, p3 = st.columns(3)

    with p1:
        premium_stat_card(
            "Bogey with Penalty",
            f"{penalty_stats['bogey_penalty_pct']:.1f}%",
            sentiment="neutral"
        )

    with p2:
        premium_stat_card(
            "Double+ with Penalty",
            f"{penalty_stats['db_penalty_pct']:.1f}%",
            sentiment="neutral"
        )

    with p3:
        premium_stat_card(
            "Double+ with 2+ Bad Shots",
            f"{penalty_stats['db_multiple_bad_pct']:.1f}%",
            sentiment="neutral"
        )

    # ------------------------------------------------------------
    # ROOT CAUSE DETAILS (shot-level breakdown)
    # ------------------------------------------------------------
    with st.expander("View Root Cause Details"):
        shot_details = scoring_perf_results['shot_details']
        any_details = False

        for rc_name in root_cause_names:
            holes = shot_details.get(rc_name, [])
            if holes:
                any_details = True
                st.markdown(f"#### {rc_name}")
                for hole_data in holes:
                    st.markdown(
                        f"**{hole_data['date']} &mdash; "
                        f"{hole_data['course']} &mdash; "
                        f"Hole {hole_data['hole']}** "
                        f"(Par {hole_data['par']}, Score {hole_data['score']})"
                    )
                    st.dataframe(
                        hole_data['shots'],
                        use_container_width=True,
                        hide_index=True
                    )

        if not any_details:
            st.info("No scoring issues to display.")

    # ------------------------------------------------------------
    # CATEGORY BREAKDOWN (optional sub-tabs)
    # ------------------------------------------------------------
    section_header("Breakdown by Issue Type")

    tab_db, tab_bog, tab_under = st.tabs(["Double Bogey+", "Bogey", "Underperformance"])

    with tab_db:
        db_analysis = scoring_perf_results['double_bogey_analysis']
        st.markdown(f"**Total Holes:** {len(db_analysis['holes'])}")

        if db_analysis['counts']:
            # Show top 3 root causes
            sorted_causes = sorted(db_analysis['counts'].items(), key=lambda x: x[1], reverse=True)
            st.markdown("**Top Root Causes:**")
            for rc, count in sorted_causes[:3]:
                if count > 0:
                    pct = (count / len(db_analysis['holes']) * 100) if len(db_analysis['holes']) > 0 else 0
                    st.markdown(f"- {rc}: {count} ({pct:.0f}%)")

    with tab_bog:
        bogey_analysis = scoring_perf_results['bogey_analysis']
        st.markdown(f"**Total Holes:** {len(bogey_analysis['holes'])}")

        if bogey_analysis['counts']:
            sorted_causes = sorted(bogey_analysis['counts'].items(), key=lambda x: x[1], reverse=True)
            st.markdown("**Top Root Causes:**")
            for rc, count in sorted_causes[:3]:
                if count > 0:
                    pct = (count / len(bogey_analysis['holes']) * 100) if len(bogey_analysis['holes']) > 0 else 0
                    st.markdown(f"- {rc}: {count} ({pct:.0f}%)")

    with tab_under:
        underperf_analysis = scoring_perf_results['underperformance_analysis']
        st.markdown(f"**Total Holes:** {len(underperf_analysis['holes'])}")

        if underperf_analysis['counts']:
            sorted_causes = sorted(underperf_analysis['counts'].items(), key=lambda x: x[1], reverse=True)
            st.markdown("**Top Root Causes:**")
            for rc, count in sorted_causes[:3]:
                if count > 0:
                    pct = (count / len(underperf_analysis['holes']) * 100) if len(underperf_analysis['holes']) > 0 else 0
                    st.markdown(f"- {rc}: {count} ({pct:.0f}%)")
