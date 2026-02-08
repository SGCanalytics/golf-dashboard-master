# ============================================================
# TAB: COACH'S CORNER — COMPLETE OVERHAUL
# ============================================================

import streamlit as st
import pandas as pd

from ui.theme import (
    CHARCOAL, SLATE, FONT_BODY, FONT_HEADING,
    POSITIVE, NEGATIVE, NEUTRAL, ACCENT_PRIMARY, WARNING,
    WHITE, BORDER_LIGHT, CARD_RADIUS, CARD_PADDING
)
from ui.formatters import format_sg, format_pct


# ============================================================
# UI COMPONENT HELPERS
# ============================================================


def section_header(title):
    """Premium section title with accent underline."""
    st.markdown(
        f'<p style="font-family:{FONT_HEADING};font-size:1.5rem;font-weight:600;'
        f'color:{CHARCOAL};margin:2rem 0 1.25rem 0;padding-bottom:0.6rem;'
        f'border-bottom:2px solid {ACCENT_PRIMARY};">{title}</p>',
        unsafe_allow_html=True,
    )


def subheader(title):
    """Subheader without accent line."""
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.85rem;'
        f'font-weight:600;color:{SLATE};text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:0.5rem;">{title}</p>',
        unsafe_allow_html=True,
    )


def premium_stat_card(label, value, subtitle="", sentiment="neutral"):
    """
    Light-background stat card with subtle shadow.
    """
    value_color = {
        "positive": POSITIVE,
        "negative": NEGATIVE,
        "neutral": CHARCOAL,
    }.get(sentiment, CHARCOAL)

    st.markdown(f'''
        <div style="background:{WHITE};border-radius:{CARD_RADIUS};
             padding:{CARD_PADDING};text-align:center;
             box-shadow:0 1px 4px rgba(0,0,0,0.04);
             border:1px solid {BORDER_LIGHT};margin-bottom:1rem;">
            <div style="font-family:{FONT_BODY};font-size:0.65rem;font-weight:600;
                 color:{SLATE};text-transform:uppercase;letter-spacing:0.08em;
                 margin-bottom:0.5rem;">{label}</div>
            <div style="font-family:{FONT_HEADING};font-size:2rem;font-weight:700;
                 color:{value_color};line-height:1;">{value}</div>
            <div style="font-family:{FONT_BODY};font-size:0.65rem;color:{SLATE};
                 margin-top:0.3rem;">{subtitle}</div>
        </div>
    ''', unsafe_allow_html=True)


def dynamic_narrative_card(item, is_positive=True):
    """Render a dynamic narrative card for strengths/weaknesses."""
    border_color = POSITIVE if is_positive else NEGATIVE
    
    st.markdown(f'''
        <div style="background:{WHITE};border-radius:{CARD_RADIUS};
             padding:{CARD_PADDING};margin-bottom:1rem;
             border-left:4px solid {border_color};
             box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <div style="font-family:{FONT_BODY};font-size:0.6rem;
                 color:{SLATE};text-transform:uppercase;
                 letter-spacing:0.08em;">{item['type']}</div>
            <div style="font-family:{FONT_HEADING};font-size:1rem;font-weight:600;
                 color:{CHARCOAL};margin:0.5rem 0;">{item['title']}</div>
            <div style="font-family:{FONT_BODY};font-size:0.85rem;
                 color:{ACCENT_PRIMARY};margin-bottom:0.5rem;
                 font-weight:500;">{item['detail']}</div>
            <div style="font-family:{FONT_BODY};font-size:0.75rem;
                 color:{SLATE};font-style:italic;
                 line-height:1.4;">{item['narrative']}</div>
        </div>
    ''', unsafe_allow_html=True)


def driver_card(driver):
    """Render a performance driver card."""
    priority_colors = {
        "HIGH": "#E63946",
        "MEDIUM": "#F4A261", 
        "LOW": "#2A9D8F"
    }
    priority_color = priority_colors.get(driver.get('priority', 'MEDIUM'), ACCENT_PRIMARY)
    
    impact_width = min(driver.get('impact_score', 1) * 33, 100)
    
    st.markdown(f'''
        <div style="background:{WHITE};border-radius:{CARD_RADIUS};
             padding:1.25rem;margin-bottom:1rem;
             border:1px solid {BORDER_LIGHT};
             box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <div style="display:flex;justify-content:space-between;align-items:center;
                 margin-bottom:0.75rem;">
                <div style="font-family:{FONT_BODY};font-size:0.65rem;
                     color:{SLATE};text-transform:uppercase;
                     letter-spacing:0.08em;">#{driver.get('rank', '')} DRIVER</div>
                <div style="background:{priority_color};color:white;
                     padding:0.2rem 0.6rem;border-radius:4px;
                     font-family:{FONT_BODY};font-size:0.6rem;font-weight:600;
                     text-transform:uppercase;">{driver.get('priority', 'MEDIUM')}</div>
            </div>
            <div style="font-family:{FONT_HEADING};font-size:1.1rem;font-weight:600;
                 color:{CHARCOAL};margin-bottom:0.5rem;">{driver['factor']}</div>
            <div style="font-family:{FONT_BODY};font-size:0.85rem;
                 color:{ACCENT_PRIMARY};margin-bottom:0.75rem;
                 font-weight:500;">{driver['detail']}</div>
            <div style="background:#F8F9FA;padding:0.75rem;border-radius:6px;
                 margin-bottom:0.75rem;">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;
                     color:{SLATE};text-transform:uppercase;
                     letter-spacing:0.08em;margin-bottom:0.3rem;">Recommendation</div>
                <div style="font-family:{FONT_BODY};font-size:0.8rem;
                     color:{CHARCOAL};line-height:1.4;">{driver['recommendation']}</div>
            </div>
            <div style="font-family:{FONT_BODY};font-size:0.6rem;
                 color:{SLATE};text-transform:uppercase;
                 letter-spacing:0.05em;">Impact Score</div>
            <div style="background:#E9ECEF;border-radius:4px;height:6px;
                 margin-top:0.3rem;overflow:hidden;">
                <div style="background:{ACCENT_PRIMARY};width:{impact_width}%;
                     height:100%;border-radius:4px;"></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)


def definition_expander(title, definition):
    """Collapsible definition section."""
    with st.expander(f"📖 {title}", expanded=False):
        st.markdown(
            f'<p style="font-family:{FONT_BODY};font-size:0.8rem;'
            f'color:{SLATE};line-height:1.6;">{definition}</p>',
            unsafe_allow_html=True
        )


# ============================================================
# SECTION 1: TIGER 5 ROOT CAUSES NARRATIVE
# ============================================================


def render_tiger5_narrative(narrative):
    """Render Section 1: Dynamic Tiger 5 Root Causes narrative."""
    section_header("Tiger 5 Root Causes")
    
    if not narrative:
        st.info("No Tiger 5 data available for analysis.")
        return
    
    for item in narrative:
        is_positive = "Challenge" not in item.get('type', '') and "Issue" not in item.get('type', '') and "Weakness" not in item.get('type', '')
        dynamic_narrative_card(item, is_positive=is_positive)
    
    st.markdown("---")


# ============================================================
# SECTION 2: MENTAL CHARACTERISTICS & ROUND FLOW
# ============================================================


def render_mental_metrics(mental_metrics):
    """Render Section 2: Mental Characteristics with stat cards and definitions."""
    section_header("Mental Characteristics & Round Flow")
    
    # === ROW 1: Flow Metrics (4 cards) ===
    subheader("Round Flow")
    
    col1, col2, col3, col4 = st.columns(4)
    
    bounce = mental_metrics.get('bounce_back', {})
    drop = mental_metrics.get('drop_off', {})
    gas = mental_metrics.get('gas_pedal', {})
    bogey = mental_metrics.get('bogey_train_rate', {})
    
    with col1:
        sentiment = "positive" if bounce.get('rate', 0) >= 20 else "negative" if bounce.get('rate', 0) < 10 else "neutral"
        premium_stat_card(
            "Bounce Back %",
            format_pct(bounce.get('rate', 0)),
            f"{bounce.get('successes', 0)}/{bounce.get('opportunities', 0)}",
            sentiment
        )
    
    with col2:
        sentiment = "negative" if drop.get('rate', 0) > 20 else "positive" if drop.get('rate', 0) < 10 else "neutral"
        premium_stat_card(
            "Drop Off %",
            format_pct(drop.get('rate', 0)),
            f"{drop.get('events', 0)}/{drop.get('opportunities', 0)}",
            sentiment
        )
    
    with col3:
        sentiment = "positive" if gas.get('rate', 0) >= 25 else "neutral"
        premium_stat_card(
            "Gas Pedal %",
            format_pct(gas.get('rate', 0)),
            f"{gas.get('successes', 0)}/{gas.get('opportunities', 0)}",
            sentiment
        )
    
    with col4:
        sentiment = "negative" if bogey.get('btr', 0) > 40 else "positive" if bogey.get('btr', 0) < 20 else "neutral"
        premium_stat_card(
            "Bogey Train Rate %",
            format_pct(bogey.get('btr', 0)),
            f"Longest: {bogey.get('longest', 0)} holes",
            sentiment
        )
    
    # === Definitions for Flow Metrics ===
    definition_expander(
        "Round Flow Metrics Definitions",
        """
        **Bounce Back %**: Percentage of bogey-or-worse holes followed by birdie-or-better on the next hole. 
        Measures resilience after mistakes.
        
        **Drop Off %**: Percentage of bogey-or-worse holes followed by another bogey-or-worse. 
        Lower is better — indicates avoiding streak mistakes.
        
        **Gas Pedal %**: Percentage of birdie-or-better holes followed by another birdie-or-better. 
        Measures positive momentum and capitalizing on good play.
        
        **Bogey Train Rate %**: Percentage of bogey-or-worse holes that are part of consecutive streaks (2+ holes). 
        Lower is better — indicates breaking streaks early.
        """
    )
    
    st.markdown("---")
    
    # === ROW 2: Pressure & Early Round (3 cards) ===
    subheader("Pressure & Early Round Performance")
    
    colA, colB, colC = st.columns(3)
    
    finish = mental_metrics.get('pressure_finish', {})
    early = mental_metrics.get('early_round', {})
    mpi = mental_metrics.get('mistake_penalty', {})
    
    with colA:
        # Score vs par on 16-18
        score_diff = finish.get('score_vs_baseline', 0)
        sentiment = "negative" if score_diff > 0.2 else "positive" if score_diff < -0.2 else "neutral"
        sg_diff = finish.get('sg_vs_baseline', 0)
        premium_stat_card(
            "Pressure Finish (16-18)",
            f"{finish.get('finish_score_to_par', 0):+d}",
            f"SG: {sg_diff:+.2f} vs baseline",
            sentiment
        )
    
    with colB:
        # Score vs par on 1-3
        score_diff = early.get('score_vs_baseline', 0)
        sentiment = "negative" if score_diff > 0.2 else "positive" if score_diff < -0.2 else "neutral"
        sg_diff = early.get('sg_vs_baseline', 0)
        premium_stat_card(
            "Early Round (1-3)",
            f"{early.get('early_score_to_par', 0):+d}",
            f"SG: {sg_diff:+.2f} vs baseline",
            sentiment
        )
    
    with colC:
        # Mistake Penalty Index
        penalty = mpi.get('penalty_index', 0)
        sentiment = "negative" if penalty > 0.3 else "positive" if penalty < 0 else "neutral"
        premium_stat_card(
            "Mistake Penalty Index",
            f"{penalty:+.2f}",
            f"On T5 fails: {mpi.get('fail_per_hole', 0):+.2f} vs clean: {mpi.get('clean_per_hole', 0):+.2f}",
            sentiment
        )
    
    # === Definitions for Pressure Metrics ===
    definition_expander(
        "Pressure & Early Round Definitions",
        """
        **Pressure Finish (16-18)**: Score relative to par and SG per hole on the closing three holes, 
        compared to the player's overall baseline. Shows how performance changes under pressure.
        
        **Early Round Composure (1-3)**: Score relative to par and SG per hole on the first three holes, 
        compared to baseline. Indicates mental readiness at round start.
        
        **Mistake Penalty Index**: Additional strokes per hole when making a Tiger 5 mistake vs clean holes. 
        Measures how costly mental mistakes become. Lower values indicate better damage control.
        """
    )
    
    st.markdown("---")


# ============================================================
# SECTION 3: GAME OVERVIEW — DYNAMIC STRENGTHS/WEAKNESSES
# ============================================================


def render_game_overview(game_overview):
    """Render Section 3: Dynamic two-column Game Overview."""
    section_header("Game Overview")
    
    strengths = game_overview.get('strengths', [])
    weaknesses = game_overview.get('weaknesses', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f'<p style="font-family:{FONT_HEADING};font-size:1.2rem;font-weight:600;'
            f'color:{POSITIVE};margin-bottom:1rem;">'
            f'✓ Player Strengths</p>',
            unsafe_allow_html=True
        )
        
        if not strengths:
            st.info("No significant strengths identified.")
        else:
            for item in strengths[:4]:
                dynamic_narrative_card(item, is_positive=True)
    
    with col2:
        st.markdown(
            f'<p style="font-family:{FONT_HEADING};font-size:1.2rem;font-weight:600;'
            f'color:{NEGATIVE};margin-bottom:1rem;">'
            f'✗ Player Weaknesses</p>',
            unsafe_allow_html=True
        )
        
        if not weaknesses:
            st.info("No significant weaknesses identified.")
        else:
            for item in weaknesses[:4]:
                dynamic_narrative_card(item, is_positive=False)
    
    st.markdown("---")


# ============================================================
# SECTION 4: "IMPRESS ME" — PERFORMANCE DRIVERS
# ============================================================


def render_performance_drivers(drivers):
    """Render Section 4: 'Impress Me' Performance Drivers."""
    section_header("Performance Drivers")
    
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.85rem;'
        f'color:{SLATE};margin-bottom:1.5rem;">'
        f'The key factors driving your final score, ranked by impact.</p>',
        unsafe_allow_html=True
    )
    
    if not drivers:
        st.info("Not enough data to identify performance drivers.")
        return
    
    for driver in drivers:
        driver_card(driver)
    
    st.markdown("---")


# ============================================================
# SECTION 5: SHOT CHARACTERISTICS (COLLAPSIBLE)
# ============================================================


def render_shot_characteristics(shot_chars):
    """Render Section 5: Collapsible shot characteristics breakdown."""
    section_header("Shot Characteristics")
    
    if not shot_chars:
        st.info("No shot data available.")
        return
    
    # Recovery shots
    with st.expander("🏌️ Recovery Shots", expanded=False):
        recovery = shot_chars.get('recovery', {})
        data = recovery.get('data')
        stats = recovery.get('stats')
        
        if data is not None and not data.empty:
            if stats:
                st.markdown(
                    f"**{stats.get('count', 0)} shots** | "
                    f"SG: {format_sg(stats.get('sg_total', 0))} | "
                    f"Avg: {format_sg(stats.get('sg_avg', 0))}"
                )
            st.dataframe(
                data.style.format({
                    'Starting Distance': '{:.0f}',
                    'Ending Distance': '{:.1f}',
                    'Strokes Gained': format_sg
                }),
                use_container_width=True
            )
        else:
            st.info("No recovery shots in the dataset.")
    
    # Penalty shots
    with st.expander("⚠️ Penalty Shots", expanded=False):
        penalty = shot_chars.get('penalty', {})
        data = penalty.get('data')
        stats = penalty.get('stats')
        
        if data is not None and not data.empty:
            if stats:
                st.markdown(
                    f"**{stats.get('count', 0)} shots** | "
                    f"SG: {format_sg(stats.get('sg_total', 0))} | "
                    f"Avg: {format_sg(stats.get('sg_avg', 0))}"
                )
            st.dataframe(
                data.style.format({
                    'Starting Distance': '{:.0f}',
                    'Ending Distance': '{:.1f}',
                    'Strokes Gained': format_sg
                }),
                use_container_width=True
            )
        else:
            st.info("No penalty shots in the dataset.")
    
    # Other shots
    with st.expander("📊 Other Shots", expanded=False):
        other = shot_chars.get('other', {})
        data = other.get('data')
        stats = other.get('stats')
        
        if data is not None and not data.empty:
            if stats:
                st.markdown(
                    f"**{stats.get('count', 0)} shots** | "
                    f"SG: {format_sg(stats.get('sg_total', 0))} | "
                    f"Avg: {format_sg(stats.get('sg_avg', 0))}"
                )
            st.dataframe(
                data.style.format({
                    'Starting Distance': '{:.0f}',
                    'Ending Distance': '{:.1f}',
                    'Strokes Gained': format_sg
                }),
                use_container_width=True
            )
        else:
            st.info("No 'other' shots in the dataset.")


# ============================================================
# MAIN TAB RENDERER
# ============================================================


def coachs_corner_tab(cc):
    """
    Main entry point for Coach's Corner tab.
    Renders all 5 sections in order.
    """
    # Section 1: Tiger 5 Root Causes
    render_tiger5_narrative(cc.get('tiger5_narrative', []))
    
    # Section 2: Mental Characteristics & Round Flow
    render_mental_metrics(cc.get('mental_metrics', {}))
    
    # Section 3: Game Overview (Strengths/Weaknesses)
    render_game_overview(cc.get('game_overview', {}))
    
    # Section 4: Performance Drivers ("Impress Me")
    render_performance_drivers(cc.get('performance_drivers', []))
    
    # Section 5: Shot Characteristics
    render_shot_characteristics(cc.get('shot_characteristics', {}))
