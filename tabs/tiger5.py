# ============================================================
# TAB: TIGER 5
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

from engines.overview import build_tiger5_fail_shots
from engines.tiger5 import build_tiger5_root_cause, build_tiger5_scoring_impact


def tiger5_tab(filtered_df, hole_summary, tiger5_results, total_tiger5_fails):

    tiger5_names = ['3 Putts', 'Double Bogey', 'Par 5 Bogey',
                    'Missed Green', '125yd Bogey']

    # ----------------------------------------------------------------
    # HERO CARD — TOTAL TIGER 5 FAILS
    # ----------------------------------------------------------------
    sentiment = "negative" if total_tiger5_fails > 0 else "positive"
    premium_hero_card(
        "Total Tiger 5 Fails",
        str(total_tiger5_fails),
        "across all filtered rounds",
        sentiment=sentiment,
    )

    # ----------------------------------------------------------------
    # TIGER 5 PERFORMANCE CARDS
    # ----------------------------------------------------------------
    section_header("Tiger 5 Performance")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    for col, stat_name in zip([col1, col2, col3, col4, col5], tiger5_names):
        fails = int(tiger5_results[stat_name]['fails'])
        attempts = int(tiger5_results[stat_name]['attempts'])
        sentiment = "negative" if fails > 0 else "positive"
        with col:
            premium_hero_card(stat_name, str(fails), f"of {attempts}",
                              sentiment=sentiment)

    with col6:
        grit_score = tiger5_results["grit_score"]
        premium_hero_card("Grit Score", format_pct(grit_score),
                          "success rate", sentiment="accent")

    # ----------------------------------------------------------------
    # TIGER 5 TREND CHART (stacked bar by round)
    # ----------------------------------------------------------------
    with st.expander("View Tiger 5 Trend by Round"):
        t5_df = tiger5_results["by_round"]

        if not t5_df.empty:
            t5_df = t5_df.copy()
            t5_df['Chart Label'] = (
                t5_df['Date'].dt.strftime('%m/%d/%y') + ' ' + t5_df['Course']
            )

            fail_types = ['3 Putts', 'Double Bogey', 'Par 5 Bogey',
                          'Missed Green', '125yd Bogey']
            t5_colors = [CHART_PUTTING, NEGATIVE, ACCENT_PRIMARY,
                         POSITIVE, CHARCOAL]

            fig_t5 = go.Figure()
            for fail_type, color in zip(fail_types, t5_colors):
                fig_t5.add_trace(go.Bar(
                    x=t5_df['Chart Label'],
                    y=t5_df[fail_type],
                    name=fail_type,
                    marker_color=color,
                ))

            fig_t5.update_layout(
                **CHART_LAYOUT,
                barmode='stack',
                xaxis_title='',
                yaxis_title='Tiger 5 Fails',
                height=400,
                legend=dict(orientation='h', yanchor='bottom', y=1.02,
                            xanchor='right', x=1),
                margin=dict(t=60, b=80, l=60, r=40),
                xaxis=dict(tickangle=-45),
                hovermode='x unified',
            )

            st.plotly_chart(fig_t5, use_container_width=True,
                            config={'displayModeBar': False})
        else:
            st.info("No data available for Tiger 5 trend.")

    # ----------------------------------------------------------------
    # ROOT CAUSE ANALYSIS
    # ----------------------------------------------------------------
    section_header("Root Cause Analysis")

    shot_type_counts, detail_by_type = build_tiger5_root_cause(
        filtered_df, tiger5_results, hole_summary
    )

    rc_cols = st.columns(5)
    rc_types = ['Driving', 'Approach', 'Short Game', 'Short Putts', 'Lag Putts']
    rc_palette = [ACCENT_PRIMARY, CHARCOAL, POSITIVE, CHART_PUTTING,
                  ACCENT_SECONDARY]

    for col, stype, color in zip(rc_cols, rc_types, rc_palette):
        count = shot_type_counts.get(stype, 0)
        pct = (count / total_tiger5_fails * 100) if total_tiger5_fails > 0 else 0
        with col:
            premium_stat_card(stype, str(count), f"{pct:.0f}% of fails")

    # Detailed breakdown
    with st.expander("View Root Cause Breakdown by Fail Type"):
        for stat_name in tiger5_names:
            items = detail_by_type.get(stat_name, [])
            if not items:
                continue
            st.markdown(f"#### {stat_name}")
            if stat_name == '3 Putts':
                lag = sum(1 for i in items if i['cause'] == 'Poor Lag Putt')
                short = sum(1 for i in items if i['cause'] == 'Missed Short Putt')
                other = len(items) - lag - short
                parts = []
                if lag:
                    parts.append(f"Poor Lag Putt (left >=6ft): **{lag}**")
                if short:
                    parts.append(f"Missed Short Putt (<6ft): **{short}**")
                if other:
                    parts.append(f"Other: **{other}**")
                for p in parts:
                    st.markdown(f"- {p}")
            elif stat_name == '125yd Bogey':
                cause_counts = {}
                for i in items:
                    cause_counts[i['cause']] = cause_counts.get(
                        i['cause'], 0) + 1
                for cause, cnt in sorted(cause_counts.items(),
                                         key=lambda x: -x[1]):
                    st.markdown(f"- {cause}: **{cnt}**")
            else:
                cause_counts = {}
                for i in items:
                    cause_counts[i['shot_type']] = cause_counts.get(
                        i['shot_type'], 0) + 1
                for stype_name, cnt in sorted(cause_counts.items(),
                                              key=lambda x: -x[1]):
                    st.markdown(f"- {stype_name}: **{cnt}**")

    # ----------------------------------------------------------------
    # TIGER 5 FAIL DETAILS (shot-level)
    # ----------------------------------------------------------------
    with st.expander("View Tiger 5 Fail Details"):
        fail_shots = build_tiger5_fail_shots(filtered_df, tiger5_results)
        any_fails = False

        for stat_name in tiger5_names:
            holes = fail_shots.get(stat_name, [])
            if holes:
                any_fails = True
                st.markdown(f"#### {stat_name}")
                for hole_data in holes:
                    st.markdown(
                        f"**{hole_data['date']} &mdash; "
                        f"{hole_data['course']} &mdash; "
                        f"Hole {hole_data['hole']}**"
                    )
                    st.dataframe(
                        hole_data['shots'],
                        use_container_width=True,
                        hide_index=True,
                    )

        if not any_fails:
            st.info("No Tiger 5 fails to display.")

    # ----------------------------------------------------------------
    # SCORING IMPACT
    # ----------------------------------------------------------------
    section_header("Scoring Impact")

    t5_by_round = tiger5_results.get("by_round", pd.DataFrame())
    impact_df = build_tiger5_scoring_impact(t5_by_round)

    if not impact_df.empty:
        fig_impact = go.Figure()

        fig_impact.add_trace(go.Bar(
            x=impact_df['Label'],
            y=impact_df['Total Score'],
            name='Actual Score',
            marker_color=NEGATIVE,
            opacity=0.85,
        ))

        fig_impact.add_trace(go.Bar(
            x=impact_df['Label'],
            y=impact_df['Potential Score'],
            name='Potential Score (50% fewer fails)',
            marker_color=POSITIVE,
            opacity=0.85,
        ))

        fig_impact.update_layout(
            **CHART_LAYOUT,
            barmode='group',
            xaxis_title='',
            yaxis_title='Score',
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02,
                        xanchor='right', x=1),
            margin=dict(t=60, b=80, l=60, r=40),
            xaxis=dict(tickangle=-45),
            hovermode='x unified',
        )

        st.plotly_chart(fig_impact, use_container_width=True,
                        config={'displayModeBar': False})

        # Summary stats
        total_actual = impact_df['Total Score'].sum()
        total_potential = impact_df['Potential Score'].sum()
        total_saved = total_actual - total_potential
        num_rds = len(impact_df)
        avg_actual = total_actual / num_rds if num_rds > 0 else 0
        avg_potential = total_potential / num_rds if num_rds > 0 else 0

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            premium_stat_card("Avg Actual Score", f"{avg_actual:.1f}")
        with sc2:
            premium_stat_card("Avg Potential Score", f"{avg_potential:.1f}",
                              sentiment="positive")
        with sc3:
            premium_stat_card("Total Strokes Saved", f"{total_saved:.0f}",
                              sentiment="positive")
    else:
        st.info("No round data available for scoring impact.")
