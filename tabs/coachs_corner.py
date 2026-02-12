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

_SEVERITY_COLORS = {
    "critical": NEGATIVE,
    "significant": WARNING,
    "moderate": ACCENT_MUTED,
}

_LIGHT_COLORS = {
    "Green": POSITIVE,
    "Yellow": WARNING,
    "Red": NEGATIVE,
}


def _driver_card(rank, driver):
    """Render a single Performance Driver as a premium numbered card."""
    sev = driver.get("severity", "moderate")
    border_color = _SEVERITY_COLORS.get(sev, ACCENT_MUTED)
    sev_label = sev.capitalize()
    sg_pr = driver["sg_per_round"]
    sg_color = NEGATIVE if sg_pr < 0 else POSITIVE

    st.markdown(f'''
        <div style="background:{WHITE};border-radius:{CARD_RADIUS};
             padding:1rem 1.25rem;margin-bottom:0.75rem;
             border:1px solid {BORDER_LIGHT};border-left:5px solid {border_color};
             box-shadow:0 2px 8px rgba(0,0,0,0.05);
             display:flex;align-items:center;gap:1rem;">
            <div style="min-width:40px;text-align:center;">
                <div style="font-family:{FONT_HEADING};font-size:1.8rem;
                     font-weight:700;color:{border_color};line-height:1;">
                    {rank}</div>
            </div>
            <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;
                     align-items:baseline;margin-bottom:0.3rem;">
                    <div>
                        <span style="font-family:{FONT_BODY};font-size:0.7rem;
                              font-weight:600;color:{SLATE};text-transform:uppercase;
                              letter-spacing:0.06em;">{driver["category"]}</span>
                        <span style="font-family:{FONT_BODY};font-size:0.6rem;
                              color:{border_color};margin-left:0.5rem;
                              text-transform:uppercase;letter-spacing:0.05em;">
                            {sev_label}</span>
                    </div>
                    <div style="font-family:{FONT_HEADING};font-size:1.4rem;
                         font-weight:700;color:{sg_color};">
                        {sg_pr:+.2f}
                        <span style="font-size:0.65rem;color:{SLATE};
                              font-weight:400;">SG/rd</span>
                    </div>
                </div>
                <div style="font-family:{FONT_HEADING};font-size:0.95rem;
                     font-weight:600;color:{CHARCOAL};margin-bottom:0.2rem;">
                    {driver["label"]}</div>
                <div style="font-family:{FONT_BODY};font-size:0.75rem;
                     color:{CHARCOAL_LIGHT};">{driver["detail"]}</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)


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


def _deep_dive_card(dive):
    """Render a Tiger 5 deep-dive diagnosis card."""
    st.markdown(f'''
        <div style="background:{WHITE};border-radius:{CARD_RADIUS};
             padding:1rem 1.25rem;margin-bottom:0.75rem;
             border:1px solid {BORDER_LIGHT};border-left:5px solid {NEGATIVE};
             box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="display:flex;justify-content:space-between;
                 align-items:baseline;margin-bottom:0.4rem;">
                <div style="font-family:{FONT_HEADING};font-size:1rem;
                     font-weight:700;color:{CHARCOAL};">
                    {dive["category"]}</div>
                <div style="font-family:{FONT_BODY};font-size:0.7rem;
                     color:{NEGATIVE};font-weight:600;">
                    {dive["fail_count"]} fails ({dive["pct_of_fails"]:.0f}%)</div>
            </div>
            <div style="display:flex;align-items:baseline;gap:0.5rem;
                 margin-bottom:0.5rem;">
                <span style="font-family:{FONT_BODY};font-size:0.65rem;
                      font-weight:600;color:{SLATE};text-transform:uppercase;
                      letter-spacing:0.06em;">{dive["key_metric_label"]}</span>
                <span style="font-family:{FONT_HEADING};font-size:1.2rem;
                      font-weight:700;color:{NEGATIVE};">
                    {dive["key_metric_value"]}</span>
            </div>
            <div style="font-family:{FONT_BODY};font-size:0.8rem;
                 color:{CHARCOAL_LIGHT};line-height:1.5;">
                {dive["diagnosis"]}</div>
        </div>
    ''', unsafe_allow_html=True)

    # Supporting metrics as small cards
    sm = dive.get("supporting_metrics", [])
    if sm:
        cols = st.columns(len(sm))
        for col, m in zip(cols, sm):
            with col:
                premium_stat_card(m["label"], m["value"])


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
    # SECTION 2: PERFORMANCE DRIVERS
    # ================================================================
    section_header("Performance Drivers")

    drivers = cc.get("performance_drivers", [])

    if drivers:
        st.markdown(
            f'<p style="font-family:{FONT_BODY};font-size:0.8rem;color:{SLATE};'
            f'margin-bottom:1rem;">Top factors costing strokes per round, '
            f'ranked by impact.</p>',
            unsafe_allow_html=True,
        )
        for i, drv in enumerate(drivers, 1):
            _driver_card(i, drv)
    else:
        st.info("No negative performance drivers found — all areas performing at or above benchmark.")

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
    # SECTION 4: TIGER 5 ROOT CAUSE DEEP DIVE
    # ================================================================
    section_header("Tiger 5: Root Cause Deep Dive")

    # Shot type count cards
    rc_counts = cc.get("tiger5_root_cause_counts", {})
    total_rc = sum(rc_counts.values())
    rc_types = ['Driving', 'Approach', 'Short Game', 'Short Putts', 'Lag Putts']

    rc_cols = st.columns(5)
    for col, stype in zip(rc_cols, rc_types):
        count = rc_counts.get(stype, 0)
        pct = (count / total_rc * 100) if total_rc > 0 else 0
        with col:
            premium_stat_card(
                stype, str(count),
                f"{pct:.0f}% of fails",
                sentiment="negative" if count > 0 else "neutral",
            )

    # Deep dive diagnosis cards
    dives = cc.get("tiger5_deep_dive", [])
    if dives:
        st.markdown(
            f'<p style="font-family:{FONT_BODY};font-size:0.8rem;color:{SLATE};'
            f'margin:1rem 0 0.75rem 0;">Detailed diagnosis for each root cause '
            f'category.</p>',
            unsafe_allow_html=True,
        )
        for dive in dives:
            _deep_dive_card(dive)
    else:
        st.info("No Tiger 5 failures — no root cause analysis needed.")

    # ================================================================
    # SECTION 5: DECISION MAKING
    # ================================================================
    section_header("Decision Making")

    # Green / Yellow / Red SG
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.75rem;font-weight:600;'
        f'color:{SLATE};text-transform:uppercase;letter-spacing:0.06em;'
        f'margin-bottom:0.5rem;">Green / Yellow / Red SG</p>',
        unsafe_allow_html=True,
    )
    gyr_cols = st.columns(3)
    for col, gy in zip(gyr_cols, cc["green_yellow_red"]):
        light = gy["light"]
        color = _LIGHT_COLORS.get(light, ACCENT_PRIMARY)
        with col:
            st.markdown(f'''
                <div style="background:{WHITE};border-radius:{CARD_RADIUS};
                     padding:{CARD_PADDING};text-align:center;
                     border:1px solid {BORDER_LIGHT};border-top:4px solid {color};
                     box-shadow:0 1px 4px rgba(0,0,0,0.04);margin-bottom:1rem;">
                    <div style="font-family:{FONT_BODY};font-size:0.65rem;
                         font-weight:600;color:{color};text-transform:uppercase;
                         letter-spacing:0.08em;margin-bottom:0.5rem;">
                        {light} Light</div>
                    <div style="font-family:{FONT_HEADING};font-size:1.8rem;
                         font-weight:700;color:{color};line-height:1;">
                        {format_sg(gy["total_sg"])}</div>
                    <div style="font-family:{FONT_BODY};font-size:0.6rem;
                         color:{SLATE};margin-top:0.25rem;">Total SG</div>
                </div>
            ''', unsafe_allow_html=True)

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
        s = "positive" if rate <= 30 else ("negative" if rate >= 50 else "neutral")
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
                          "1st putt \u226420 ft", sentiment="accent")
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
