import streamlit as st
import pandas as pd
from ui.components import section_header
from engines.coaches_table import build_coaches_table_results

# ============================================================
# COACHES TABLE TAB
# Comprehensive player performance comparison table
# ============================================================


def coaches_table_tab(filtered_df, hole_summary):
    """
    Render coaches table with tournament filter and rank/value toggle.

    Args:
        filtered_df: Shot-level data (from app.py filters)
        hole_summary: Hole-level aggregated data
    """
    section_header("Coaches Table")

    # Handle empty data
    if filtered_df.empty or hole_summary.empty:
        st.warning("No player data available for the selected filters.")
        return

    # Get list of tournaments for dropdown
    tournaments = sorted(filtered_df['Tournament'].unique())

    # Tournament selector (independent of sidebar filter)
    st.markdown("### Filter by Tournament")
    tournament_options = ["All Tournaments"] + tournaments
    selected_tournament = st.selectbox(
        "Select Tournament",
        options=tournament_options,
        index=0,
        key="coaches_table_tournament",
        label_visibility="collapsed"
    )

    # Filter data by selected tournament
    if selected_tournament != "All Tournaments":
        tournament_filtered_df = filtered_df[filtered_df['Tournament'] == selected_tournament].copy()
        # Get Round IDs from the tournament-filtered data
        tournament_rounds = tournament_filtered_df['Round ID'].unique()
        tournament_hole_summary = hole_summary[hole_summary['Round ID'].isin(tournament_rounds)].copy()
    else:
        tournament_filtered_df = filtered_df.copy()
        tournament_hole_summary = hole_summary.copy()

    # Check if filtered result is empty
    if tournament_filtered_df.empty:
        st.info(f"No data available for {selected_tournament}")
        return

    # Call engine with tournament-filtered data
    coaches_table_results = build_coaches_table_results(
        tournament_filtered_df,
        tournament_hole_summary
    )

    if coaches_table_results["empty"]:
        st.info(f"No data available for {selected_tournament}")
        return

    players_df = coaches_table_results["players_df"].copy()

    # Toggle for rank vs values
    show_rank = st.checkbox(
        "Show Rank Instead of Values",
        value=False,
        key="coaches_table_show_rank",
        help="Toggle to view player rankings (1 = best) instead of actual metric values"
    )

    # Create display dataframe
    if show_rank:
        final_df = _create_ranked_df(players_df, coaches_table_results["column_groups"])
    else:
        final_df = _create_values_df(players_df, coaches_table_results["column_groups"])

    # Display metric groups legend
    st.markdown("### Metric Categories")
    st.markdown("""
    **Basic**: Player info | **Tiger 5**: Fail metrics | **Scoring**: Momentum
    **Total SG**: Overall strokes gained | **Driving**: Tee shots | **Approach**: Iron play
    **Short Game**: Chipping/pitching | **Putting**: Green performance | **Other**: Recovery shots
    """)

    # Render table
    st.dataframe(
        final_df,
        use_container_width=True,
        hide_index=True,
        height=600
    )


def _create_ranked_df(players_df, column_groups):
    """
    Convert values to ranks within the displayed subset.
    Lower rank number = better performance.
    """
    ranked_df = players_df[['Player']].copy()

    # Higher is better (rank descending: highest value gets rank 1)
    higher_better = [
        'SG/Rd', 'SGD/Rd', 'SGA/Rd', 'SGSG/Rd', 'SGP/Rd', 'SGO/Rd',
        'GZ SG', 'YZ SG', 'RZ SG', 'SG25-50', 'SG0-25', 'SG4-6', 'SG7-10',
        'BB%', 'GP%', 'FW%'
    ]

    # Lower is better (rank ascending: lowest value gets rank 1)
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


def _create_values_df(players_df, column_groups):
    """
    Format values for display with appropriate precision and units.
    """
    formatted_df = players_df.copy()

    # SG metrics: +/- sign, 2 decimal places
    sg_cols = [
        'SG/Rd', 'SGD/Rd', 'SGA/Rd', 'SGSG/Rd', 'SGP/Rd', 'SGO/Rd',
        'GZ SG', 'YZ SG', 'RZ SG', 'SG25-50', 'SG0-25', 'SG4-6', 'SG7-10'
    ]
    for col in sg_cols:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:+.2f}")

    # Percentages: 1 decimal place + %
    pct_cols = ['BB%', 'DO%', 'GP%', 'FW%', 'Obs%', 'Pen%', 'Lag%']
    for col in pct_cols:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.1f}%")

    # Per-round metrics: 2 decimal places
    pr_cols = ['T5 Fails/Rd', '3P/Rd', 'DB/Rd', 'P5B/Rd', 'MG/Rd', '125B/Rd', 'SF/Rd']
    for col in pr_cols:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2f}")

    # Scores: 1 decimal place
    if 'Avg Score' in formatted_df.columns:
        formatted_df['Avg Score'] = formatted_df['Avg Score'].apply(lambda x: f"{x:.1f}")

    # Integers
    if 'BT' in formatted_df.columns:
        formatted_df['BT'] = formatted_df['BT'].astype(int)
    if 'Rounds' in formatted_df.columns:
        formatted_df['Rounds'] = formatted_df['Rounds'].astype(int)

    return formatted_df
