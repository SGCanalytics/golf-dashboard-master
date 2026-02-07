# ============================================================
# TAB: SHORT GAME
# ============================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.theme import (
    CHARCOAL, ACCENT_PRIMARY, POSITIVE, NEGATIVE,
    BORDER_LIGHT, THRESHOLDS,
)
from ui.chart_config import CHART_LAYOUT, SG_HEATMAP_COLORSCALE
from ui.components import (
    section_header, premium_hero_card, sg_sentiment,
)
from ui.formatters import format_sg, format_pct


def short_game_tab(sg, num_rounds):

    if sg["empty"]:
        st.warning("No short game data available for the selected filters.")
        return

    hero = sg["hero_metrics"]

    section_header("Short Game Performance")

    # ----------------------------------------------------------------
    # SECTION 1 — HERO CARDS
    # ----------------------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        premium_hero_card(
            "SG Short Game", format_sg(hero["sg_total"]),
            f"{format_sg(hero['sg_per_round'])} per round",
            sentiment=sg_sentiment(hero["sg_total"]),
        )

    with col2:
        premium_hero_card(
            "SG 25\u201350", format_sg(hero["sg_25_50"]),
            "Total",
            sentiment=sg_sentiment(hero["sg_25_50"]),
        )

    with col3:
        premium_hero_card(
            "SG ARG", format_sg(hero["sg_arg"]),
            "Total",
            sentiment=sg_sentiment(hero["sg_arg"]),
        )

    with col4:
        t = THRESHOLDS["pct_inside_8ft"]
        premium_hero_card(
            "% Inside 8 ft", format_pct(hero["pct_inside_8_fr"]),
            "Fairway & Rough",
            sentiment=sg_sentiment(hero["pct_inside_8_fr"], threshold=t),
        )

    with col5:
        premium_hero_card(
            "% Inside 8 ft", format_pct(hero["pct_inside_8_sand"]),
            "Bunker",
            sentiment=sg_sentiment(hero["pct_inside_8_sand"], threshold=t),
        )

    # ----------------------------------------------------------------
    # SECTION 2 — HEAT MAP + DETAIL TABLE
    # ----------------------------------------------------------------
    section_header("Short Game Heat Map")

    sg_pivot = sg["heatmap_sg_pivot"]
    count_pivot = sg["heatmap_count_pivot"]

    if not sg_pivot.empty:
        count_filled = count_pivot.fillna(0).astype(int)
        text_matrix = count_filled.astype(str)
        text_matrix = text_matrix.where(count_filled > 0, "")
        text_vals = text_matrix.values.tolist()

        hover_matrix = []
        for i, lie in enumerate(sg_pivot.index):
            row = []
            for j, bucket in enumerate(sg_pivot.columns):
                sg_val = sg_pivot.iloc[i, j]
                cnt = count_filled.iloc[i, j]
                if cnt > 0 and not np.isnan(sg_val):
                    row.append(
                        f"Lie: {lie}<br>Distance: {bucket}<br>"
                        f"SG/Shot: {sg_val:+.3f}<br>Shots: {cnt}"
                    )
                else:
                    row.append("")
            hover_matrix.append(row)

        fig_heat = go.Figure(data=go.Heatmap(
            z=sg_pivot.values,
            x=sg_pivot.columns.tolist(),
            y=sg_pivot.index.tolist(),
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=14, color="#ffffff"),
            colorscale=SG_HEATMAP_COLORSCALE,
            zmid=0,
            colorbar=dict(title="SG/Shot"),
            hovertext=hover_matrix,
            hovertemplate="%{hovertext}<extra></extra>",
        ))

        fig_heat.update_layout(
            **CHART_LAYOUT,
            xaxis_title="Distance (yards)",
            yaxis_title="Starting Lie",
            height=300,
            margin=dict(t=40, b=60, l=100, r=40),
        )

        st.plotly_chart(fig_heat, use_container_width=True,
                        config={'displayModeBar': False})
    else:
        st.info("No heat map data available.")

    with st.expander("View Detailed Performance by Distance & Lie"):
        if not sg["distance_lie_table"].empty:
            st.dataframe(sg["distance_lie_table"],
                         use_container_width=True, hide_index=True)
        else:
            st.info("No data available.")

    # ----------------------------------------------------------------
    # SECTION 3 — LEAVE DISTANCE DISTRIBUTION
    # ----------------------------------------------------------------
    section_header("Leave Distance Distribution")

    leave = sg["leave_distribution"]

    if not leave.empty and leave['Shots'].sum() > 0:
        fig_leave = go.Figure(data=go.Bar(
            x=leave['Leave Bucket'],
            y=leave['Shots'],
            marker_color=ACCENT_PRIMARY,
            text=leave['Shots'],
            textposition='outside',
            textfont=dict(size=13, family='Inter'),
        ))

        fig_leave.update_layout(
            **CHART_LAYOUT,
            xaxis_title="Leave Distance (ft)",
            yaxis_title="Number of Shots",
            height=350,
            margin=dict(t=40, b=60, l=60, r=40),
            showlegend=False,
        )

        st.plotly_chart(fig_leave, use_container_width=True,
                        config={'displayModeBar': False})
    else:
        st.info("No leave distance data available.")

    # ----------------------------------------------------------------
    # SECTION 4 — SG SHORT GAME TREND
    # ----------------------------------------------------------------
    section_header("Short Game Trend by Round")

    trend_df = sg["trend_df"]

    if not trend_df.empty:
        use_ma = st.checkbox("Apply Moving Average", value=False,
                             key="sg_ma")

        if use_ma:
            window = st.selectbox("Moving Average Window", [3, 5, 10],
                                  index=0, key="sg_ma_window")
            trend_df = trend_df.copy()
            trend_df["SG_MA"] = trend_df["SG"].rolling(
                window=window).mean()
            trend_df["Inside8_MA"] = trend_df["Inside8 %"].rolling(
                window=window).mean()
            y1 = "SG_MA"
            y2 = "Inside8_MA"
        else:
            y1 = "SG"
            y2 = "Inside8 %"

        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

        fig_trend.add_trace(
            go.Bar(
                x=trend_df["Label"], y=trend_df[y1],
                name="SG: Short Game", marker_color=ACCENT_PRIMARY,
                opacity=0.85,
            ),
            secondary_y=False,
        )

        fig_trend.add_trace(
            go.Scatter(
                x=trend_df["Label"], y=trend_df[y2],
                name="% Inside 8 ft", mode="lines+markers",
                line=dict(color=CHARCOAL, width=3),
                marker=dict(size=9, color=CHARCOAL),
            ),
            secondary_y=True,
        )

        fig_trend.update_layout(
            **CHART_LAYOUT,
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1),
            margin=dict(t=60, b=80, l=60, r=60),
            height=350,
            hovermode="x unified",
            xaxis=dict(tickangle=-45),
        )

        fig_trend.update_yaxes(
            title_text="Strokes Gained", gridcolor=BORDER_LIGHT,
            zerolinecolor=CHARCOAL, zerolinewidth=2,
            secondary_y=False,
        )

        fig_trend.update_yaxes(
            title_text="% Inside 8 ft", range=[0, 100],
            showgrid=False, secondary_y=True,
        )

        st.plotly_chart(fig_trend, use_container_width=True,
                        config={'displayModeBar': False})
    else:
        st.info("No trend data available.")

    # ----------------------------------------------------------------
    # SECTION 5 — SHOT DETAIL
    # ----------------------------------------------------------------
    with st.expander("View All Short Game Shots"):
        if not sg["shot_detail"].empty:
            st.dataframe(sg["shot_detail"], use_container_width=True,
                         hide_index=True)
        else:
            st.info("No shot data available.")
