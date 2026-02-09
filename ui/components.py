# ============================================================
# SHARED UI COMPONENTS
# ============================================================
# Reusable, themeable building blocks for every tab.
# Light, airy aesthetic — white cards with subtle borders.
# ============================================================

import streamlit as st
import plotly.graph_objects as go
from ui.theme import (
    CHARCOAL, CHARCOAL_LIGHT, SLATE, WHITE, BORDER_LIGHT,
    ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_MUTED, ACCENT_PALE,
    POSITIVE, NEGATIVE, NEUTRAL, WARNING,
    FONT_HEADING, FONT_BODY, CARD_RADIUS, CARD_PADDING,
    THRESHOLDS,
    COMPARISON_GROUP_1, COMPARISON_GROUP_1_BG,
    COMPARISON_GROUP_2, COMPARISON_GROUP_2_BG,
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


def subheader(title):
    """Subheader without accent line."""
    st.markdown(
        f'<p style="font-family:{FONT_BODY};font-size:0.85rem;'
        f'font-weight:600;color:{SLATE};text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:0.5rem;">{title}</p>',
        unsafe_allow_html=True,
    )


# ============================================================
# COMPARISON COMPONENTS
# ============================================================


def comparison_radar_chart(categories, group1_values, group2_values,
                           group1_name, group2_name, title):
    """
    Render a radar chart comparing two groups.
    
    Args:
        categories: list of category labels
        group1_values: list of values for Group 1
        group2_values: list of values for Group 2
        group1_name: display name for Group 1
        group2_name: display name for Group 2
        title: chart title
    """
    fig = go.Figure()
    
    # Group 1 - filled area (purple)
    fig.add_trace(go.Scatterpolar(
        r=group1_values,
        theta=categories,
        fill='toself',
        name=group1_name,
        line_color=COMPARISON_GROUP_1,
        fillcolor=COMPARISON_GROUP_1,
        line_width=2,
        opacity=0.3,
    ))
    
    # Group 2 - filled area (charcoal gray)
    fig.add_trace(go.Scatterpolar(
        r=group2_values,
        theta=categories,
        fill='toself',
        name=group2_name,
        line_color=COMPARISON_GROUP_2,
        fillcolor=COMPARISON_GROUP_2,
        line_width=2,
        opacity=0.3,
    ))
    
    fig.update_polars(
        radialaxis=dict(
            visible=True,
            showline=False,
            gridcolor=BORDER_LIGHT,
        ),
        bgcolor=WHITE,
    )
    
    fig.update_layout(
        title=dict(text=title, font=dict(family=FONT_HEADING, size=14)),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(t=40, b=60, l=40, r=40),
        height=300,
        paper_bgcolor=WHITE,
        font=dict(family=FONT_BODY, color=CHARCOAL),
    )
    
    st.plotly_chart(fig, use_container_width=True)


def comparison_grouped_bar(labels, group1_values, group2_values,
                           group1_name, group2_name, title,
                           value_format='{:.1f}'):
    """
    Render a grouped bar chart comparing two groups.
    
    Args:
        labels: list of category labels
        group1_values: list of values for Group 1
        group2_values: list of values for Group 2
        group1_name: display name for Group 1
        group2_name: display name for Group 2
        title: chart title
        value_format: format string for values
    """
    # Defensive: ensure value_format has a valid default
    if value_format is None:
        value_format = '{:.1f}'
    
    fig = go.Figure()
    
    # Group 1 bars
    fig.add_trace(go.Bar(
        x=labels,
        y=group1_values,
        name=group1_name,
        marker_color=COMPARISON_GROUP_1,
        text=[value_format.format(v) for v in group1_values],
        textposition='outside',
    ))
    
    # Group 2 bars
    fig.add_trace(go.Bar(
        x=labels,
        y=group2_values,
        name=group2_name,
        marker_color=COMPARISON_GROUP_2,
        text=[value_format.format(v) for v in group2_values],
        textposition='outside',
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(family=FONT_HEADING, size=14)),
        xaxis=dict(title=''),
        yaxis=dict(title='', gridcolor=BORDER_LIGHT),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(t=60, b=40, l=40, r=40),
        height=350,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(family=FONT_BODY, color=CHARCOAL),
        barmode='group',
    )
    
    st.plotly_chart(fig, use_container_width=True)


def comparison_stacked_bar(labels, group1_values, group2_values,
                           group1_name, group2_name, title):
    """
    Render a stacked bar chart comparing two groups.
    Useful for showing breakdowns (e.g., Tiger 5 categories).
    """
    fig = go.Figure()
    
    # Group 1
    fig.add_trace(go.Bar(
        x=labels,
        y=group1_values,
        name=group1_name,
        marker_color=COMPARISON_GROUP_1,
    ))
    
    # Group 2
    fig.add_trace(go.Bar(
        x=labels,
        y=group2_values,
        name=group2_name,
        marker_color=COMPARISON_GROUP_2,
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(family=FONT_HEADING, size=14)),
        xaxis=dict(title=''),
        yaxis=dict(title='', gridcolor=BORDER_LIGHT),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(t=60, b=40, l=40, r=40),
        height=350,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(family=FONT_BODY, color=CHARCOAL),
        barmode='group',
    )
    
    st.plotly_chart(fig, use_container_width=True)


def comparison_stat_row(g1_label, g1_value, g2_label, g2_value,
                        label, unit='', show_diff=False):
    """
    Render a row comparing two stat values side by side.
    
    Args:
        g1_label: label for Group 1 value
        g1_value: value for Group 1
        g2_label: label for Group 2 value
        g2_value: value for Group 2
        label: metric label
        unit: optional unit string
        show_diff: whether to show difference indicator
    """
    col1, col2, col3 = st.columns([1, 1, 0.5])
    
    with col1:
        st.markdown(f'''
            <div style="background:{WHITE};border-radius:{CARD_RADIUS};
                 padding:{CARD_PADDING};text-align:center;
                 border:1px solid {BORDER_LIGHT};margin-bottom:1rem;
                 border-left:4px solid {COMPARISON_GROUP_1};">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;font-weight:600;
                     color:{SLATE};text-transform:uppercase;letter-spacing:0.08em;
                     margin-bottom:0.3rem;">{g1_label}</div>
                <div style="font-family:{FONT_HEADING};font-size:1.5rem;font-weight:700;
                     color:{COMPARISON_GROUP_1};line-height:1;">{g1_value}</div>
                <div style="font-family:{FONT_BODY};font-size:0.55rem;
                     color:{SLATE};text-transform:uppercase;
                     letter-spacing:0.05em;margin-top:0.2rem;">{unit}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
            <div style="background:{WHITE};border-radius:{CARD_RADIUS};
                 padding:{CARD_PADDING};text-align:center;
                 border:1px solid {BORDER_LIGHT};margin-bottom:1rem;
                 border-left:4px solid {COMPARISON_GROUP_2};">
                <div style="font-family:{FONT_BODY};font-size:0.6rem;font-weight:600;
                     color:{SLATE};text-transform:uppercase;letter-spacing:0.08em;
                     margin-bottom:0.3rem;">{g2_label}</div>
                <div style="font-family:{FONT_HEADING};font-size:1.5rem;font-weight:700;
                     color:{COMPARISON_GROUP_2};line-height:1;">{g2_value}</div>
                <div style="font-family:{FONT_BODY};font-size:0.55rem;
                     color:{SLATE};text-transform:uppercase;
                     letter-spacing:0.05em;margin-top:0.2rem;">{unit}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        if show_diff and g1_value != g2_value:
            try:
                diff = float(g2_value) - float(g1_value)
                diff_color = POSITIVE if diff < 0 else NEGATIVE
                diff_symbol = '−' if diff < 0 else '+'
                st.markdown(f'''
                    <div style="background:{WHITE};border-radius:{CARD_RADIUS};
                         padding:{CARD_PADDING};text-align:center;
                         border:1px solid {BORDER_LIGHT};margin-bottom:1rem;">
                        <div style="font-family:{FONT_BODY};font-size:0.55rem;font-weight:600;
                             color:{SLATE};text-transform:uppercase;
                             letter-spacing:0.05em;margin-bottom:0.2rem;">Diff</div>
                        <div style="font-family:{FONT_HEADING};font-size:1.3rem;font-weight=700;
                             color:{diff_color};line-height:1;">{diff_symbol}{abs(diff):.1f}</div>
                    </div>
                ''', unsafe_allow_html=True)
            except (ValueError, TypeError):
                pass


def comparison_mode_selector(players):
    """
    Render the comparison mode selector with mode-specific controls.
    
    Returns:
        tuple: (mode, mode_params)
    """
    st.markdown(
        f'<p style="font-family:{FONT_HEADING};font-size:1.3rem;font-weight:600;'
        f'color:{CHARCOAL};margin-bottom:1rem;">Comparison Mode</p>',
        unsafe_allow_html=True,
    )
    
    mode = st.selectbox(
        "Select Comparison Mode",
        options=["Player vs Player", "Round Quality", "Time Period"],
        index=0,
        label_visibility="collapsed",
    )
    
    st.markdown('<br>', unsafe_allow_html=True)
    
    if mode == "Player vs Player":
        col1, col2 = st.columns(2)
        
        with col1:
            player1 = st.selectbox("Player 1 (Group 1)", options=players, index=0 if players else None)
        with col2:
            player2 = st.selectbox("Player 2 (Group 2)", options=players, index=1 if len(players) > 1 else 0)
        
        return 'player', {'player1': player1, 'player2': player2}
    
    elif mode == "Round Quality":
        col1, col2 = st.columns(2)
        
        qualities = ["Under Par", "Par to +3", "+4+"]
        
        with col1:
            quality1 = st.selectbox("Group 1 Quality", options=qualities, index=0)
        with col2:
            quality2 = st.selectbox("Group 2 Quality", options=qualities, index=2)
        
        return 'round_quality', {'quality1': quality1, 'quality2': quality2}
    
    elif mode == "Time Period":
        col1, col2 = st.columns(2)
        
        with col1:
            num_recent = st.number_input("Recent Rounds (Group 1)", min_value=1, max_value=20, value=5)
        with col2:
            num_previous = st.number_input("Previous Rounds (Group 2)", min_value=1, max_value=20, value=5)
        
        return 'time_period', {'num_recent': num_recent, 'num_previous': num_previous}
    
    return 'player', {}


def comparison_legend(group1_label, group2_label):
    """Render a legend showing group colors."""
    st.markdown(
        f'<div style="display:flex;justify-content:center;gap:2rem;margin-bottom:1rem;">'
        f'<span style="color:{COMPARISON_GROUP_1};font-family:{FONT_BODY};font-weight:600;">'
        f'&#9679; {group1_label}</span>'
        f'<span style="color:{COMPARISON_GROUP_2};font-family:{FONT_BODY};font-weight:600;">'
        f'&#9679; {group2_label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
