# ============================================================
# GOLF ANALYTICS DASHBOARD — SLIM CONTROLLER
# ============================================================
# All UI components, formatting, and theming live in ui/.
# All tab rendering functions live in tabs/.
# This file: data loading, sidebar filters, engine calls, tab dispatch.
# ============================================================

import streamlit as st
import pandas as pd

from data.load_data import load_data
from engines.hole_summary import build_hole_summary
from engines.driving import build_driving_results
from engines.approach import build_approach_results
from engines.short_game import build_short_game_results
from engines.putting import build_putting_results
from engines.tiger5 import build_tiger5_results
from engines.scoring_performance import build_scoring_performance
from engines.coachs_corner import build_coachs_corner
from engines.strokes_gained import BENCHMARK_FILES, apply_benchmark_sg

from ui.css import inject_css
from ui.components import sidebar_title, sidebar_label

from tabs.tiger5 import tiger5_tab
from tabs.scoring_performance import scoring_perf_tab
from tabs.strokes_gained import strokes_gained_tab
from tabs.driving import driving_tab
from tabs.approach import approach_tab
from tabs.short_game import short_game_tab
from tabs.putting import putting_tab
from tabs.coachs_corner import coachs_corner_tab

# ============================================================
# PAGE CONFIG & GLOBAL CSS
# ============================================================

st.set_page_config(page_title="Golf Analytics Dashboard", layout="wide")
inject_css()

# ============================================================
# DATA LOADING
# ============================================================

df = load_data()

# ============================================================
# SIDEBAR FILTERS (DYNAMIC/CASCADING)
# ============================================================

with st.sidebar:
    sidebar_title("Golf Analytics")

    sidebar_label("SG Benchmark")
    benchmark_choice = st.selectbox(
        "SG Benchmark",
        options=list(BENCHMARK_FILES.keys()),
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Initialize session state for filter selections if not exists
    if 'selected_players' not in st.session_state:
        st.session_state.selected_players = list(df['Player'].unique())
    if 'selected_courses' not in st.session_state:
        st.session_state.selected_courses = list(df['Course'].unique())
    if 'selected_tournaments' not in st.session_state:
        st.session_state.selected_tournaments = list(df['Tournament'].unique())
    if 'selected_date_range' not in st.session_state:
        min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
        st.session_state.selected_date_range = (min_date, max_date)

    # Dynamic filter options based on other selections
    # For each filter, calculate available options by applying ALL OTHER filters

    # Available players (filtered by course, tournament, date)
    temp_df = df[
        (df['Course'].isin(st.session_state.selected_courses))
        & (df['Tournament'].isin(st.session_state.selected_tournaments))
        & (df['Date'].dt.date >= st.session_state.selected_date_range[0])
        & (df['Date'].dt.date <= st.session_state.selected_date_range[1])
    ]
    available_players = sorted(temp_df['Player'].unique())

    # Available courses (filtered by player, tournament, date)
    temp_df = df[
        (df['Player'].isin(st.session_state.selected_players))
        & (df['Tournament'].isin(st.session_state.selected_tournaments))
        & (df['Date'].dt.date >= st.session_state.selected_date_range[0])
        & (df['Date'].dt.date <= st.session_state.selected_date_range[1])
    ]
    available_courses = sorted(temp_df['Course'].unique())

    # Available tournaments (filtered by player, course, date)
    temp_df = df[
        (df['Player'].isin(st.session_state.selected_players))
        & (df['Course'].isin(st.session_state.selected_courses))
        & (df['Date'].dt.date >= st.session_state.selected_date_range[0])
        & (df['Date'].dt.date <= st.session_state.selected_date_range[1])
    ]
    available_tournaments = sorted(temp_df['Tournament'].unique())

    # Available date range (filtered by player, course, tournament)
    temp_df = df[
        (df['Player'].isin(st.session_state.selected_players))
        & (df['Course'].isin(st.session_state.selected_courses))
        & (df['Tournament'].isin(st.session_state.selected_tournaments))
    ]
    if len(temp_df) > 0:
        min_date_available = temp_df['Date'].min().date()
        max_date_available = temp_df['Date'].max().date()
    else:
        min_date_available = df['Date'].min().date()
        max_date_available = df['Date'].max().date()

    # Keep only valid selections (intersection with available options)
    valid_players = [p for p in st.session_state.selected_players if p in available_players]
    valid_courses = [c for c in st.session_state.selected_courses if c in available_courses]
    valid_tournaments = [t for t in st.session_state.selected_tournaments if t in available_tournaments]

    # If no valid selections remain, default to all available
    if not valid_players and available_players:
        valid_players = available_players
    if not valid_courses and available_courses:
        valid_courses = available_courses
    if not valid_tournaments and available_tournaments:
        valid_tournaments = available_tournaments

    # Render filters
    sidebar_label("Player")
    players = st.multiselect(
        "Player",
        options=available_players,
        default=valid_players,
        label_visibility="collapsed",
        key="player_select",
    )

    sidebar_label("Course")
    courses = st.multiselect(
        "Course",
        options=available_courses,
        default=valid_courses,
        label_visibility="collapsed",
        key="course_select",
    )

    sidebar_label("Tournament")
    tournaments = st.multiselect(
        "Tournament",
        options=available_tournaments,
        default=valid_tournaments,
        label_visibility="collapsed",
        key="tournament_select",
    )

    sidebar_label("Date Range")

    # Clamp current date range to available bounds
    current_start, current_end = st.session_state.selected_date_range
    clamped_start = max(min(current_start, max_date_available), min_date_available)
    clamped_end = max(min(current_end, max_date_available), min_date_available)

    date_range = st.date_input(
        "Date Range",
        value=(clamped_start, clamped_end),
        min_value=min_date_available,
        max_value=max_date_available,
        label_visibility="collapsed",
        key="date_range_select",
    )

    # Update session state with current selections
    st.session_state.selected_players = players if players else available_players
    st.session_state.selected_courses = courses if courses else available_courses
    st.session_state.selected_tournaments = tournaments if tournaments else available_tournaments
    if isinstance(date_range, tuple) and len(date_range) == 2:
        st.session_state.selected_date_range = date_range
    elif hasattr(date_range, '__iter__') and len(list(date_range)) >= 2:
        dr_list = list(date_range)
        st.session_state.selected_date_range = (dr_list[0], dr_list[1])

# ============================================================
# APPLY FILTERS
# ============================================================

# Ensure we have valid filter values (use all if empty)
final_players = players if players else list(df['Player'].unique())
final_courses = courses if courses else list(df['Course'].unique())
final_tournaments = tournaments if tournaments else list(df['Tournament'].unique())

filtered_df = df[
    (df['Player'].isin(final_players))
    & (df['Course'].isin(final_courses))
    & (df['Tournament'].isin(final_tournaments))
    & (df['Date'].dt.date >= date_range[0])
    & (df['Date'].dt.date <= date_range[1])
].copy()

# ============================================================
# RECALCULATE SG FROM BENCHMARK
# ============================================================

filtered_df = apply_benchmark_sg(filtered_df, benchmark_choice)

num_rounds = filtered_df['Round ID'].nunique()

# ============================================================
# HOLE SUMMARY
# ============================================================

hole_summary = build_hole_summary(filtered_df)

# ============================================================
# ENGINE CALLS
# ============================================================

driving_results = build_driving_results(filtered_df, num_rounds, hole_summary)
approach_results = build_approach_results(filtered_df, num_rounds)
short_game_results = build_short_game_results(filtered_df, num_rounds)
putting_results = build_putting_results(filtered_df, num_rounds)

tiger5_results, total_tiger5_fails, grit_score = build_tiger5_results(
    filtered_df, hole_summary
)

scoring_perf_results = build_scoring_performance(filtered_df, hole_summary)

coachs_corner_results = build_coachs_corner(
    filtered_df,
    hole_summary,
    driving_results,
    approach_results,
    short_game_results,
    putting_results,
    tiger5_results,
    scoring_perf_results,
    grit_score,
    num_rounds,
)

# ============================================================
# TABS
# ============================================================

tab_tiger5, tab_scoring_perf, tab_sg, tab_driving, tab_approach, tab_short_game, \
    tab_putting, tab_coach = st.tabs(
        ["Tiger 5", "Scoring Performance", "Strokes Gained", "Driving", "Approach",
         "Short Game", "Putting", "Coach's Corner"]
    )

with tab_tiger5:
    tiger5_tab(filtered_df, hole_summary, tiger5_results, total_tiger5_fails)

with tab_scoring_perf:
    scoring_perf_tab(filtered_df, hole_summary, scoring_perf_results)

with tab_sg:
    strokes_gained_tab(
        filtered_df, hole_summary, num_rounds,
        driving_results, approach_results, short_game_results,
        putting_results, tiger5_results,
    )

with tab_driving:
    driving_tab(driving_results, num_rounds, hole_summary)

with tab_approach:
    approach_tab(approach_results, num_rounds)

with tab_short_game:
    short_game_tab(short_game_results, num_rounds)

with tab_putting:
    putting_tab(putting_results, num_rounds)

with tab_coach:
    coachs_corner_tab(coachs_corner_results)
