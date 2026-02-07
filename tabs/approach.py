# ============================================================
# TAB: APPROACH
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from ui.theme import (
    CHARCOAL, SLATE, ACCENT_PRIMARY, ACCENT_SECONDARY,
    POSITIVE, NEGATIVE, BORDER_LIGHT,
    THRESHOLDS,
)
from ui.chart_config import CHART_LAYOUT, sg_bar_color
from ui.components import (
    section_header, premium_hero_card, premium_stat_card, sg_sentiment,
)
from ui.formatters import format_sg, format_pct


def approach_tab(approach, num_rounds):
    if approach["empty"]:
        st.warning("No approach data available for the selected filters.")
        return

    section_header("Approach Play")

    # ----------------------------------------------------------------
    # SECTION 1: HERO CARDS
    # ----------------------------------------------------------------
    total_sg = approach["total_sg"]
    sg_per_round = approach["sg_per_round"]
    sg_fairway = approach["sg_fairway"]
    sg_rough = approach["sg_rough"]
    pos_rate = approach["positive_shot_rate"]
    poor_rate = approach["poor_shot_rate"]

    hero_items = [
        ("Total SG Approach", format_sg(total_sg),
         f"{format_sg(sg_per_round)} per round", sg_sentiment(total_sg)),
        ("SG App Fairway", format_sg(sg_fairway),
         "Starting Lie: Fairway", sg_sentiment(sg_fairway)),
        ("SG App Rough", format_sg(sg_rough),
         "Starting Lie: Rough", sg_sentiment(sg_rough)),
        ("Positive Shot Rate", format_pct(pos_rate),
         "Shots with SG \u2265 0.00",
         "positive" if pos_rate >= THRESHOLDS["pct_positive_shot"] else "negative"),
        ("Poor Shot Rate", format_pct(poor_rate),
         "Shots with SG \u2264 -0.15",
         "positive" if poor_rate <= THRESHOLDS["pct_poor_shot"] else "negative"),
    ]

    h_cols = st.columns(5)
    for col, (label, value, unit, sent) in zip(h_cols, hero_items):
        with col:
            premium_hero_card(label, value, unit, sentiment=sent)

    # ----------------------------------------------------------------
    # SECTION 2: PERFORMANCE BY DISTANCE
    # ----------------------------------------------------------------
    section_header("Approach Performance by Distance")

    best_key = approach["best_bucket"]
    worst_key = approach["worst_bucket"]

    # Row 1: Fairway / Tee
    st.markdown(
        f'<p style="font-family:{st.__name__ and "Inter"},sans-serif;'
        f'font-size:0.85rem;font-weight:600;color:{ACCENT_SECONDARY};'
        f'text-transform:uppercase;letter-spacing:0.08em;'
        f'margin-bottom:0.5rem;">From Fairway / Tee</p>',
        unsafe_allow_html=True,
    )

    ft_buckets = ["50\u2013100", "100\u2013150", "150\u2013200", ">200"]
    ft_cols = st.columns(4)

    for col, bucket in zip(ft_cols, ft_buckets):
        m = approach["fairway_tee_metrics"][bucket]
        card_key = f"FT|{bucket}"
        sent = sg_sentiment(m["total_sg"])

        if card_key == best_key:
            border_style = f"border:2px solid {POSITIVE};"
        elif card_key == worst_key:
            border_style = f"border:2px solid {NEGATIVE};"
        else:
            border_style = ""

        with col:
            st.markdown(f'''
                <div style="background:#fff;border-radius:12px;
                     padding:1.25rem 1rem;text-align:center;
                     box-shadow:0 2px 8px rgba(0,0,0,0.06);
                     border:1px solid #e2e2e2;margin-bottom:1rem;{border_style}">
                    <div style="font-family:Inter,sans-serif;font-size:0.7rem;
                         font-weight:600;color:{SLATE};text-transform:uppercase;
                         letter-spacing:0.08em;margin-bottom:0.5rem;">
                         {bucket} Yards</div>
                    <div style="font-family:Playfair Display,serif;font-size:2rem;
                         font-weight:700;color:{POSITIVE if m['total_sg'] >= 0 else NEGATIVE};
                         line-height:1;">{m['total_sg']:+.2f}</div>
                    <div style="font-family:Inter,sans-serif;font-size:0.7rem;
                         color:{SLATE};margin-top:0.3rem;">
                         {m['shots']} shots &middot; Prox: {m['prox']:.1f} ft
                         &middot; GIR: {m['green_hit_pct']:.0f}%</div>
                </div>
            ''', unsafe_allow_html=True)

    # Row 2: Rough
    st.markdown(
        f'<p style="font-family:Inter,sans-serif;font-size:0.85rem;'
        f'font-weight:600;color:{ACCENT_SECONDARY};text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-top:1rem;margin-bottom:0.5rem;">'
        f'From Rough</p>',
        unsafe_allow_html=True,
    )

    rough_buckets = ["<150", ">150"]
    r_cols = st.columns([1, 1, 1, 1])

    for col, rb in zip(r_cols[:2], rough_buckets):
        m = approach["rough_metrics"][rb]
        card_key = f"R|{rb}"

        if card_key == best_key:
            border_style = f"border:2px solid {POSITIVE};"
        elif card_key == worst_key:
            border_style = f"border:2px solid {NEGATIVE};"
        else:
            border_style = ""

        with col:
            st.markdown(f'''
                <div style="background:#fff;border-radius:12px;
                     padding:1.25rem 1rem;text-align:center;
                     box-shadow:0 2px 8px rgba(0,0,0,0.06);
                     border:1px solid #e2e2e2;margin-bottom:1rem;{border_style}">
                    <div style="font-family:Inter,sans-serif;font-size:0.7rem;
                         font-weight:600;color:{SLATE};text-transform:uppercase;
                         letter-spacing:0.08em;margin-bottom:0.5rem;">
                         {rb} Yards</div>
                    <div style="font-family:Playfair Display,serif;font-size:2rem;
                         font-weight:700;color:{POSITIVE if m['total_sg'] >= 0 else NEGATIVE};
                         line-height:1;">{m['total_sg']:+.2f}</div>
                    <div style="font-family:Inter,sans-serif;font-size:0.7rem;
                         color:{SLATE};margin-top:0.3rem;">
                         {m['shots']} shots &middot; Prox: {m['prox']:.1f} ft
                         &middot; GIR: {m['green_hit_pct']:.0f}%</div>
                </div>
            ''', unsafe_allow_html=True)

    # Best / worst legend
    st.markdown(
        f'<p style="font-family:Inter,sans-serif;font-size:0.7rem;color:#999;'
        f'margin-top:0.5rem;">'
        f'<span style="color:{POSITIVE};">\u25aa</span> Best Total SG &nbsp;&nbsp;'
        f'<span style="color:{NEGATIVE};">\u25aa</span> Worst Total SG</p>',
        unsafe_allow_html=True,
    )

    # ----------------------------------------------------------------
    # SECTION 3: APPROACH PROFILE
    # ----------------------------------------------------------------
    section_header("Approach Profile")

    profile_df = approach["profile_df"]

    if not profile_df.empty:
        profile_df['Label'] = profile_df.apply(
            lambda r: f"{r['Group']}: {r['Category']}", axis=1
        )
        label_order = profile_df['Label'].tolist()

        # Green Hit %
        fig_gir = go.Figure(go.Bar(
            y=profile_df['Label'],
            x=profile_df['Green Hit %'],
            orientation='h',
            marker_color=[ACCENT_PRIMARY if g == 'Fairway / Tee' else NEGATIVE
                          for g in profile_df['Group']],
            text=profile_df['Green Hit %'].apply(lambda v: f"{v:.0f}%"),
            textposition='outside',
            textfont=dict(family='Inter', size=12, color=CHARCOAL),
        ))
        fig_gir.update_layout(
            **CHART_LAYOUT,
            title=dict(text='Green Hit %', font=dict(size=14)),
            yaxis=dict(categoryorder='array',
                       categoryarray=label_order[::-1]),
            xaxis=dict(title='', showticklabels=False),
            margin=dict(t=40, b=20, l=160, r=60),
            height=280,
        )
        st.plotly_chart(fig_gir, use_container_width=True)

        # Total SG
        bar_colors = [sg_bar_color(v) for v in profile_df['Total SG']]
        fig_sg = go.Figure(go.Bar(
            y=profile_df['Label'],
            x=profile_df['Total SG'],
            orientation='h',
            marker_color=bar_colors,
            text=profile_df['Total SG'].apply(lambda v: f"{v:+.2f}"),
            textposition='outside',
            textfont=dict(family='Inter', size=12, color=CHARCOAL),
        ))
        fig_sg.update_layout(
            **CHART_LAYOUT,
            title=dict(text='Total SG', font=dict(size=14)),
            yaxis=dict(categoryorder='array',
                       categoryarray=label_order[::-1]),
            xaxis=dict(title='', showticklabels=False),
            margin=dict(t=40, b=20, l=160, r=60),
            height=280,
        )
        st.plotly_chart(fig_sg, use_container_width=True)

        # Proximity
        fig_prox = go.Figure(go.Bar(
            y=profile_df['Label'],
            x=profile_df['Proximity'],
            orientation='h',
            marker_color=[ACCENT_PRIMARY if g == 'Fairway / Tee' else NEGATIVE
                          for g in profile_df['Group']],
            text=profile_df['Proximity'].apply(lambda v: f"{v:.1f} ft"),
            textposition='outside',
            textfont=dict(family='Inter', size=12, color=CHARCOAL),
        ))
        fig_prox.update_layout(
            **CHART_LAYOUT,
            title=dict(text='Proximity (ft)', font=dict(size=14)),
            yaxis=dict(categoryorder='array',
                       categoryarray=label_order[::-1]),
            xaxis=dict(title='', showticklabels=False),
            margin=dict(t=40, b=20, l=160, r=60),
            height=280,
        )
        st.plotly_chart(fig_prox, use_container_width=True)

    # ----------------------------------------------------------------
    # SECTION 4: HEATMAP
    # ----------------------------------------------------------------
    section_header("Strokes Gained per Shot Heatmap")

    heatmap_sg = approach["heatmap_sg"]
    heatmap_counts = approach["heatmap_counts"]

    if not heatmap_sg.empty:
        annotations = []
        for i, row_label in enumerate(heatmap_sg.index):
            for j, col_label in enumerate(heatmap_sg.columns):
                sg_val = heatmap_sg.iloc[i, j]
                cnt_val = (int(heatmap_counts.iloc[i, j])
                           if not heatmap_counts.empty else 0)
                if np.isnan(sg_val):
                    continue
                annotations.append(dict(
                    x=col_label, y=row_label,
                    text=f"{sg_val:+.2f}<br><span style='font-size:10px'>"
                         f"({cnt_val})</span>",
                    showarrow=False,
                    font=dict(family='Inter', size=12, color='#000'),
                ))

        fig_heat = px.imshow(
            heatmap_sg,
            color_continuous_scale='RdYlGn',
            aspect='auto',
            labels=dict(x='Starting Location', y='Distance Bucket',
                        color='SG/Shot'),
        )
        fig_heat.update_layout(
            **CHART_LAYOUT,
            annotations=annotations,
            height=400,
        )
        fig_heat.update_traces(showscale=True)
        st.plotly_chart(fig_heat, use_container_width=True)

    # ----------------------------------------------------------------
    # SECTION 5: OUTCOME DISTRIBUTION
    # ----------------------------------------------------------------
    section_header("Approach Outcome Distribution")

    outcome_df = approach["outcome_df"]

    if not outcome_df.empty:
        col_out1, col_out2 = st.columns(2)

        with col_out1:
            fig_pct = go.Figure(go.Bar(
                x=outcome_df['Ending Location'],
                y=outcome_df['Pct'],
                marker_color=ACCENT_PRIMARY,
                text=outcome_df['Pct'].apply(lambda v: f"{v:.1f}%"),
                textposition='outside',
                textfont=dict(family='Inter', size=12, color=CHARCOAL),
            ))
            fig_pct.update_layout(
                **CHART_LAYOUT,
                title=dict(text='% of Shots by Ending Location',
                           font=dict(size=14)),
                yaxis=dict(title='% of Shots', gridcolor=BORDER_LIGHT),
                xaxis=dict(title=''),
                margin=dict(t=40, b=40, l=60, r=40),
                height=350,
            )
            st.plotly_chart(fig_pct, use_container_width=True)

        with col_out2:
            bar_colors = [sg_bar_color(v) for v in outcome_df['Total SG']]
            fig_out_sg = go.Figure(go.Bar(
                x=outcome_df['Ending Location'],
                y=outcome_df['Total SG'],
                marker_color=bar_colors,
                text=outcome_df['Total SG'].apply(lambda v: f"{v:+.2f}"),
                textposition='outside',
                textfont=dict(family='Inter', size=12, color=CHARCOAL),
            ))
            fig_out_sg.update_layout(
                **CHART_LAYOUT,
                title=dict(text='Total SG by Ending Location',
                           font=dict(size=14)),
                yaxis=dict(title='Total SG', gridcolor=BORDER_LIGHT,
                           zerolinecolor=CHARCOAL, zerolinewidth=2),
                xaxis=dict(title=''),
                margin=dict(t=40, b=40, l=60, r=40),
                height=350,
            )
            st.plotly_chart(fig_out_sg, use_container_width=True)

    # ----------------------------------------------------------------
    # SECTION 6: TREND
    # ----------------------------------------------------------------
    section_header("Approach SG Trend by Round")

    trend_df = approach["trend_df"]

    use_ma = st.checkbox("Apply Moving Average", value=False,
                         key="approach_ma")

    if use_ma:
        window = st.selectbox("Moving Average Window", [3, 5, 10], index=0,
                              key="approach_ma_window")
        trend_df["SG_MA"] = trend_df["Strokes Gained"].rolling(
            window=window).mean()
        y_col = "SG_MA"
    else:
        y_col = "Strokes Gained"

    fig_trend = px.line(
        trend_df, x="Label", y=y_col, markers=True,
        title="SG: Approach Trend",
        color_discrete_sequence=[CHARCOAL],
    )
    fig_trend.update_layout(
        **CHART_LAYOUT,
        xaxis_title='', yaxis_title='Strokes Gained', height=400,
    )
    fig_trend.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_trend, use_container_width=True)

    # ----------------------------------------------------------------
    # SECTION 7: SHOT DETAIL
    # ----------------------------------------------------------------
    detail_df = approach["detail_df"]

    if not detail_df.empty:
        with st.expander("Approach Shot Detail"):
            st.dataframe(detail_df, use_container_width=True,
                         hide_index=True)
