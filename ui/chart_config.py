# ============================================================
# PLOTLY CHART DEFAULTS & HELPERS
# ============================================================

from ui.theme import (
    WHITE, CHARCOAL, BORDER_LIGHT, WARM_GRAY, POSITIVE, POSITIVE_BG,
    POSITIVE_TEXT, NEGATIVE, NEGATIVE_BG, NEGATIVE_TEXT,
    SG_STRONG, SG_GAIN, SG_NEUTRAL, SG_LOSS, SG_WEAK,
    FONT_BODY, THRESHOLDS,
)

# Shared base layout — spread into every fig.update_layout() call
CHART_LAYOUT = dict(
    plot_bgcolor=WHITE,
    paper_bgcolor=WHITE,
    font=dict(family="Outfit", color=CHARCOAL),
)


def base_layout(**overrides):
    """Return a copy of CHART_LAYOUT merged with caller overrides."""
    layout = dict(CHART_LAYOUT)
    layout.update(overrides)
    return layout


def trend_layout(height=400):
    """Standard layout for trend line / bar charts."""
    return base_layout(
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        margin=dict(t=60, b=80, l=60, r=40),
        hovermode="x unified",
        xaxis=dict(tickangle=-45),
        yaxis=dict(gridcolor=BORDER_LIGHT,
                   zerolinecolor=CHARCOAL, zerolinewidth=2),
    )


def sg_bar_color(val):
    """POSITIVE or NEGATIVE colour based on SG sign."""
    return POSITIVE if val >= 0 else NEGATIVE


def sg_color_5(val):
    """5-level SG color per v1.6 scale: teal-to-rust, gold at neutral."""
    try:
        v = float(val)
    except (ValueError, TypeError):
        return SG_NEUTRAL
    if v >= 1.0:
        return SG_STRONG
    if v >= 0.3:
        return SG_GAIN
    if v >= -0.3:
        return SG_NEUTRAL
    if v >= -1.0:
        return SG_LOSS
    return SG_WEAK


def sg_cell_style(val):
    """Inline CSS for SG heatmap / table cells (5-level conditional colouring)."""
    try:
        v = float(val)
    except (ValueError, TypeError):
        return ""
    if v >= 1.0:
        return f"background:{POSITIVE_BG};color:{POSITIVE_TEXT};font-weight:700;"
    if v >= 0.3:
        return f"background:{POSITIVE_BG};color:{POSITIVE_TEXT};font-weight:600;"
    if v > 0:
        return f"background:{POSITIVE_BG};color:{POSITIVE};"
    if v <= -1.0:
        return f"background:{NEGATIVE_BG};color:{NEGATIVE_TEXT};font-weight:700;"
    if v <= -0.3:
        return f"background:{NEGATIVE_BG};color:{NEGATIVE_TEXT};font-weight:600;"
    if v < 0:
        return f"background:{NEGATIVE_BG};color:{NEGATIVE};"
    return f"color:{CHARCOAL};"


# Diverging heatmap colorscale — 5-stop, gold at centre
SG_HEATMAP_COLORSCALE = [
    [0.0,  SG_WEAK],
    [0.25, SG_LOSS],
    [0.5,  SG_NEUTRAL],
    [0.75, SG_GAIN],
    [1.0,  SG_STRONG],
]

# Colorbar config for SG heatmaps — shows tick labels at every scale breakpoint
SG_HEATMAP_COLORBAR = dict(
    title=dict(text="SG/Shot", side="right", font=dict(size=12)),
    tickvals=[-1.0, -0.3, 0, 0.3, 1.0],
    ticktext=["-1.0", "-0.3", "0", "+0.3", "+1.0"],
    tickfont=dict(size=11),
    thickness=14,
    len=0.85,
    outlinewidth=0,
)
