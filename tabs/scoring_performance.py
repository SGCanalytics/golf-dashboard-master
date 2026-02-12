# ============================================================
# TAB: SCORING PERFORMANCE
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from ui.theme import (
    CHARCOAL, CHARCOAL_LIGHT, POSITIVE, NEGATIVE, ACCENT_PRIMARY, ACCENT_SECONDARY,
    WARNING, CHART_PUTTING, CHART_PALETTE, DONUT_SEQUENCE,
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

    root_cause_names = ['Short Putts', 'Mid-range Putts', 'Lag Putts', 'Driving', 'Approach', 'Short Game', 'Recovery and Other']

    # ------------------------------------------------------------
    # TOTAL FAIL CARD + CATEGORY BREAKDOWN CARDS
    # ------------------------------------------------------------
    section_header("Scoring Performance Overview")

    total_fails = scoring_perf_results['total_fails']
    total_sg_sum = sum(scoring_perf_results['total_sg_sums'].values())
    category_counts = scoring_perf_results['category_counts']
    category_sg_sums = scoring_perf_results['category_sg_sums']

    # Large total fail card
    st.markdown(f'''
        <div style="background:linear-gradient(135deg,{CHARCOAL} 0%,{CHARCOAL_LIGHT} 100%);
             border-radius:12px;padding:2rem 1.5rem;text-align:center;
             border:none;margin-bottom:1.5rem;">
            <div style="font-family:Inter;font-size:0.8rem;font-weight:600;
                 color:rgba(255,255,255,0.9);text-transform:uppercase;
                 letter-spacing:0.08em;margin-bottom:0.75rem;">Total Scoring Fails</div>
            <div style="font-family:Playfair Display,serif;font-size:3.5rem;
                 font-weight:700;color:#ffffff;line-height:1;margin-bottom:0.5rem;">
                {total_fails}</div>
            <div style="font-family:Inter;font-size:0.75rem;
                 color:rgba(255,255,255,0.8);">
                Total SG Impact: {format_sg(total_sg_sum)}</div>
        </div>
    ''', unsafe_allow_html=True)

    # 3 category breakdown cards
    col_db, col_bog, col_under = st.columns(3)

    with col_db:
        db_count = category_counts['double_bogey_plus']
        db_sg = category_sg_sums['double_bogey_plus']
        db_pct = (db_count / total_fails * 100) if total_fails > 0 else 0

        st.markdown(f'''
            <div style="background:linear-gradient(135deg,{NEGATIVE} 0%,{NEGATIVE}dd 100%);
                 border-radius:12px;padding:1.5rem 1rem;text-align:center;
                 border:none;margin-bottom:1rem;">
                <div style="font-family:Inter;font-size:0.75rem;font-weight:600;
                     color:rgba(255,255,255,0.9);text-transform:uppercase;
                     letter-spacing:0.08em;margin-bottom:0.5rem;">Double Bogey+</div>
                <div style="font-family:Playfair Display,serif;font-size:2.75rem;
                     font-weight:700;color:#ffffff;line-height:1;margin-bottom:0.25rem;">
                    {db_count}</div>
                <div style="font-family:Inter;font-size:0.65rem;
                     color:rgba(255,255,255,0.7);">{db_pct:.0f}% of fails</div>
                <div style="font-family:Inter;font-size:0.65rem;
                     color:rgba(255,255,255,0.8);margin-top:0.5rem;">
                    SG Impact: {format_sg(db_sg)}</div>
            </div>
        ''', unsafe_allow_html=True)

    with col_bog:
        bog_count = category_counts['bogey']
        bog_sg = category_sg_sums['bogey']
        bog_pct = (bog_count / total_fails * 100) if total_fails > 0 else 0

        st.markdown(f'''
            <div style="background:linear-gradient(135deg,{WARNING} 0%,{WARNING}dd 100%);
                 border-radius:12px;padding:1.5rem 1rem;text-align:center;
                 border:none;margin-bottom:1rem;">
                <div style="font-family:Inter;font-size:0.75rem;font-weight:600;
                     color:rgba(255,255,255,0.9);text-transform:uppercase;
                     letter-spacing:0.08em;margin-bottom:0.5rem;">Bogey</div>
                <div style="font-family:Playfair Display,serif;font-size:2.75rem;
                     font-weight:700;color:#ffffff;line-height:1;margin-bottom:0.25rem;">
                    {bog_count}</div>
                <div style="font-family:Inter;font-size:0.65rem;
                     color:rgba(255,255,255,0.7);">{bog_pct:.0f}% of fails</div>
                <div style="font-family:Inter;font-size:0.65rem;
                     color:rgba(255,255,255,0.8);margin-top:0.5rem;">
                    SG Impact: {format_sg(bog_sg)}</div>
            </div>
        ''', unsafe_allow_html=True)

    with col_under:
        under_count = category_counts['underperformance']
        under_sg = category_sg_sums['underperformance']
        under_pct = (under_count / total_fails * 100) if total_fails > 0 else 0

        st.markdown(f'''
            <div style="background:linear-gradient(135deg,{ACCENT_SECONDARY} 0%,{ACCENT_SECONDARY}dd 100%);
                 border-radius:12px;padding:1.5rem 1rem;text-align:center;
                 border:none;margin-bottom:1rem;">
                <div style="font-family:Inter;font-size:0.75rem;font-weight:600;
                     color:rgba(255,255,255,0.9);text-transform:uppercase;
                     letter-spacing:0.08em;margin-bottom:0.5rem;">Underperformance</div>
                <div style="font-family:Playfair Display,serif;font-size:2.75rem;
                     font-weight:700;color:#ffffff;line-height:1;margin-bottom:0.25rem;">
                    {under_count}</div>
                <div style="font-family:Inter;font-size:0.65rem;
                     color:rgba(255,255,255,0.7);">{under_pct:.0f}% of fails</div>
                <div style="font-family:Inter;font-size:0.65rem;
                     color:rgba(255,255,255,0.8);margin-top:0.5rem;">
                    SG Impact: {format_sg(under_sg)}</div>
            </div>
        ''', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # HERO CARDS — ROOT CAUSE COUNTS (8 cards, sorted by count)
    # ------------------------------------------------------------
    section_header("Scoring Issues by Root Cause")

    total_fails = scoring_perf_results['total_fails']
    total_counts = scoring_perf_results['total_counts']
    total_sg_sums = scoring_perf_results['total_sg_sums']

    # Color mapping for 8 categories
    rc_color_map = {
        'Short Putts': CHART_PALETTE[4],      # Purple
        'Mid-range Putts': CHART_PALETTE[3],  # Teal
        'Lag Putts': CHART_PALETTE[5],        # Gold
        'Driving': ACCENT_PRIMARY,             # Blue
        'Approach': CHARCOAL,                  # Charcoal
        'Short Game': POSITIVE,                # Green
        'Recovery and Other': NEGATIVE         # Red
    }

    # Sort root causes by count (descending)
    sorted_root_causes = sorted(
        root_cause_names,
        key=lambda rc: total_counts.get(rc, 0),
        reverse=True
    )

    # Display in 2 rows of 4
    for row_idx in range(2):
        cols = st.columns(4)
        start_idx = row_idx * 4
        end_idx = start_idx + 4

        for col_idx, col in enumerate(cols):
            rc_idx = start_idx + col_idx
            if rc_idx < len(sorted_root_causes):
                rc_name = sorted_root_causes[rc_idx]
                count = total_counts.get(rc_name, 0)
                sg_sum = total_sg_sums.get(rc_name, 0.0)
                pct = (count / total_fails * 100) if total_fails > 0 else 0
                color = rc_color_map.get(rc_name, CHARCOAL)

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
                            <div style="font-family:Inter;font-size:0.65rem;
                                 color:rgba(255,255,255,0.8);margin-top:0.5rem;">
                                SG: {format_sg(sg_sum)}</div>
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

            # Add stacked bars for each root cause (in sorted order)
            for rc_name in sorted_root_causes:
                color = rc_color_map.get(rc_name, CHARCOAL)
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
    # ROOT CAUSE DETAILS (shot-level breakdown)
    # ------------------------------------------------------------
    with st.expander("View Root Cause Details"):
        shot_details = scoring_perf_results['shot_details']
        any_details = False

        for rc_name in sorted_root_causes:
            holes = shot_details.get(rc_name, [])
            if holes:
                any_details = True
                st.markdown(f"#### {rc_name}")
                for hole_data in holes:
                    tournament_display = hole_data.get('tournament', 'Unknown Tournament')
                    st.markdown(
                        f"**{tournament_display} &mdash; "
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
    # ACTUAL VS POTENTIAL SCORE
    # ------------------------------------------------------------
    section_header("Scoring Impact Analysis")

    scoring_impact = scoring_perf_results['scoring_impact']

    if not scoring_impact.empty:
        # Summary stats
        total_actual = scoring_impact['Total Score'].sum()
        total_potential = scoring_impact['Potential Score'].sum()
        strokes_saved = total_actual - total_potential

        s1, s2, s3 = st.columns(3)

        with s1:
            premium_stat_card(
                "Total Actual Strokes",
                f"{int(total_actual)}",
                sentiment="neutral"
            )

        with s2:
            premium_stat_card(
                "Potential Strokes",
                f"{int(total_potential)}",
                sentiment="positive"
            )

        with s3:
            premium_stat_card(
                "Strokes Saved (50% Fix)",
                f"{int(strokes_saved)}",
                sentiment="positive"
            )

        # Grouped bar chart
        with st.expander("View Actual vs Potential Scores by Round"):
            fig_impact = go.Figure()

            # Actual scores
            fig_impact.add_trace(go.Bar(
                x=scoring_impact['Label'],
                y=scoring_impact['Total Score'],
                name='Actual Score',
                marker_color=CHARCOAL,
                text=scoring_impact['Total Score'],
                textposition='outside'
            ))

            # Potential scores
            fig_impact.add_trace(go.Bar(
                x=scoring_impact['Label'],
                y=scoring_impact['Potential Score'],
                name='Potential Score',
                marker_color=POSITIVE,
                text=scoring_impact['Potential Score'],
                textposition='outside'
            ))

            fig_impact.update_layout(
                **CHART_LAYOUT,
                barmode='group',
                xaxis_title='',
                yaxis_title='Score',
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

            st.plotly_chart(fig_impact, use_container_width=True,
                            config={'displayModeBar': False})
    else:
        st.info("No scoring impact data available.")

    # ------------------------------------------------------------
    # CATEGORY BREAKDOWN — GROUPED BAR CHART
    # ------------------------------------------------------------
    section_header("Breakdown by Issue Type")

    db_analysis = scoring_perf_results['double_bogey_analysis']
    bogey_analysis = scoring_perf_results['bogey_analysis']
    underperf_analysis = scoring_perf_results['underperformance_analysis']

    # Create grouped bar chart
    with st.expander("View Root Cause Distribution by Issue Type"):
        fig_breakdown = go.Figure()

        # Double Bogey+ bars
        db_counts = [db_analysis['counts'].get(rc, 0) for rc in sorted_root_causes]
        fig_breakdown.add_trace(go.Bar(
            x=sorted_root_causes,
            y=db_counts,
            name='Double Bogey+',
            marker_color=NEGATIVE,
            text=db_counts,
            textposition='outside'
        ))

        # Bogey bars
        bogey_counts = [bogey_analysis['counts'].get(rc, 0) for rc in sorted_root_causes]
        fig_breakdown.add_trace(go.Bar(
            x=sorted_root_causes,
            y=bogey_counts,
            name='Bogey',
            marker_color=WARNING,
            text=bogey_counts,
            textposition='outside'
        ))

        # Underperformance bars
        under_counts = [underperf_analysis['counts'].get(rc, 0) for rc in sorted_root_causes]
        fig_breakdown.add_trace(go.Bar(
            x=sorted_root_causes,
            y=under_counts,
            name='Underperformance',
            marker_color=ACCENT_SECONDARY,
            text=under_counts,
            textposition='outside'
        ))

        fig_breakdown.update_layout(
            **CHART_LAYOUT,
            barmode='group',
            xaxis_title='Root Cause',
            yaxis_title='Count',
            height=450,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(t=60, b=100, l=60, r=60),
            xaxis=dict(tickangle=-45),
            hovermode='x unified'
        )

        st.plotly_chart(fig_breakdown, use_container_width=True,
                        config={'displayModeBar': False})

    # Summary tables below the chart
    col_sum1, col_sum2, col_sum3 = st.columns(3)

    with col_sum1:
        st.markdown("**Double Bogey+ Summary**")
        st.markdown(f"Total Holes: {len(db_analysis['holes'])}")
        if db_analysis['counts']:
            sorted_db = sorted(db_analysis['counts'].items(), key=lambda x: x[1], reverse=True)
            for rc, count in sorted_db[:3]:
                if count > 0:
                    pct = (count / len(db_analysis['holes']) * 100) if len(db_analysis['holes']) > 0 else 0
                    st.markdown(f"- {rc}: {count} ({pct:.0f}%)")

    with col_sum2:
        st.markdown("**Bogey Summary**")
        st.markdown(f"Total Holes: {len(bogey_analysis['holes'])}")
        if bogey_analysis['counts']:
            sorted_bog = sorted(bogey_analysis['counts'].items(), key=lambda x: x[1], reverse=True)
            for rc, count in sorted_bog[:3]:
                if count > 0:
                    pct = (count / len(bogey_analysis['holes']) * 100) if len(bogey_analysis['holes']) > 0 else 0
                    st.markdown(f"- {rc}: {count} ({pct:.0f}%)")

    with col_sum3:
        st.markdown("**Underperformance Summary**")
        st.markdown(f"Total Holes: {len(underperf_analysis['holes'])}")
        if underperf_analysis['counts']:
            sorted_under = sorted(underperf_analysis['counts'].items(), key=lambda x: x[1], reverse=True)
            for rc, count in sorted_under[:3]:
                if count > 0:
                    pct = (count / len(underperf_analysis['holes']) * 100) if len(underperf_analysis['holes']) > 0 else 0
                    st.markdown(f"- {rc}: {count} ({pct:.0f}%)")
