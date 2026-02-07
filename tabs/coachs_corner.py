# ============================================================
# TAB: COACH'S CORNER
# ============================================================

import streamlit as st

from ui.theme import CHARCOAL, SLATE, FONT_BODY, FONT_HEADING
from ui.components import section_header, premium_stat_card
from ui.formatters import format_sg, format_pct


def coachs_corner_tab(cc):

    section_header("Coach's Corner")

    # ================================================================
    # COACH SUMMARY
    # ================================================================
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.85rem;'
        f'font-weight:600;color:{SLATE};text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:0.5rem;">Coach Summary</p>',
        unsafe_allow_html=True,
    )

    summary = cc["coach_summary"]
    st.markdown(summary)

    st.markdown("---")

    # ================================================================
    # 1. STRENGTHS & WEAKNESSES
    # ================================================================
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.85rem;'
        f'font-weight:600;color:{SLATE};text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:0.5rem;">'
        f'Strengths & Weaknesses</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Strengths")
        for cat, sg_val in cc["strengths"]:
            st.markdown(f"- **{cat}**: {format_sg(sg_val)} SG")

    with col2:
        st.markdown("### Weaknesses")
        for cat, sg_val in cc["weaknesses"]:
            st.markdown(f"- **{cat}**: {format_sg(sg_val)} SG")

    st.markdown("---")

    # ================================================================
    # 2. RED FLAGS
    # ================================================================
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.85rem;'
        f'font-weight:600;color:{SLATE};text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:0.5rem;">Red Flags</p>',
        unsafe_allow_html=True,
    )

    # Approach
    st.markdown("### Approach (GIR < 50%)")
    gir_flags = cc["gir_flags"]
    if gir_flags:
        for gf in gir_flags:
            st.markdown(
                f"- **{gf['bucket']}**: {format_pct(gf['gir_pct'])} GIR"
            )
    else:
        st.markdown("*No GIR red flags.*")

    # Short Game
    st.markdown("### Short Game (Inside 8 ft)")
    sgf = cc["short_game_flags"]
    st.markdown(
        f"- **Fairway/Rough**: {format_pct(sgf['inside8_fr_pct'])} inside 8 ft"
    )
    st.markdown(
        f"- **Sand**: {format_pct(sgf['inside8_sand_pct'])} inside 8 ft"
    )

    # Putting
    st.markdown("### Putting")
    pf = cc["putting_flags"]
    st.markdown(f"- **Make % (4\u20135 ft)**: {format_pct(pf['make_45_pct'])}")
    st.markdown(f"- **SG (5\u201310 ft)**: {format_sg(pf['sg_510'])}")
    st.markdown(
        f"- **Lag Miss % (>5 ft)**: {format_pct(pf['lag_miss_pct'])}"
    )
    st.markdown(
        f"- **3-Putts Inside 20 ft**: {pf['three_putts_inside_20']}"
    )

    st.markdown("---")

    # ================================================================
    # 3. DECISION MAKING
    # ================================================================
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.85rem;'
        f'font-weight:600;color:{SLATE};text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:0.5rem;">Decision Making</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### Green / Yellow / Red SG")
    for gy in cc["green_yellow_red"]:
        st.markdown(
            f"- **{gy['light']} Light**: {format_sg(gy['total_sg'])} SG"
        )

    st.markdown("### Bogey Avoidance")
    ba = cc["bogey_avoidance"]
    st.markdown(
        f"- **Overall**: {format_pct(ba['Overall']['bogey_rate'])} bogey rate"
    )
    st.markdown(f"- **Par 3**: {format_pct(ba['Par3']['bogey_rate'])}")
    st.markdown(f"- **Par 4**: {format_pct(ba['Par4']['bogey_rate'])}")
    st.markdown(f"- **Par 5**: {format_pct(ba['Par5']['bogey_rate'])}")

    st.markdown("### Birdie Opportunities")
    bo = cc["birdie_opportunities"]
    st.markdown(f"- **Opportunities**: {bo['opportunities']}")
    st.markdown(f"- **Conversions**: {bo['conversions']}")
    st.markdown(
        f"- **Conversion %**: {format_pct(bo['conversion_pct'])}"
    )

    st.markdown("---")

    # ================================================================
    # 4. ROUND FLOW
    # ================================================================
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.85rem;'
        f'font-weight:600;color:{SLATE};text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:0.5rem;">Round Flow</p>',
        unsafe_allow_html=True,
    )

    fm = cc["flow_metrics"]

    colA, colB, colC, colD = st.columns(4)

    with colA:
        premium_stat_card("Bounce Back %",
                          format_pct(fm['bounce_back_pct']))
    with colB:
        premium_stat_card("Drop Off %",
                          format_pct(fm['drop_off_pct']))
    with colC:
        premium_stat_card("Gas Pedal %",
                          format_pct(fm['gas_pedal_pct']))
    with colD:
        premium_stat_card("Bogey Trains",
                          str(fm['bogey_train_count']))

    if fm["bogey_train_count"] > 0:
        st.markdown(
            f"- **Longest Train**: {fm['longest_bogey_train']} holes"
        )
        st.markdown(f"- **Train Lengths**: {fm['bogey_trains']}")

    st.markdown("---")

    # ================================================================
    # 5. PRACTICE PRIORITIES
    # ================================================================
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.85rem;'
        f'font-weight:600;color:{SLATE};text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:0.5rem;">'
        f'Practice Priorities</p>',
        unsafe_allow_html=True,
    )

    for p in cc["practice_priorities"]:
        st.markdown(f"- {p}")
