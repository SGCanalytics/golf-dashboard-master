# ============================================================
# FORMATTING UTILITIES — GLOBAL FORMATTING CONTRACT
# ============================================================
# Rules applied everywhere (cards, charts, tables):
#   1) Dates:       mm/dd/yy        (e.g. 02/06/26)
#   2) SG metrics:  sign + 2 dp     (e.g. +1.20, -0.35)
#   3) Percentages: 0 dp + %        (e.g. 63%)
# ============================================================


def format_date(dt_val):
    """Format a date/datetime to mm/dd/yy string."""
    if hasattr(dt_val, "strftime"):
        return dt_val.strftime("%m/%d/%y")
    return str(dt_val)


def format_sg(val):
    """Strokes gained: always show sign, exactly 2 decimal places."""
    try:
        return f"{float(val):+.2f}"
    except (ValueError, TypeError):
        return "-"


def format_pct(val, decimals=0):
    """Percentage with no decimals by default. Input is already 0-100 scale."""
    try:
        return f"{float(val):.{decimals}f}%"
    except (ValueError, TypeError):
        return "-"


def format_pct_safe(count, total):
    """Calculate and format a percentage safely (count / total * 100)."""
    if total and total > 0:
        return f"{count / total * 100:.0f}%"
    return "-"


def format_per_round(count, rounds):
    """Per-round metric with 1 decimal place."""
    if rounds and rounds > 0:
        return f"{count / rounds:.1f}"
    return "-"


def format_score(val, decimals=2):
    """Scoring average, e.g. 72.45."""
    try:
        return f"{float(val):.{decimals}f}"
    except (ValueError, TypeError):
        return "-"


def format_distance(val, unit="yds"):
    """Distance as integer with unit, e.g. '285 yds'."""
    try:
        return f"{int(round(float(val)))} {unit}"
    except (ValueError, TypeError):
        return "-"


def format_sg_with_class(val):
    """Return (formatted_string, css_class) for an SG value."""
    try:
        v = float(val)
        formatted = f"{v:+.2f}"
        if v > 0:
            return formatted, "positive"
        elif v < 0:
            return formatted, "negative"
        return formatted, "neutral"
    except (ValueError, TypeError):
        return "-", "neutral"


def round_label(date, course):
    """Standard round label for chart x-axes: '01/15/26 Pine Valley'."""
    return f"{format_date(date)} {course}"
