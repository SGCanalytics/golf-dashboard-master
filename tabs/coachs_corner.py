# ============================================================
# TAB: COACH'S CORNER — PREMIUM UPGRADE
# ============================================================

import streamlit as st

from ui.theme import (
    CHARCOAL, CHARCOAL_LIGHT, SLATE, WHITE, WARM_GRAY,
    ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_MUTED, ACCENT_PALE,
    POSITIVE, NEGATIVE, WARNING, NEUTRAL,
    BORDER_LIGHT, FONT_BODY, FONT_HEADING,
    CARD_RADIUS, CARD_PADDING,
)
from ui.components import (
    section_header, premium_hero_card, premium_stat_card,
    sg_sentiment, pct_sentiment_above, pct_sentiment_below,
)
from ui.formatters import format_sg, format_pct


# ---- Local card helpers -----------------------------------------------

# Removed: _SEVERITY_COLORS - used by removed Performance Drivers section
# Removed: _LIGHT_COLORS - used by removed Green/Yellow/Red SG section
# Removed: _driver_card() function - Performance Drivers (Red Flags) section has been removed


def _path_category_card(entry, is_strength):
    """Render a PlayerPath category (strength or weakness) as a card block."""
    sg_val = entry["sg_total"]
    sg_pr = entry["sg_per_round"]
    color = POSITIVE if is_strength else NEGATIVE
    border = POSITIVE if is_strength else NEGATIVE

    st.markdown(f'''
        <div style="background:{WHITE};border-radius:{CARD_RADIUS};
             padding:1rem 1.25rem;margin-bottom:0.75rem;
             border:1px solid {BORDER_LIGHT};border-left:5px solid {border};
             box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="display:flex;justify-content:space-between;
                 align-items:baseline;margin-bottom:0.5rem;">
                <div style="font-family:{FONT_HEADING};font-size:1rem;
                     font-weight:700;color:{CHARCOAL};">
                    {entry["headline"]}</div>
                <div style="text-align:right;">
                    <span style="font-family:{FONT_HEADING};font-size:1.3rem;
                          font-weight:700;color:{color};">
                        {sg_val:+.2f}</span>
                    <span style="font-family:{FONT_BODY};font-size:0.6rem;
                          color:{SLATE};margin-left:0.25rem;">SG</span>
                    <div style="font-family:{FONT_BODY};font-size:0.6rem;
                         color:{SLATE};">{sg_pr:+.2f} per round</div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # Detail items as compact stat row
    if entry.get("detail_items"):
        cols = st.columns(min(len(entry["detail_items"]), 4))
        for i, item in enumerate(entry["detail_items"][:4]):
            with cols[i % len(cols)]:
                premium_stat_card(
                    item["label"],
                    item["value"],
                    sentiment=item.get("sentiment", "neutral"),
                )


# Removed: _deep_dive_card() function - Tiger 5 Root Cause Deep Dive section has been removed


# ============================================================
# MAIN TAB FUNCTION
# ============================================================

def coachs_corner_tab(cc):

    # ================================================================
    # SECTION 0: SG SUMMARY HERO CARDS
    # ================================================================
    sg = cc["sg_summary"]

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_sg = sum(sg.values())
        premium_hero_card(
            "SG Total", format_sg(total_sg),
            "all categories combined",
            sentiment=sg_sentiment(total_sg),
        )
    with col2:
        premium_hero_card(
            "SG Driving", format_sg(sg.get("Driving", 0)),
            sentiment=sg_sentiment(sg.get("Driving", 0)),
        )
    with col3:
        premium_hero_card(
            "SG Approach", format_sg(sg.get("Approach", 0)),
            sentiment=sg_sentiment(sg.get("Approach", 0)),
        )
    with col4:
        premium_hero_card(
            "SG Short Game", format_sg(sg.get("Short Game", 0)),
            sentiment=sg_sentiment(sg.get("Short Game", 0)),
        )
    with col5:
        premium_hero_card(
            "SG Putting", format_sg(sg.get("Putting", 0)),
            sentiment=sg_sentiment(sg.get("Putting", 0)),
        )

    # ================================================================
    # SECTION 1: COACH SUMMARY
    # ================================================================
    section_header("Coach Summary")

    grit = cc.get("grit_score", 0)
    summary = cc["coach_summary"]

    col_sum, col_grit = st.columns([3, 1])

    with col_sum:
        st.markdown(f'''
            <div style="background:{WHITE};border-radius:{CARD_RADIUS};
                 padding:1.25rem 1.5rem;
                 border:1px solid {BORDER_LIGHT};border-left:5px solid {ACCENT_PRIMARY};
                 box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:1rem;">
                <div style="font-family:{FONT_BODY};font-size:0.88rem;
                     color:{CHARCOAL};line-height:1.7;">
                    {summary}</div>
            </div>
        ''', unsafe_allow_html=True)

    with col_grit:
        grit_sent = "positive" if grit >= 80 else ("warning" if grit >= 60 else "negative")
        premium_hero_card("Grit Score", format_pct(grit), "Tiger 5 success rate",
                          sentiment=grit_sent)

    # ================================================================
    # SECTION 2: PERFORMANCE DRIVERS — REMOVED
    # ================================================================
    # This section (Red Flags) has been removed per user requirements

    # ================================================================
    # SECTION 3: PLAYERPATH — STRENGTHS & WEAKNESSES
    # ================================================================
    section_header("PlayerPath")

    path = cc.get("player_path", {"strengths": [], "weaknesses": []})

    col_str, col_wk = st.columns(2)

    with col_str:
        st.markdown(f'''
            <div style="font-family:{FONT_HEADING};font-size:1.1rem;
                 font-weight:700;color:{POSITIVE};margin-bottom:0.75rem;
                 padding-bottom:0.4rem;
                 border-bottom:2px solid {POSITIVE};">Strengths</div>
        ''', unsafe_allow_html=True)

        if path["strengths"]:
            for entry in path["strengths"]:
                _path_category_card(entry, is_strength=True)
        else:
            st.markdown(
                f'<p style="font-family:{FONT_BODY};font-size:0.8rem;'
                f'color:{SLATE};font-style:italic;">No categories with positive SG.</p>',
                unsafe_allow_html=True,
            )

    with col_wk:
        st.markdown(f'''
            <div style="font-family:{FONT_HEADING};font-size:1.1rem;
                 font-weight:700;color:{NEGATIVE};margin-bottom:0.75rem;
                 padding-bottom:0.4rem;
                 border-bottom:2px solid {NEGATIVE};">Weaknesses</div>
        ''', unsafe_allow_html=True)

        if path["weaknesses"]:
            for entry in path["weaknesses"]:
                _path_category_card(entry, is_strength=False)
        else:
            st.markdown(
                f'<p style="font-family:{FONT_BODY};font-size:0.8rem;'
                f'color:{SLATE};font-style:italic;">No categories with negative SG.</p>',
                unsafe_allow_html=True,
            )

    # ================================================================
    # SECTION 4: TIGER 5 ROOT CAUSE DEEP DIVE — REMOVED
    # ================================================================
    # This section has been removed per user requirements

    # ================================================================
    # SECTION 5: DECISION MAKING
    # ================================================================
    section_header("Decision Making")

    # Green / Yellow / Red SG — REMOVED
    # This subsection has been removed per user requirements

    # Bogey Avoidance
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.75rem;font-weight:600;'
        f'color:{SLATE};text-transform:uppercase;letter-spacing:0.06em;'
        f'margin:1rem 0 0.5rem 0;">Bogey Avoidance</p>',
        unsafe_allow_html=True,
    )
    ba = cc["bogey_avoidance"]
    ba_cols = st.columns(4)
    ba_keys = [("Overall", "Overall"), ("Par3", "Par 3"), ("Par4", "Par 4"), ("Par5", "Par 5")]
    for col, (key, label) in zip(ba_cols, ba_keys):
        rate = ba[key]["bogey_rate"]
        # Updated thresholds: ≤10% green, 10-30% yellow, ≥30% red
        s = "positive" if rate <= 10 else ("warning" if rate < 30 else "negative")
        with col:
            premium_stat_card(label, format_pct(rate), "bogey rate", sentiment=s)

    # Birdie Opportunities
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.75rem;font-weight:600;'
        f'color:{SLATE};text-transform:uppercase;letter-spacing:0.06em;'
        f'margin:1rem 0 0.5rem 0;">Birdie Opportunities</p>',
        unsafe_allow_html=True,
    )
    bo = cc["birdie_opportunities"]
    bo_cols = st.columns(3)
    with bo_cols[0]:
        premium_stat_card("Opportunities", str(bo["opportunities"]),
                          "Green in Regulation", sentiment="accent")
    with bo_cols[1]:
        premium_stat_card("Conversions", str(bo["conversions"]),
                          "birdie or better", sentiment="positive")
    with bo_cols[2]:
        s = "positive" if bo["conversion_pct"] >= 30 else "negative"
        premium_stat_card("Conversion %", format_pct(bo["conversion_pct"]),
                          sentiment=s)

    # ================================================================
    # SECTION 7: ROUND FLOW
    # ================================================================
    section_header("Round Flow")

    fm = cc["flow_metrics"]

    colA, colB, colC, colD = st.columns(4)

    with colA:
        s = pct_sentiment_above(fm["bounce_back_pct"], "pct_bounce_back")
        premium_stat_card("Bounce Back %",
                          format_pct(fm['bounce_back_pct']),
                          "birdie after bogey", sentiment=s)
    with colB:
        s = "positive" if fm["drop_off_pct"] <= 25 else "negative"
        premium_stat_card("Drop Off %",
                          format_pct(fm['drop_off_pct']),
                          "bogey after birdie", sentiment=s)
    with colC:
        s = "positive" if fm["gas_pedal_pct"] >= 20 else "neutral"
        premium_stat_card("Gas Pedal %",
                          format_pct(fm['gas_pedal_pct']),
                          "birdie after birdie", sentiment=s)
    with colD:
        s = "negative" if fm["bogey_train_count"] > 0 else "positive"
        premium_stat_card("Bogey Trains",
                          str(fm['bogey_train_count']),
                          sentiment=s)

    if fm["bogey_train_count"] > 0:
        bt_c1, bt_c2 = st.columns(2)
        with bt_c1:
            premium_stat_card("Longest Train",
                              f"{fm['longest_bogey_train']} holes",
                              sentiment="negative")
        with bt_c2:
            premium_stat_card("Train Lengths",
                              str(fm['bogey_trains']),
                              sentiment="negative")

    # ================================================================
    # SECTION 8: PRACTICE PRIORITIES
    # ================================================================
    section_header("Practice Priorities")

    priorities = cc["practice_priorities"]
    if priorities:
        for i, p in enumerate(priorities, 1):
            st.markdown(f'''
                <div style="background:{WHITE};border-radius:8px;
                     padding:0.75rem 1rem;margin-bottom:0.5rem;
                     border:1px solid {BORDER_LIGHT};
                     border-left:4px solid {ACCENT_PRIMARY};
                     box-shadow:0 1px 3px rgba(0,0,0,0.04);
                     display:flex;align-items:center;gap:0.75rem;">
                    <div style="font-family:{FONT_HEADING};font-size:1.1rem;
                         font-weight:700;color:{ACCENT_PRIMARY};min-width:24px;
                         text-align:center;">{i}</div>
                    <div style="font-family:{FONT_BODY};font-size:0.82rem;
                         color:{CHARCOAL};">{p}</div>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No practice priorities identified.")
