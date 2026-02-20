# ============================================================
# TAB: DRIVING
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.theme import (
    CHARCOAL, SLATE, WHITE, ACCENT_PRIMARY, ACCENT_SECONDARY,
    POSITIVE, NEGATIVE, WARNING,
    BORDER_LIGHT, FONT_BODY, FONT_HEADING,
    THRESHOLDS,
)
from ui.chart_config import CHART_LAYOUT, sg_bar_color
from ui.components import (
    section_header, premium_hero_card, premium_stat_card,
    sg_sentiment, pct_sentiment_above, pct_sentiment_below,
)
from ui.formatters import format_sg, format_pct, format_date


def driving_tab(drive, num_rounds, hole_summary):

    if drive["num_drives"] == 0:
        st.warning("No driving data available for the selected filters.")
        return

    # ----------------------------------------------------------------
    # SECTION 1: HERO CARDS
    # ----------------------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        premium_hero_card(
            "SG Total", format_sg(drive['driving_sg']),
            f"{format_sg(drive['driving_sg_per_round'])} per round",
            sentiment=sg_sentiment(drive['driving_sg']),
        )

    with col2:
        s = "negative" if drive['obstruction_pct'] > 10 else "positive"
        premium_hero_card(
            "Obstruction Rate",
            format_pct(drive['obstruction_pct']),
            f"{drive['obstruction_count']} of {drive['num_drives']} drives",
            sentiment=s,
        )

    with col3:
        total_penalty_count = drive['penalty_count'] + drive['ob_count']
        penalty_pct = (total_penalty_count / drive['num_drives'] * 100) if drive['num_drives'] > 0 else 0.0
        s = "negative" if total_penalty_count > 0 else "positive"
        premium_hero_card(
            "Driver Penalties",
            format_pct(penalty_pct),
            f"{total_penalty_count} of {drive['num_drives']} drives \u00b7 OB: {drive['ob_count']} \u00b7 Penalty: {drive['penalty_count']}",
            sentiment=s,
        )

    with col4:
        premium_hero_card(
            "Driving Distance", f"{drive['driving_distance_p90']:.0f}",
            "90th Percentile (yds)",
            sentiment="accent",
        )

    with col5:
        s = pct_sentiment_above(drive['fairway_pct'], "pct_fairway")
        premium_hero_card(
            "Fairways Hit", format_pct(drive['fairway_pct']),
            f"{drive['fairway']} of {drive['num_drives']} drives",
            sentiment=s,
        )

    # ----------------------------------------------------------------
    # SECTION 2: STROKES GAINED BY RESULT (Donut + Bar)
    # ----------------------------------------------------------------
    section_header("Strokes Gained by Result")

    col_donut, col_bar = st.columns([1, 1])

    with col_donut:
        labels = ['Fairway', 'Rough', 'Sand', 'Recovery', 'Green']
        values = [
            drive['fairway'], drive['rough'], drive['sand'],
            drive['recovery'], drive['green'],
        ]
        colors = [ACCENT_PRIMARY, ACCENT_SECONDARY, WARNING, NEGATIVE, POSITIVE]

        chart_data = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]

        fig_donut = go.Figure(data=[go.Pie(
            labels=[d[0] for d in chart_data],
            values=[d[1] for d in chart_data],
            hole=0.6,
            marker_colors=[d[2] for d in chart_data],
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(family=FONT_BODY, size=12),
            pull=[0.02] * len(chart_data),
        )])

        fig_donut.update_layout(
            **CHART_LAYOUT,
            showlegend=False,
            margin=dict(t=40, b=40, l=40, r=40),
            height=350,
            annotations=[dict(
                text=f'<b>{drive["num_drives"]}</b><br>Drives',
                x=0.5, y=0.5,
                font=dict(family=FONT_HEADING, size=24,
                          color=CHARCOAL),
                showarrow=False,
            )],
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    with col_bar:
        sg_df = drive["sg_by_result"].sort_values("Total SG", ascending=True)
        colors_bar = [sg_bar_color(x) for x in sg_df['Total SG']]

        fig_sg_result = go.Figure(data=[go.Bar(
            y=sg_df['Result'],
            x=sg_df['Total SG'],
            orientation='h',
            marker_color=colors_bar,
            text=sg_df['Total SG'].apply(lambda x: f'{x:+.2f}'),
            textposition='outside',
            textfont=dict(family=FONT_BODY, size=12, color=CHARCOAL),
        )])

        fig_sg_result.update_layout(
            **CHART_LAYOUT,
            xaxis=dict(title='Strokes Gained', gridcolor=BORDER_LIGHT,
                       zerolinecolor=CHARCOAL, zerolinewidth=2),
            yaxis=dict(title=''),
            margin=dict(t=40, b=40, l=100, r=80),
            height=350,
        )

        st.plotly_chart(fig_sg_result, use_container_width=True)

    # ----------------------------------------------------------------
    # SECTION 3: PENALTY BREAKOUT
    # ----------------------------------------------------------------
    section_header("Penalty Breakout")

    total_penalty_count = drive['penalty_count'] + drive['ob_count']
    total_penalty_sg = drive['penalty_sg'] + drive['ob_sg']

    # Calculate SG for obstruction types from the driving dataframe
    sand_sg = drive['df'][drive['df']['Ending Location'] == 'Sand']['Strokes Gained'].sum() if 'df' in drive else 0.0
    recovery_sg = drive['df'][drive['df']['Ending Location'] == 'Recovery']['Strokes Gained'].sum() if 'df' in drive else 0.0

    col_pen, col_obs, col_avoid = st.columns(3)

    with col_pen:
        s = "negative" if total_penalty_count > 0 else "neutral"
        premium_stat_card(
            "Penalty Type", str(total_penalty_count),
            f"Total Penalties \u00b7 SG: {format_sg(total_penalty_sg)}",
            sentiment=s,
        )
        st.markdown(
            f'''
            <table class="premium-table">
                <tr><th style="text-align:left;">Type</th><th>#</th><th>SG</th></tr>
                <tr><td>OB (Re-Tee)</td><td>{drive['ob_count']}</td>
                    <td>{drive['ob_sg']:+.2f}</td></tr>
                <tr><td>Penalty</td><td>{drive['penalty_count']}</td>
                    <td>{drive['penalty_sg']:+.2f}</td></tr>
            </table>
            ''',
            unsafe_allow_html=True,
        )

    with col_obs:
        s = "negative" if drive['obstruction_pct'] > 10 else "positive"
        premium_stat_card(
            "Obstruction Type",
            str(drive['obstruction_count']),
            f"Total Obstructions \u00b7 SG: {format_sg(drive['obstruction_sg'])}",
            sentiment=s,
        )
        st.markdown(
            f'''
            <table class="premium-table">
                <tr><th style="text-align:left;">Type</th><th>#</th><th>SG</th></tr>
                <tr><td>Recovery</td><td>{drive['recovery']}</td>
                    <td>{recovery_sg:+.2f}</td></tr>
                <tr><td>Sand</td><td>{drive['sand']}</td>
                    <td>{sand_sg:+.2f}</td></tr>
            </table>
            ''',
            unsafe_allow_html=True,
        )

    with col_avoid:
        s = "negative" if drive['avoidable_loss_pct'] > 10 else "positive"
        premium_stat_card(
            "Avoidable Loss Rate",
            format_pct(drive['avoidable_loss_pct']),
            f"{drive['avoidable_loss_count']} of {drive['num_drives']} \u00b7 SG: {format_sg(drive['avoidable_loss_sg'])}",
            sentiment=s,
        )

    # ----------------------------------------------------------------
    # SECTION 4: DRIVING CONSISTENCY
    # ----------------------------------------------------------------
    section_header("Driving Consistency")

    col_con1, col_con2, col_con3 = st.columns(3)

    with col_con1:
        premium_stat_card(
            "Driving Consistency", f"{drive['sg_std']:.2f}",
            "SG Standard Deviation",
        )

    with col_con2:
        s = pct_sentiment_above(drive['positive_sg_pct'], "pct_positive_sg_drives")
        premium_stat_card(
            "Positive SG Drives",
            format_pct(drive['positive_sg_pct']),
            f"SG: {format_sg(drive['positive_sg_total'])}",
            sentiment=s,
        )

    with col_con3:
        s = pct_sentiment_below(drive['poor_drive_pct'], "pct_poor_drive")
        premium_stat_card(
            "Poor Drive Rate",
            format_pct(drive['poor_drive_pct']),
            f"SG: {format_sg(drive['poor_drive_sg'])}",
            sentiment=s,
        )

    # ----------------------------------------------------------------
    # SECTION 5: SCORING IMPACTS
    # ----------------------------------------------------------------
    section_header("Scoring Impacts")

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        s = pct_sentiment_below(drive['trouble_to_bogey_pct'], "pct_trouble_bogey")
        premium_stat_card(
            "Trouble to Bogey",
            format_pct(drive['trouble_to_bogey_pct']),
            f"{drive['trouble_to_bogey_fails']} of {drive['trouble_to_bogey_attempts']} recovery drives",
            sentiment=s,
        )

    with col_s2:
        s = "negative" if drive['double_penalty_pct'] > 50 else "positive"
        premium_stat_card(
            "Double+ on Penalty Holes",
            format_pct(drive['double_penalty_pct']),
            f"{drive['double_penalty_fails']} of {drive['double_penalty_attempts']} penalty holes (excl. OB)",
            sentiment=s,
        )

    # Avg score by drive ending location vs par
    avg_loc = drive['avg_score_by_end_loc']
    if not avg_loc.empty:
        loc_order = ['Fairway', 'Rough', 'Sand', 'Recovery']
        avg_loc['Ending Location'] = pd.Categorical(
            avg_loc['Ending Location'], categories=loc_order, ordered=True
        )
        avg_loc = avg_loc.sort_values('Ending Location')

        bar_colors = [NEGATIVE if v > 0 else POSITIVE for v in avg_loc['Avg vs Par']]

        fig_avg = go.Figure(data=[go.Bar(
            x=avg_loc['Ending Location'],
            y=avg_loc['Avg vs Par'],
            marker_color=bar_colors,
            text=avg_loc['Avg vs Par'].apply(lambda x: f'{x:+.2f}'),
            textposition='outside',
            textfont=dict(family=FONT_BODY, size=12, color=CHARCOAL),
        )])

        fig_avg.update_layout(
            **CHART_LAYOUT,
            yaxis=dict(title='Avg Score vs Par', gridcolor=BORDER_LIGHT,
                       zerolinecolor=CHARCOAL, zerolinewidth=2),
            xaxis=dict(title='Drive Ending Location'),
            margin=dict(t=30, b=40, l=60, r=40),
            height=300,
        )

        st.plotly_chart(fig_avg, use_container_width=True)

    # ----------------------------------------------------------------
    # SECTION 6: SG TREND
    # ----------------------------------------------------------------
    section_header("Driving Performance Trend")

    trend = drive["trend"]

    if len(trend) > 1:
        ma_options = [i for i in [3, 5, 7, 10] if i <= len(trend)]
        if ma_options:
            ma_window = st.selectbox(
                "Moving Average Window", options=ma_options, index=0,
                key="driving_ma_window",
            )
        else:
            ma_window = None
    else:
        ma_window = None

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

    fig_trend.add_trace(
        go.Scatter(
            x=trend['Label'], y=trend['SG'],
            name='SG Driving', mode='lines+markers',
            line=dict(color=ACCENT_PRIMARY, width=3),
            marker=dict(size=8, color=ACCENT_PRIMARY),
        ),
        secondary_y=False,
    )

    fig_trend.add_trace(
        go.Scatter(
            x=trend['Label'], y=trend['Fairway %'],
            name='Fairway %', mode='lines+markers',
            line=dict(color=CHARCOAL, width=3),
            marker=dict(size=10, color=CHARCOAL),
        ),
        secondary_y=True,
    )

    if ma_window and len(trend) >= ma_window:
        ma_values = trend['SG'].rolling(
            window=ma_window, min_periods=ma_window
        ).mean()
        fig_trend.add_trace(
            go.Scatter(
                x=trend['Label'], y=ma_values,
                name=f'SG {ma_window}-Round MA', mode='lines',
                line=dict(color=ACCENT_SECONDARY, width=3, dash='dash'),
            ),
            secondary_y=False,
        )

    fig_trend.update_layout(
        **CHART_LAYOUT,
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1),
        margin=dict(t=60, b=80, l=60, r=60),
        height=350,
        hovermode='x unified',
        xaxis=dict(tickangle=-45),
    )

    fig_trend.update_yaxes(
        title_text="Strokes Gained", gridcolor=BORDER_LIGHT,
        zerolinecolor=CHARCOAL, zerolinewidth=2,
        secondary_y=False,
    )

    fig_trend.update_yaxes(
        title_text="Fairway %", range=[0, 100],
        showgrid=False, secondary_y=True,
    )

    st.plotly_chart(fig_trend, use_container_width=True,
                    config={'displayModeBar': False})

    # ----------------------------------------------------------------
    # SECTION 7: DETAIL TABLES
    # ----------------------------------------------------------------
    section_header("Detailed Data")

    with st.expander(f"All Driving Shots ({drive['num_drives']} total)"):
        detail = drive["df"][[
            'Player', 'Date', 'Course', 'Hole',
            'Starting Distance', 'Ending Distance',
            'Ending Location', 'Penalty', 'Strokes Gained',
        ]].copy()

        detail['Date'] = pd.to_datetime(detail['Date']).dt.strftime('%m/%d/%y')

        detail.columns = [
            'Player', 'Date', 'Course', 'Hole',
            'Distance', 'End Dist', 'Result', 'Penalty', 'SG',
        ]

        detail['Hole'] = detail['Hole'].astype(int)
        detail['Distance'] = detail['Distance'].round(0).astype(int)
        detail['End Dist'] = detail['End Dist'].round(0).astype(int)
        detail['SG'] = detail['SG'].round(2)

        st.dataframe(
            detail.sort_values(['Date', 'Hole'], ascending=[False, True]),
            use_container_width=True, hide_index=True,
        )

    if drive['ob_count'] > 0:
        with st.expander(f"OB / Re-Tee Instances ({drive['ob_count']} total)"):
            ob_df = pd.DataFrame(drive['ob_details'])
            ob_df['Date'] = pd.to_datetime(ob_df['Date']).dt.strftime('%m/%d/%y')
            ob_df['Hole'] = ob_df['Hole'].astype(int)
            st.dataframe(ob_df, use_container_width=True, hide_index=True)

    # Penalty section (excluding OB)
    if drive['penalty_count'] > 0:
        with st.expander(f"Penalty Shots ({drive['penalty_count']} total)"):
            penalty = drive['penalty_details'].copy()

            penalty['Date'] = pd.to_datetime(penalty['Date']).dt.strftime('%m/%d/%y')

            penalty.columns = [
                'Player', 'Date', 'Course', 'Hole',
                'Distance', 'Result', 'SG',
            ]

            penalty['Hole'] = penalty['Hole'].astype(int)
            penalty['Distance'] = penalty['Distance'].round(0).astype(int)
            penalty['SG'] = penalty['SG'].round(2)

            st.dataframe(penalty, use_container_width=True, hide_index=True)

    if drive['obstruction_count'] > 0:
        with st.expander(f"Obstruction Shots ({drive['obstruction_count']} total)"):
            obs = drive["df"][
                drive["df"]['Ending Location'].isin(['Sand', 'Recovery'])
            ][[
                'Player', 'Date', 'Course', 'Hole',
                'Starting Distance', 'Ending Location', 'Strokes Gained',
            ]].copy()

            obs['Date'] = pd.to_datetime(obs['Date']).dt.strftime('%m/%d/%y')

            obs.columns = [
                'Player', 'Date', 'Course', 'Hole',
                'Distance', 'Result', 'SG',
            ]

            obs['Hole'] = obs['Hole'].astype(int)
            obs['Distance'] = obs['Distance'].round(0).astype(int)
            obs['SG'] = obs['SG'].round(2)

            st.dataframe(obs, use_container_width=True, hide_index=True)
