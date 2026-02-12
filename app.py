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
from engines.coachs_corner import build_coachs_corner
from engines.strokes_gained import BENCHMARK_FILES, apply_benchmark_sg

from ui.css import inject_css
from ui.components import sidebar_title, sidebar_label

from tabs.tiger5 import tiger5_tab
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
# SIDEBAR FILTERS
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
    sidebar_label("Player")

    players = st.multiselect(
        "Player",
        options=sorted(df['Player'].unique()),
        default=df['Player'].unique(),
        label_visibility="collapsed",
    )

    sidebar_label("Course")
    courses = st.multiselect(
        "Course",
        options=sorted(df['Course'].unique()),
        default=df['Course'].unique(),
        label_visibility="collapsed",
    )

    sidebar_label("Tournament")
    tournaments = st.multiselect(
        "Tournament",
        options=sorted(df['Tournament'].unique()),
        default=df['Tournament'].unique(),
        label_visibility="collapsed",
    )

    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()

    sidebar_label("Date Range")
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
    )

# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    (df['Player'].isin(players))
    & (df['Course'].isin(courses))
    & (df['Tournament'].isin(tournaments))
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

coachs_corner_results = build_coachs_corner(
    filtered_df,
    hole_summary,
    driving_results,
    approach_results,
    short_game_results,
    putting_results,
    tiger5_results,
    grit_score,
    num_rounds,
)

# ============================================================
# TABS
# ============================================================

tab_tiger5, tab_sg, tab_driving, tab_approach, tab_short_game, \
    tab_putting, tab_coach = st.tabs(
        ["Tiger 5", "Strokes Gained", "Driving", "Approach",
         "Short Game", "Putting", "Coach's Corner"]
    )

with tab_tiger5:
    tiger5_tab(filtered_df, hole_summary, tiger5_results, total_tiger5_fails)

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
