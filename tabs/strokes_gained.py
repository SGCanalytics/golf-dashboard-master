# ============================================================
# TAB: STROKES GAINED (formerly Overview)
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from ui.theme import (
    CHARCOAL, CHARCOAL_LIGHT, SLATE, WHITE, WARM_GRAY,
    ACCENT_PRIMARY, ACCENT_SECONDARY,
    POSITIVE, NEGATIVE, CHART_PUTTING, CHART_SHORT_GAME,
    FONT_HEADING, FONT_BODY, CARD_RADIUS, CARD_PADDING, OUTCOME_COLORS,
    BORDER_LIGHT,
)
from ui.chart_config import CHART_LAYOUT, sg_cell_style
from ui.components import (
    section_header, premium_hero_card, premium_stat_card, sg_sentiment,
)
from ui.formatters import format_sg, format_pct, format_score

from engines.overview import (
    overview_engine, build_sg_separators, build_sg_trend,
    build_scoring_by_par, build_hole_outcomes,
    build_sg_by_hole_pivot, build_shot_detail,
)


def strokes_gained_tab(
    filtered_df, hole_summary, num_rounds,
    driving_results, approach_results, short_game_results,
    putting_results, tiger5_results,
):

    overview = overview_engine(
        filtered_df, hole_summary, driving_results,
        approach_results, short_game_results, putting_results,
        tiger5_results,
    )

    total_sg = overview["total_sg"]
    sg_cat = overview.get("sg_by_category", {})
    sg_other_recovery = overview.get('sg_other_recovery', 0)

    # ----------------------------------------------------------------
    # 1. SG SUMMARY CARDS
    # ----------------------------------------------------------------
    section_header("Strokes Gained Summary")

    sg_drive = sg_cat.get('Driving', 0)
    sg_approach = sg_cat.get('Approach', 0)
    sg_putting = sg_cat.get('Putting', 0)
    sg_short = sg_cat.get('Short Game', 0)

    summary_metrics_row1 = [
        ('SG Total', total_sg),
        ('SG Drive', sg_drive),
        ('SG Approach', sg_approach),
    ]

    summary_metrics_row2 = [
        ('SG Putting', sg_putting),
        ('SG Short Game', sg_short),
        ('SG Other + Recovery', sg_other_recovery),
    ]

    cols1 = st.columns(3)
    for col, (label, val) in zip(cols1, summary_metrics_row1):
        pr = val / num_rounds if num_rounds > 0 else 0
        with col:
            premium_hero_card(
                label, format_sg(val),
                f"{format_sg(pr)} per round",
                sentiment=sg_sentiment(val),
            )

    cols2 = st.columns(3)
    for col, (label, val) in zip(cols2, summary_metrics_row2):
        pr = val / num_rounds if num_rounds > 0 else 0
        with col:
            premium_hero_card(
                label, format_sg(val),
                f"{format_sg(pr)} per round",
                sentiment=sg_sentiment(val),
            )

    # ----------------------------------------------------------------
    # 2. SG SEPARATORS
    # ----------------------------------------------------------------
    section_header("Strokes Gained Separators")

    separators, best_key, worst_key = build_sg_separators(filtered_df, num_rounds)

    if separators:
        row1 = st.columns(4)
        for col, (label, val, pr, key) in zip(row1, separators[:4]):
            border_style = ""
            if key == best_key:
                border_style = f"border:2px solid {POSITIVE};"
            elif key == worst_key:
                border_style = f"border:2px solid {NEGATIVE};"

            sent_color = POSITIVE if val >= 0 else NEGATIVE

            with col:
                st.markdown(f'''
                    <div style="background:{WHITE};border-radius:{CARD_RADIUS};
                         padding:{CARD_PADDING};text-align:center;
                         box-shadow:0 1px 4px rgba(0,0,0,0.04);
                         border:1px solid {BORDER_LIGHT};margin-bottom:1rem;{border_style}">
                        <div style="font-family:{FONT_BODY};font-size:0.65rem;font-weight:600;
                             color:{SLATE};text-transform:uppercase;letter-spacing:0.08em;
                             margin-bottom:0.5rem;">{label}</div>
                        <div style="font-family:{FONT_HEADING};font-size:2rem;font-weight:700;
                             color:{sent_color};line-height:1;">{format_sg(val)}</div>
                        <div style="font-family:{FONT_BODY};font-size:0.65rem;color:{SLATE};
                             margin-top:0.3rem;">{format_sg(pr)} per round</div>
                    </div>
                ''', unsafe_allow_html=True)

        row2 = st.columns(4)
        for col, (label, val, pr, key) in zip(row2, separators[4:]):
            border_style = ""
            if key == best_key:
                border_style = f"border:2px solid {POSITIVE};"
            elif key == worst_key:
                border_style = f"border:2px solid {NEGATIVE};"

            sent_color = POSITIVE if val >= 0 else NEGATIVE

            with col:
                st.markdown(f'''
                    <div style="background:{WHITE};border-radius:{CARD_RADIUS};
                         padding:{CARD_PADDING};text-align:center;
                         box-shadow:0 1px 4px rgba(0,0,0,0.04);
                         border:1px solid {BORDER_LIGHT};margin-bottom:1rem;{border_style}">
                        <div style="font-family:{FONT_BODY};font-size:0.65rem;font-weight:600;
                             color:{SLATE};text-transform:uppercase;letter-spacing:0.08em;
                             margin-bottom:0.5rem;">{label}</div>
                        <div style="font-family:{FONT_HEADING};font-size:2rem;font-weight:700;
                             color:{sent_color};line-height:1;">{format_sg(val)}</div>
                        <div style="font-family:{FONT_BODY};font-size:0.65rem;color:{SLATE};
                             margin-top:0.3rem;">{format_sg(pr)} per round</div>
                    </div>
                ''', unsafe_allow_html=True)

        # Add legend
        st.markdown(
            f'<p style="font-family:{FONT_BODY};font-size:0.7rem;color:{SLATE};'
            f'margin-top:0.5rem;">'
            f'<span style="color:{POSITIVE};">●</span> Best Total SG &nbsp;&nbsp;'
            f'<span style="color:{NEGATIVE};">●</span> Worst Total SG</p>',
            unsafe_allow_html=True,
        )

    # ----------------------------------------------------------------
    # 3. HOLE-BY-HOLE SG PIVOT
    # ----------------------------------------------------------------
    section_header("Hole-by-Hole Strokes Gained")

    sg_pivot = build_sg_by_hole_pivot(filtered_df, hole_summary)

    if not sg_pivot.empty:
        hole_cols = [c for c in sg_pivot.columns if c != 'Shot Type']

        html = '<div style="overflow-x:auto;">'
        html += (
            '<table style="width:100%;border-collapse:separate;'
            'border-spacing:0;font-family:Inter,sans-serif;'
            f'background:{WHITE};border-radius:12px;overflow:hidden;'
            'box-shadow:0 4px 16px rgba(0,0,0,0.08);table-layout:fixed;">'
        )

        label_w = '90px'
        html += '<tr>'
        html += (
            f'<th style="background:{WARM_GRAY};color:{CHARCOAL};'
            f'font-weight:600;font-size:0.65rem;text-transform:uppercase;'
            f'letter-spacing:0.03em;padding:0.55rem 0.25rem;text-align:left;'
            f'border-bottom:2px solid {ACCENT_PRIMARY};width:{label_w};'
            f'position:sticky;left:0;z-index:1;">Shot Type</th>'
        )
        for h in hole_cols:
            is_total_col = (str(h) == 'Total')
            th_extra = (f'border-left:2px solid {ACCENT_PRIMARY};'
                        'font-weight:700;') if is_total_col else ''
            html += (
                f'<th style="background:{WARM_GRAY};color:{CHARCOAL};'
                f'font-weight:600;font-size:0.65rem;'
                f'border-bottom:2px solid {ACCENT_PRIMARY};'
                f'padding:0.55rem 0.15rem;text-align:center;'
                f'white-space:nowrap;{th_extra}">{h}</th>'
            )
        html += '</tr>'

        for _, row in sg_pivot.iterrows():
            shot_type = row['Shot Type']
            is_total_row = (shot_type == 'Total SG')
            is_par_row = (shot_type == 'Hole Par')
            is_score_row = (shot_type == 'Hole Score')
            is_info_row = is_par_row or is_score_row

            if is_total_row:
                row_bg = (
                    f'background:linear-gradient(90deg,'
                    f'{ACCENT_PRIMARY} 0%,{ACCENT_SECONDARY} 100%);'
                )
                label_style = (
                    f'font-weight:700;color:{WHITE};font-size:0.72rem;'
                    f'padding:0.5rem 0.25rem;text-align:left;'
                    f'position:sticky;left:0;width:{label_w};'
                )
                cell_base = (
                    f'font-weight:700;color:{WHITE};font-size:0.72rem;'
                    'padding:0.5rem 0.15rem;text-align:center;'
                )
            elif is_info_row:
                row_bg = f'background:{WARM_GRAY};'
                label_style = (
                    f'font-weight:600;color:{CHARCOAL};font-size:0.72rem;'
                    f'padding:0.4rem 0.25rem;text-align:left;'
                    f'border-bottom:1px solid {BORDER_LIGHT};position:sticky;left:0;'
                    f'background:{WARM_GRAY};width:{label_w};'
                )
                cell_base = (
                    f'font-size:0.72rem;padding:0.4rem 0.15rem;'
                    f'text-align:center;border-bottom:1px solid {BORDER_LIGHT};'
                    f'background:{WARM_GRAY};color:{CHARCOAL};font-weight:500;'
                )
            else:
                row_bg = ''
                label_style = (
                    f'font-weight:500;color:{CHARCOAL};font-size:0.72rem;'
                    f'padding:0.4rem 0.25rem;text-align:left;'
                    f'border-bottom:1px solid {BORDER_LIGHT};position:sticky;left:0;'
                    f'background:{WHITE};width:{label_w};'
                )
                cell_base = (
                    'font-size:0.72rem;padding:0.4rem 0.15rem;'
                    f'text-align:center;border-bottom:1px solid {BORDER_LIGHT};'
                )

            html += f'<tr style="{row_bg}">'
            html += f'<td style="{label_style}">{shot_type}</td>'

            for h in hole_cols:
                val = row[h]
                is_total_col = (str(h) == 'Total')
                border_left = (
                    f'border-left:2px solid {ACCENT_PRIMARY};'
                    if is_total_col else ''
                )

                if is_total_row:
                    style = cell_base + border_left
                elif is_info_row:
                    style = cell_base + border_left
                else:
                    style = cell_base + sg_cell_style(val) + border_left
                    if is_total_col:
                        style += 'font-weight:600;'

                # Format display value
                if is_info_row:
                    # Plain numbers for Par/Score (no +/- formatting)
                    if is_par_row:
                        display = f'{int(val)}' if val == int(val) else f'{val:.1f}'
                    else:  # is_score_row
                        display = f'{val:.2f}' if val != 0 else '0.00'
                else:
                    # SG values with +/- formatting
                    display = f'{val:+.2f}' if val != 0 else '0.00'

                html += f'<td style="{style}">{display}</td>'

            html += '</tr>'

        html += '</table></div>'
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("No hole-by-hole data available.")

    # ----------------------------------------------------------------
    # 4. SG TREND BY ROUND
    # ----------------------------------------------------------------
    section_header("Strokes Gained Trend")

    sg_trend = build_sg_trend(filtered_df)

    if not sg_trend.empty:
        use_ma_sg = st.checkbox("Apply Moving Average", value=False,
                                key="overview_sg_trend_ma")
        categories = ['Driving', 'Approach', 'Short Game', 'Putting']
        cat_colors = [ACCENT_PRIMARY, CHARCOAL, CHART_SHORT_GAME, CHART_PUTTING]

        if use_ma_sg:
            ma_window = st.selectbox("Moving Average Window", [3, 5, 10],
                                     index=0, key="overview_sg_trend_window")
            for cat in categories:
                sg_trend[f'{cat}_MA'] = (
                    sg_trend[cat].rolling(window=ma_window).mean()
                )
            plot_cols = [f'{cat}_MA' for cat in categories]
        else:
            plot_cols = categories

        fig_sg_trend = go.Figure()
        for cat, pcol, color in zip(categories, plot_cols, cat_colors):
            fig_sg_trend.add_trace(go.Scatter(
                x=sg_trend['Label'],
                y=sg_trend[pcol],
                name=cat,
                mode='lines+markers',
                line=dict(color=color, width=2),
                marker=dict(size=6),
            ))

        fig_sg_trend.update_layout(
            **CHART_LAYOUT,
            xaxis_title='',
            yaxis_title='Strokes Gained',
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02,
                        xanchor='right', x=1),
            margin=dict(t=60, b=80, l=60, r=40),
            xaxis=dict(tickangle=-45),
            yaxis=dict(gridcolor=BORDER_LIGHT, zerolinecolor=CHARCOAL,
                       zerolinewidth=2),
            hovermode='x unified',
        )

        st.plotly_chart(fig_sg_trend, use_container_width=True,
                        config={'displayModeBar': False})
    else:
        st.info("No data available for SG trend.")

    # ----------------------------------------------------------------
    # 5. SCORING & HOLE OUTCOMES
    # ----------------------------------------------------------------
    section_header("Scoring & Hole Outcomes")

    outcomes = build_hole_outcomes(hole_summary)
    scoring_par = build_scoring_by_par(hole_summary)

    col_donut, col_cards = st.columns([3, 2])

    with col_donut:
        if not outcomes.empty:
            chart_data = outcomes[outcomes['Count'] > 0]
            total_holes = int(outcomes['Count'].sum())

            fig_outcomes = go.Figure(data=[go.Pie(
                labels=chart_data['Score'],
                values=chart_data['Count'],
                hole=0.6,
                marker_colors=[OUTCOME_COLORS.get(s, SLATE)
                               for s in chart_data['Score']],
                textinfo='label+percent',
                textposition='outside',
                textfont=dict(family='Inter', size=12),
                pull=[0.02] * len(chart_data),
                domain=dict(x=[0.1, 0.9], y=[0.05, 0.95]),
            )])

            fig_outcomes.update_layout(
                **CHART_LAYOUT,
                showlegend=False,
                margin=dict(t=30, b=30, l=40, r=40),
                height=420,
                annotations=[dict(
                    text=f'<b>{total_holes}</b><br>Holes',
                    x=0.5, y=0.5,
                    font=dict(family='Playfair Display', size=22,
                              color=CHARCOAL),
                    showarrow=False,
                )],
            )

            st.plotly_chart(fig_outcomes, use_container_width=True)
        else:
            st.info("No hole outcome data available.")

    with col_cards:
        if not scoring_par.empty:
            overall_avg = hole_summary['Hole Score'].mean()
            overall_sg = hole_summary['total_sg'].sum()
            overall_sg_hole = hole_summary['total_sg'].mean()

            sg_color = POSITIVE if overall_sg >= 0 else NEGATIVE
            st.markdown(f'''
                <div style="background:{WHITE};border-radius:12px;
                     padding:1rem 1.25rem;
                     border:1px solid {BORDER_LIGHT};border-left:4px solid {ACCENT_PRIMARY};
                     box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:0.75rem;
                     display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-family:{FONT_BODY};font-size:0.7rem;font-weight:600;
                             color:{ACCENT_PRIMARY};text-transform:uppercase;
                             letter-spacing:0.08em;">Overall</div>
                        <div style="font-family:{FONT_HEADING};font-size:1.8rem;
                             font-weight:700;color:{CHARCOAL};line-height:1.1;">
                            {overall_avg:.2f}</div>
                        <div style="font-family:{FONT_BODY};font-size:0.65rem;
                             color:{SLATE};">Scoring Avg</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:{FONT_HEADING};font-size:1.4rem;
                             font-weight:700;color:{sg_color};">
                            {overall_sg:+.2f}</div>
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;
                             color:{SLATE};">Total SG</div>
                        <div style="font-family:{FONT_HEADING};font-size:1rem;
                             font-weight:600;color:{sg_color};margin-top:0.2rem;">
                            {overall_sg_hole:+.2f}</div>
                        <div style="font-family:{FONT_BODY};font-size:0.6rem;
                             color:{SLATE};">SG / Hole</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            for _, row in scoring_par.iterrows():
                par_val = int(row['Par'])
                sc_avg = row['Scoring Avg']
                t_sg = row['Total SG']
                sg_h = row['SG / Hole']
                holes_n = int(row['Holes Played'])
                sg_color_p = POSITIVE if t_sg >= 0 else NEGATIVE
                vs_par = sc_avg - par_val

                st.markdown(f'''
                    <div style="background:{WHITE};border-radius:10px;
                         padding:0.85rem 1.25rem;margin-bottom:0.6rem;
                         border-left:4px solid {ACCENT_PRIMARY};
                         box-shadow:0 2px 6px rgba(0,0,0,0.06);
                         display:flex;justify-content:space-between;
                         align-items:center;">
                        <div>
                            <div style="font-family:{FONT_BODY};font-size:0.7rem;
                                 font-weight:600;color:{SLATE};
                                 text-transform:uppercase;
                                 letter-spacing:0.06em;">
                                Par {par_val}
                                <span style="color:{SLATE};font-weight:400;">
                                    &middot; {holes_n} holes</span></div>
                            <div style="font-family:{FONT_HEADING};
                                 font-size:1.5rem;font-weight:700;
                                 color:{CHARCOAL};line-height:1.1;">
                                {sc_avg:.2f}
                                <span style="font-size:0.8rem;color:{SLATE};">
                                    ({vs_par:+.2f})</span></div>
                            <div style="font-family:{FONT_BODY};font-size:0.6rem;
                                 color:{SLATE};">Scoring Avg (vs Par)</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-family:{FONT_HEADING};
                                 font-size:1.2rem;font-weight:700;
                                 color:{sg_color_p};">{t_sg:+.2f}</div>
                            <div style="font-family:{FONT_BODY};font-size:0.6rem;
                                 color:{SLATE};">Total SG</div>
                            <div style="font-family:{FONT_HEADING};
                                 font-size:0.95rem;font-weight:600;
                                 color:{sg_color_p};margin-top:0.15rem;">
                                {sg_h:+.2f}</div>
                            <div style="font-family:{FONT_BODY};font-size:0.6rem;
                                 color:{SLATE};">SG / Hole</div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No scoring data available.")

    # ----------------------------------------------------------------
    # SHOT LEVEL DETAIL
    # ----------------------------------------------------------------
    with st.expander("View Shot Level Detail"):
        shot_detail = build_shot_detail(filtered_df)

        if shot_detail:
            for round_lbl, detail_df in shot_detail.items():
                st.markdown(f"#### {round_lbl}")
                st.dataframe(detail_df, use_container_width=True,
                             hide_index=True)
        else:
            st.info("No shot data available.")
