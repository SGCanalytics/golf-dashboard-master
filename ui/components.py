# ============================================================
# SHARED UI COMPONENTS
# ============================================================
# Reusable, themeable building blocks for every tab.
# Light, airy aesthetic — white cards with subtle borders.
# ============================================================

import streamlit as st
from ui.theme import (
    CHARCOAL, CHARCOAL_LIGHT, SLATE, WHITE, BORDER_LIGHT,
    ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_MUTED, ACCENT_PALE,
    POSITIVE, NEGATIVE, NEUTRAL, WARNING,
    FONT_HEADING, FONT_BODY, CARD_RADIUS, CARD_PADDING,
    THRESHOLDS,
)


# ---- Section header ------------------------------------------------

def section_header(title):
    """Premium section title with accent underline."""
    st.markdown(
        f'<p style="font-family:{FONT_HEADING};font-size:1.5rem;font-weight:600;'
        f'color:{CHARCOAL};margin:2rem 0 1.25rem 0;padding-bottom:0.6rem;'
        f'border-bottom:2px solid {ACCENT_PRIMARY};">{title}</p>',
        unsafe_allow_html=True,
    )


# ---- Premium Hero Card ---------------------------------------------

_SENTIMENT_COLORS = {
    "positive": POSITIVE,
    "negative": NEGATIVE,
    "neutral":  ACCENT_PRIMARY,
    "accent":   ACCENT_PRIMARY,
    "warning":  WARNING,
}


def premium_hero_card(label, value, unit="", sentiment="neutral"):
    """
    Light-background hero metric card with coloured left border.

    White card with a 3px left accent border for sentiment.
    Clean, muted, premium feel — no dark backgrounds.

    sentiment: "positive" | "negative" | "neutral" | "accent" | "warning"
    """
    color = _SENTIMENT_COLORS.get(sentiment, ACCENT_PRIMARY)
    st.markdown(f'''
        <div style="background:{WHITE};
             border-radius:{CARD_RADIUS};padding:{CARD_PADDING};text-align:center;
             border:1px solid {BORDER_LIGHT};border-left:4px solid {color};
             box-shadow:0 1px 4px rgba(0,0,0,0.04);margin-bottom:1rem;">
            <div style="font-family:{FONT_BODY};font-size:0.65rem;font-weight:600;
                 color:{SLATE};text-transform:uppercase;letter-spacing:0.08em;
                 margin-bottom:0.5rem;">{label}</div>
            <div style="font-family:{FONT_HEADING};font-size:2.1rem;font-weight:700;
                 color:{color};line-height:1;margin-bottom:0.25rem;">{value}</div>
            <div style="font-family:{FONT_BODY};font-size:0.6rem;
                 color:{SLATE};text-transform:uppercase;
                 letter-spacing:0.05em;">{unit}</div>
        </div>
    ''', unsafe_allow_html=True)


# ---- Premium Stat Card (light background) --------------------------

def premium_stat_card(label, value, subtitle="", sentiment="neutral"):
    """
    Light-background stat card with subtle shadow.

    sentiment: "positive" | "negative" | "neutral"
    """
    value_color = {
        "positive": POSITIVE,
        "negative": NEGATIVE,
        "neutral":  CHARCOAL,
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


# ---- Sentiment helpers ----------------------------------------------

def sg_sentiment(val, threshold=None):
    """
    Determine sentiment string from a numeric value.

    With threshold: >= threshold is positive, else negative.
    Without threshold: >0 positive, <0 negative, 0 neutral.
    """
    try:
        v = float(val)
    except (ValueError, TypeError):
        return "neutral"
    if threshold is not None:
        return "positive" if v >= threshold else "negative"
    if v > 0:
        return "positive"
    elif v < 0:
        return "negative"
    return "neutral"


def pct_sentiment_above(val, threshold_key):
    """Positive when value >= threshold (higher is better)."""
    t = THRESHOLDS.get(threshold_key, 0)
    return "positive" if val >= t else "negative"


def pct_sentiment_below(val, threshold_key):
    """Positive when value <= threshold (lower is better)."""
    t = THRESHOLDS.get(threshold_key, 0)
    return "positive" if val <= t else "negative"


def get_sentiment_color(sentiment):
    """Get hex color for sentiment string."""
    return _SENTIMENT_COLORS.get(sentiment, ACCENT_PRIMARY)


def severity_color(severity):
    """
    Get color for severity levels (Coach's Corner).
    severity: "critical" | "significant" | "moderate"
    """
    return {
        "critical": NEGATIVE,
        "significant": WARNING,
        "moderate": ACCENT_MUTED,
    }.get(severity, ACCENT_MUTED)


def bounce_back_sentiment(pct):
    """Sentiment for bounce back % (higher is better)."""
    return pct_sentiment_above(pct, "pct_bounce_back")


def drop_off_sentiment(pct):
    """Sentiment for drop off % (lower is better)."""
    return "positive" if pct <= 25 else "negative"


def gas_pedal_sentiment(pct):
    """Sentiment for gas pedal % (higher is better)."""
    return "positive" if pct >= 20 else "neutral"


def bogey_train_sentiment(count):
    """Sentiment for bogey train count (lower is better)."""
    return "negative" if count > 0 else "positive"


def grit_score_sentiment(score):
    """Sentiment for Tiger 5 grit score."""
    if score >= 80:
        return "positive"
    elif score >= 60:
        return "warning"
    return "negative"


def bogey_rate_sentiment(rate):
    """Sentiment for bogey avoidance rate (lower is better)."""
    if rate <= 10:
        return "positive"
    elif rate < 30:
        return "warning"
    return "negative"


def conversion_pct_sentiment(pct):
    """Sentiment for birdie conversion % (higher is better)."""
    return "positive" if pct >= 30 else "negative"


# ---- Performance Driver Card (Coach's Corner) ----------------------

def performance_driver_card(rank, driver):
    """Render a single Performance Driver as a premium numbered card."""
    sev = driver.get("severity", "moderate")
    border_color = severity_color(sev)
    sev_label = sev.capitalize()
    sg_pr = driver["sg_per_round"]
    sg_color = POSITIVE if sg_pr > 0 else NEGATIVE

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


# ---- Practice Priority Card (Coach's Corner) -----------------------

def practice_priority_card(item, number, border_color):
    """Render a single practice priority item in tiered format."""
    label = item.get('label', '')
    metric = item.get('metric', '')
    target = item.get('target', '')
    impact = item.get('impact', 0)

    st.markdown(f'''
        <div style="background:{WHITE};border-radius:8px;
             padding:0.75rem 1rem;margin-bottom:0.5rem;
             border:1px solid {BORDER_LIGHT};
             border-left:4px solid {border_color};
             box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="display:flex;align-items:flex-start;gap:0.75rem;">
                <div style="font-family:{FONT_HEADING};font-size:1.1rem;
                     font-weight:700;color:{border_color};min-width:24px;
                     text-align:center;flex-shrink:0;">{number}</div>
                <div style="flex:1;">
                    <div style="font-family:{FONT_HEADING};font-size:0.9rem;
                         font-weight:600;color:{CHARCOAL};margin-bottom:0.3rem;">
                        {label}</div>
                    <div style="font-family:{FONT_BODY};font-size:0.75rem;
                         color:{CHARCOAL_LIGHT};">
                        <strong>Current:</strong> {metric} | <strong>Target:</strong> {target}</div>
                    <div style="font-family:{FONT_BODY};font-size:0.7rem;
                         color:{SLATE};margin-top:0.2rem;">
                        Impact: {impact:.1f} strokes/round</div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)


# ---- Strength Card (Coach's Corner) --------------------------------

def strength_maintenance_card(item, number):
    """Render a single strength to maintain card."""
    label = item.get('label', '')
    metric = item.get('metric', '')
    sg_value = item.get('sg_value', 0)

    st.markdown(f'''
        <div style="background:{WHITE};border-radius:8px;
             padding:0.75rem 1rem;margin-bottom:0.5rem;
             border:1px solid {BORDER_LIGHT};
             border-left:4px solid {POSITIVE};
             box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="display:flex;align-items:flex-start;gap:0.75rem;">
                <div style="font-family:{FONT_HEADING};font-size:1.1rem;
                     font-weight:700;color:{POSITIVE};min-width:24px;
                     text-align:center;flex-shrink:0;">{number}</div>
                <div style="flex:1;">
                    <div style="font-family:{FONT_HEADING};font-size:0.9rem;
                         font-weight:600;color:{CHARCOAL};margin-bottom:0.3rem;">
                        {label}</div>
                    <div style="font-family:{FONT_BODY};font-size:0.75rem;
                         color:{CHARCOAL_LIGHT};">
                        <strong>Performance:</strong> {metric}</div>
                    <div style="font-family:{FONT_BODY};font-size:0.7rem;
                         color:{POSITIVE};margin-top:0.2rem;">
                        Gaining: {sg_value:+.2f} strokes/round</div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)


# ---- Compact Stat Card (Coach's Corner) ----------------------------

def compact_stat_card(label, value, subtitle="", sentiment="neutral"):
    """
    Render a compact stat card with smaller fonts.
    Used in PlayerPath detail items.
    """
    sentiment_colors = {
        "positive": POSITIVE,
        "negative": NEGATIVE,
        "warning": WARNING,
        "neutral": CHARCOAL,
        "accent": ACCENT_PRIMARY,
    }
    color = sentiment_colors.get(sentiment, CHARCOAL)

    st.markdown(f'''
        <div style="background:{WHITE};border-radius:{CARD_RADIUS};
             padding:{CARD_PADDING};text-align:center;
             border:1px solid {BORDER_LIGHT};
             box-shadow:0 1px 3px rgba(0,0,0,0.04);margin-bottom:0.75rem;">
            <div style="font-family:{FONT_BODY};font-size:0.55rem;
                 font-weight:600;color:{SLATE};text-transform:uppercase;
                 letter-spacing:0.08em;margin-bottom:0.4rem;">{label}</div>
            <div style="font-family:{FONT_HEADING};font-size:1.4rem;
                 font-weight:700;color:{color};line-height:1;">
                {value}</div>
            {f'<div style="font-family:{FONT_BODY};font-size:0.55rem;color:{SLATE};margin-top:0.25rem;">{subtitle}</div>' if subtitle else ''}
        </div>
    ''', unsafe_allow_html=True)


# ---- PlayerPath Category Card (Coach's Corner) ---------------------

def player_path_category_card(entry, is_strength):
    """Render a PlayerPath category (strength/weakness) card block."""
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

    # Detail items in collapsible expander
    if entry.get("detail_items"):
        with st.expander(f"View {entry['headline']} Details"):
            cols = st.columns(min(len(entry["detail_items"]), 4))
            for i, item in enumerate(entry["detail_items"][:4]):
                with cols[i % len(cols)]:
                    compact_stat_card(
                        item["label"],
                        item["value"],
                        sentiment=item.get("sentiment", "neutral"),
                    )


# ---- Sidebar helpers ------------------------------------------------

def sidebar_title(text):
    st.markdown(
        f'<p style="font-family:{FONT_HEADING};font-size:1.4rem;font-weight:600;'
        f'color:{ACCENT_PRIMARY};margin-bottom:0.5rem;padding-bottom:1rem;'
        f'border-bottom:1px solid {BORDER_LIGHT};">{text}</p>',
        unsafe_allow_html=True,
    )


def sidebar_label(text):
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.75rem;font-weight:500;'
        f'color:{ACCENT_SECONDARY};text-transform:uppercase;letter-spacing:0.08em;'
        f'margin-bottom:0.5rem;margin-top:1.25rem;">{text}</p>',
        unsafe_allow_html=True,
    )
