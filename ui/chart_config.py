# ============================================================
# PLOTLY CHART DEFAULTS & HELPERS
# ============================================================

from ui.theme import (
    WHITE, CHARCOAL, BORDER_LIGHT, POSITIVE, POSITIVE_BG,
    POSITIVE_TEXT, NEGATIVE, NEGATIVE_BG, NEGATIVE_TEXT,
    FONT_BODY, THRESHOLDS,
)

# Shared base layout — spread into every fig.update_layout() call
CHART_LAYOUT = dict(
    plot_bgcolor=WHITE,
    paper_bgcolor=WHITE,
    font=dict(family="Inter", color=CHARCOAL),
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


def sg_cell_style(val):
    """Inline CSS for SG heatmap / table cells (conditional colouring)."""
    try:
        v = float(val)
    except (ValueError, TypeError):
        return ""
    strong = THRESHOLDS["sg_strong"]
    if v > strong:
        return f"background:{POSITIVE_BG};color:{POSITIVE_TEXT};font-weight:600;"
    if v > 0:
        return f"background:#E8F5E9;color:{POSITIVE};"
    if v < -strong:
        return f"background:{NEGATIVE_BG};color:{NEGATIVE_TEXT};font-weight:600;"
    if v < 0:
        return f"background:#FCE4EC;color:{NEGATIVE};"
    return f"color:{CHARCOAL};"


# Diverging heatmap colorscale centred on zero
SG_HEATMAP_COLORSCALE = [
    [0.0, NEGATIVE],
    [0.5, "#f5f5f5"],
    [1.0, POSITIVE],
]
