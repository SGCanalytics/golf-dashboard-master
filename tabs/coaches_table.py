import streamlit as st
import pandas as pd
from ui.components import section_header
from engines.coaches_table import build_coaches_table_results

# ============================================================
# COACHES TABLE TAB
# Comprehensive player performance comparison table
# ============================================================

# SG columns that receive color coding
_SG_COLS = [
    'SG/Rd', 'SGD/Rd', 'SGA/Rd', 'SGSG/Rd', 'SGP/Rd', 'SGO/Rd',
    'GZ SG', 'YZ SG', 'RZ SG', 'SG25-50', 'SG0-25', 'SG4-6', 'SG7-10'
]

# Normalization cap: values at ±MAX_SG get full saturation
_MAX_SG = 2.0

# Theme colors (from ui/theme.py)
_POSITIVE_BG = (209, 250, 229)   # #D1FAE5
_NEGATIVE_BG = (254, 215, 215)   # #FED7D7


def coaches_table_tab(filtered_df, hole_summary):
    """
    Render coaches table with rank/value toggle and SG color coding.

    Args:
        filtered_df: Shot-level data (from app.py filters)
        hole_summary: Hole-level aggregated data
    """
    section_header("Coaches Table")

    if filtered_df.empty or hole_summary.empty:
        st.warning("No player data available for the selected filters.")
        return

    coaches_table_results = build_coaches_table_results(filtered_df, hole_summary)

    if coaches_table_results["empty"]:
        st.warning("No player data available for the selected filters.")
        return

    players_df = coaches_table_results["players_df"].copy()

    # Toggle for rank vs values
    show_rank = st.checkbox(
        "Show Rank Instead of Values",
        value=False,
        key="coaches_table_show_rank",
        help="Toggle to view player rankings (1 = best) instead of actual metric values"
    )

    if show_rank:
        st.dataframe(
            _create_ranked_df(players_df, coaches_table_results["column_groups"]),
            use_container_width=True,
            hide_index=True,
            height=600
        )
    else:
        st.dataframe(
            _create_styled_df(players_df),
            use_container_width=True,
            hide_index=True,
            height=600
        )


def _sg_bg_color(val):
    """
    Map a numeric SG value to a background-color CSS string.
    0  → white (#FFFFFF)
    positive → transitions to green (#D1FAE5)
    negative → transitions to red  (#FED7D7)
    """
    try:
        v = float(val)
    except (TypeError, ValueError):
        return ''

    intensity = min(abs(v) / _MAX_SG, 1.0)

    if v > 0:
        target = _POSITIVE_BG
    elif v < 0:
        target = _NEGATIVE_BG
    else:
        return 'background-color: #FFFFFF'

    r = int(255 + (target[0] - 255) * intensity)
    g = int(255 + (target[1] - 255) * intensity)
    b = int(255 + (target[2] - 255) * intensity)
    return f'background-color: rgb({r},{g},{b})'


def _create_styled_df(players_df):
    """
    Return a pandas Styler with:
    - Consistent numeric formatting for all columns
    - White→green/red background gradient on all SG columns
    """
    # Build format strings for each column
    format_dict = {}
    sg_cols_present = [c for c in _SG_COLS if c in players_df.columns]

    for col in sg_cols_present:
        format_dict[col] = '{:+.2f}'

    for col in ['BB%', 'DO%', 'GP%', 'FW%', 'Obs%', 'Pen%', 'Lag%']:
        if col in players_df.columns:
            format_dict[col] = '{:.1f}%'

    for col in ['T5 Fails/Rd', '3P/Rd', 'DB/Rd', 'P5B/Rd', 'MG/Rd', '125B/Rd', 'SF/Rd']:
        if col in players_df.columns:
            format_dict[col] = '{:.2f}'

    if 'Avg Score' in players_df.columns:
        format_dict['Avg Score'] = '{:.1f}'

    styler = (
        players_df.style
        .format(format_dict, na_rep='-')
        .map(_sg_bg_color, subset=sg_cols_present)
    )

    return styler


def _create_ranked_df(players_df, column_groups):
    """
    Convert numeric values to ranks (1 = best).
    Higher-is-better metrics rank descending; lower-is-better rank ascending.
    """
    ranked_df = players_df[['Player']].copy()

    higher_better = [
        'SG/Rd', 'SGD/Rd', 'SGA/Rd', 'SGSG/Rd', 'SGP/Rd', 'SGO/Rd',
        'GZ SG', 'YZ SG', 'RZ SG', 'SG25-50', 'SG0-25', 'SG4-6', 'SG7-10',
        'BB%', 'GP%', 'FW%'
    ]
    lower_better = [
        'Avg Score', 'T5 Fails/Rd', '3P/Rd', 'DB/Rd', 'P5B/Rd', 'MG/Rd',
        '125B/Rd', 'SF/Rd', 'DO%', 'BT', 'Obs%', 'Pen%', 'Lag%'
    ]

    for col in players_df.columns:
        if col in higher_better:
            ranked_df[col] = players_df[col].rank(ascending=False, method='min').astype(int)
        elif col in lower_better:
            ranked_df[col] = players_df[col].rank(ascending=True, method='min').astype(int)
        elif col not in ['Player', 'Rounds']:
            ranked_df[col] = players_df[col]

    return ranked_df
