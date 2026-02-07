# ============================================================
# TAB: PUTTING
# ============================================================

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.theme import (
    CHARCOAL, ACCENT_PRIMARY, ACCENT_SECONDARY,
    POSITIVE, NEGATIVE, WARNING,
    BORDER_LIGHT, DONUT_SEQUENCE, THRESHOLDS,
)
from ui.chart_config import CHART_LAYOUT
from ui.components import (
    section_header, premium_hero_card, premium_stat_card, sg_sentiment,
)
from ui.formatters import format_sg, format_pct


def putting_tab(putting, num_rounds):

    if putting["empty"]:
        st.warning("No putting data available for the selected filters.")
        return

    hero = putting["hero_metrics"]

    section_header("Putting Performance")

    # ----------------------------------------------------------------
    # SECTION 1 — HERO CARDS
    # ----------------------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        premium_hero_card(
            "SG Putting", format_sg(hero["sg_total"]),
            f"{format_sg(hero['sg_per_round'])} per round",
            sentiment=sg_sentiment(hero["sg_total"]),
        )

    with col2:
        premium_hero_card(
            "SG Putting 3\u20136 ft", format_sg(hero["sg_3_6"]),
            f"Made {hero['sg_3_6_made']} / {hero['sg_3_6_attempts']}",
            sentiment=sg_sentiment(hero["sg_3_6"]),
        )

    with col3:
        premium_hero_card(
            "SG Putting 7\u201310 ft", format_sg(hero["sg_7_10"]),
            f"Made {hero['sg_7_10_made']} / {hero['sg_7_10_attempts']}",
            sentiment=sg_sentiment(hero["sg_7_10"]),
        )

    with col4:
        # Lag miss % — lower is better; card is positive when inverted val >= 80
        s = sg_sentiment(100 - hero["lag_miss_pct"], threshold=80)
        premium_hero_card(
            "Lag Miss %", format_pct(hero["lag_miss_pct"]),
            "First putts \u226520 ft leaving >5 ft",
            sentiment=s,
        )

    with col5:
        s = sg_sentiment(hero["make_0_3_pct"],
                         threshold=THRESHOLDS["pct_make_0_3"])
        premium_hero_card(
            "Make % 0\u20133 ft", format_pct(hero["make_0_3_pct"]),
            f"Made {hero['make_0_3_made']} / {hero['make_0_3_attempts']}",
            sentiment=s,
        )

    # Collapsible lag miss detail
    lag_detail = putting["lag_miss_detail"]
    if not lag_detail.empty:
        with st.expander(f"Lag Putts Leaving > 5 ft ({len(lag_detail)} total)"):
            st.dataframe(lag_detail, use_container_width=True,
                         hide_index=True)

    # ----------------------------------------------------------------
    # SECTION 2 — SG PUTTING BY DISTANCE
    # ----------------------------------------------------------------
    section_header("SG Putting by Distance")

    st.dataframe(
        putting["bucket_table"],
        use_container_width=True,
        hide_index=True,
    )

    # Dual-axis chart: stacked bar (putt outcomes) + SG line
    outcome_df = putting["outcome_chart_data"]
    if not outcome_df.empty and outcome_df['holes'].sum() > 0:
        fig_outcome = make_subplots(specs=[[{"secondary_y": True}]])

        fig_outcome.add_trace(
            go.Bar(
                x=outcome_df['Distance Bucket'],
                y=outcome_df['pct_1putt'],
                name='1-Putt', marker_color=POSITIVE,
                hovertemplate='%{y:.1f}%<extra>1-Putt</extra>',
            ),
            secondary_y=False,
        )
        fig_outcome.add_trace(
            go.Bar(
                x=outcome_df['Distance Bucket'],
                y=outcome_df['pct_2putt'],
                name='2-Putt', marker_color=ACCENT_PRIMARY,
                hovertemplate='%{y:.1f}%<extra>2-Putt</extra>',
            ),
            secondary_y=False,
        )
        fig_outcome.add_trace(
            go.Bar(
                x=outcome_df['Distance Bucket'],
                y=outcome_df['pct_3plus'],
                name='3+ Putt', marker_color=NEGATIVE,
                hovertemplate='%{y:.1f}%<extra>3+ Putt</extra>',
            ),
            secondary_y=False,
        )

        fig_outcome.add_trace(
            go.Scatter(
                x=outcome_df['Distance Bucket'],
                y=outcome_df['sg'],
                name='SG', mode='lines+markers',
                line=dict(color=CHARCOAL, width=3, shape='spline'),
                marker=dict(size=8, color=CHARCOAL),
                hovertemplate='%{y:+.2f}<extra>SG</extra>',
            ),
            secondary_y=True,
        )

        fig_outcome.update_layout(
            **CHART_LAYOUT,
            barmode='stack',
            legend=dict(orientation='h', yanchor='bottom', y=1.02,
                        xanchor='right', x=1),
            margin=dict(t=60, b=60, l=60, r=60),
            height=400,
            hovermode='x unified',
        )
        fig_outcome.update_yaxes(
            title_text='% of Holes', range=[0, 105],
            gridcolor=BORDER_LIGHT, secondary_y=False,
        )
        fig_outcome.update_yaxes(
            title_text='Strokes Gained', showgrid=False,
            zerolinecolor=CHARCOAL, zerolinewidth=1,
            secondary_y=True,
        )

        st.plotly_chart(fig_outcome, use_container_width=True,
                        config={'displayModeBar': False})

    # ----------------------------------------------------------------
    # SECTION 3 — LAG PUTTING
    # ----------------------------------------------------------------
    section_header("Lag Putting")

    lag = putting["lag_metrics"]

    colA, colB, colC = st.columns(3)

    with colA:
        premium_stat_card(
            "Avg Leave Distance", f"{lag['avg_leave']:.1f} ft",
            "Putts \u226520 ft",
        )

    with colB:
        s = sg_sentiment(lag["pct_inside_3"],
                         threshold=THRESHOLDS["pct_lag_inside_3"])
        premium_hero_card(
            "Leaves Inside 3 ft", format_pct(lag["pct_inside_3"]),
            "Putts \u226520 ft", sentiment=s,
        )

    with colC:
        s = sg_sentiment(100 - lag["pct_over_5"], threshold=80)
        premium_hero_card(
            "Leaves Over 5 ft", format_pct(lag["pct_over_5"]),
            "Putts \u226520 ft", sentiment=s,
        )

    # Donut charts
    three_putt_starts = putting["three_putt_starts"]
    leave_dist = putting["leave_distribution"]

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        if not three_putt_starts.empty and three_putt_starts['Count'].sum() > 0:
            chart_a = three_putt_starts[three_putt_starts['Count'] > 0]
            total_3putts = int(chart_a['Count'].sum())
            fig_a = go.Figure(data=[go.Pie(
                labels=chart_a['Bucket'],
                values=chart_a['Count'],
                hole=0.6,
                marker_colors=DONUT_SEQUENCE[:len(chart_a)],
                textinfo='label+percent',
                textposition='outside',
                textfont=dict(family='Inter', size=12),
                pull=[0.02] * len(chart_a),
            )])
            fig_a.update_layout(
                **CHART_LAYOUT,
                showlegend=False,
                margin=dict(t=40, b=40, l=40, r=40),
                height=350,
                annotations=[dict(
                    text=f'<b>{total_3putts}</b><br>3-Putts',
                    x=0.5, y=0.5,
                    font=dict(family='Playfair Display', size=22,
                              color=CHARCOAL),
                    showarrow=False,
                )],
            )
            st.markdown(
                '<p style="text-align:center;font-weight:600;'
                'font-size:0.9rem;">3-Putt: First Putt Starting Distance</p>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(fig_a, use_container_width=True,
                            config={'displayModeBar': False})
        else:
            st.info("No 3-putt data available.")

    with col_d2:
        if not leave_dist.empty and leave_dist['Count'].sum() > 0:
            chart_b = leave_dist[leave_dist['Count'] > 0]
            total_lag = int(chart_b['Count'].sum())
            fig_b = go.Figure(data=[go.Pie(
                labels=chart_b['Bucket'],
                values=chart_b['Count'],
                hole=0.6,
                marker_colors=DONUT_SEQUENCE[:len(chart_b)],
                textinfo='label+percent',
                textposition='outside',
                textfont=dict(family='Inter', size=12),
                pull=[0.02] * len(chart_b),
            )])
            fig_b.update_layout(
                **CHART_LAYOUT,
                showlegend=False,
                margin=dict(t=40, b=40, l=40, r=40),
                height=350,
                annotations=[dict(
                    text=f'<b>{total_lag}</b><br>Putts',
                    x=0.5, y=0.5,
                    font=dict(family='Playfair Display', size=22,
                              color=CHARCOAL),
                    showarrow=False,
                )],
            )
            st.markdown(
                '<p style="text-align:center;font-weight:600;'
                'font-size:0.9rem;">'
                'Leave Distance Distribution (&gt;20 ft putts)</p>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(fig_b, use_container_width=True,
                            config={'displayModeBar': False})
        else:
            st.info("No lag putting data available.")

    # ----------------------------------------------------------------
    # SECTION 4 — SG PUTTING TREND
    # ----------------------------------------------------------------
    section_header("SG Putting Trend")

    trend_df = putting["trend_df"]

    if not trend_df.empty:
        use_ma = st.checkbox("Apply Moving Average", value=False,
                             key="putting_ma")

        if use_ma:
            window = st.selectbox(
                "Moving Average Window", [3, 5, 10], index=0,
                key="putting_ma_window",
            )
            trend_df = trend_df.copy()
            trend_df["SG_MA"] = trend_df["SG"].rolling(
                window=window).mean()
            y_col = "SG_MA"
        else:
            y_col = "SG"

        fig_trend = px.line(
            trend_df, x="Label", y=y_col, markers=True,
            title="SG: Putting Trend",
            color_discrete_sequence=[CHARCOAL],
        )

        fig_trend.update_layout(
            **CHART_LAYOUT,
            xaxis_title='', yaxis_title='Strokes Gained', height=400,
        )
        fig_trend.update_xaxes(tickangle=-45)

        st.plotly_chart(fig_trend, use_container_width=True,
                        config={'displayModeBar': False})
    else:
        st.info("No trend data available.")

    # Collapsible shot detail
    shot_detail = putting["shot_detail"]
    if not shot_detail.empty:
        with st.expander(f"All Putting Shots ({len(shot_detail)} total)"):
            st.dataframe(shot_detail, use_container_width=True,
                         hide_index=True)
    else:
        st.info("No shot detail available.")
