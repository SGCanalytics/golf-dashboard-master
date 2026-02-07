# ============================================================
# DESIGN TOKENS — PREMIUM GREEN PALETTE
# ============================================================
# Inspired by private golf club aesthetics: clean whites,
# deep olive/forest greens, warm grays, elegant serif headings.
# ============================================================

# --- PRIMARY PALETTE ---
CHARCOAL       = "#333333"     # text color — warm dark gray (not black)
CHARCOAL_LIGHT = "#555555"     # secondary text
SLATE          = "#6B7280"     # muted labels
WHITE          = "#FFFFFF"
OFF_WHITE      = "#F8F7F4"     # warm off-white page background
WARM_GRAY      = "#F2F0EC"     # card/table header backgrounds
BORDER_LIGHT   = "#E0DDD7"     # warm light border
BORDER_MEDIUM  = "#C9C5BC"     # medium border

# --- ACCENT COLORS (deep olive/forest green) ---
ACCENT_PRIMARY   = "#3D5A3E"   # deep forest green — primary accent
ACCENT_SECONDARY = "#5A7A5C"   # medium sage — secondary accent
ACCENT_MUTED     = "#8FA890"   # light sage for subtle highlights
ACCENT_PALE      = "#E8EDE8"   # very pale green for card backgrounds

# --- SEMANTIC / CONDITIONAL FORMATTING COLORS ---
POSITIVE       = "#2D6A4F"     # deep green (positive SG / good)
POSITIVE_BG    = "#D1FAE5"     # light green cell background
POSITIVE_TEXT  = "#065F46"     # dark green cell text
NEGATIVE       = "#C53030"     # muted red (negative SG / bad)
NEGATIVE_BG    = "#FED7D7"     # light red cell background
NEGATIVE_TEXT  = "#9B2C2C"     # dark red cell text
NEUTRAL        = "#6B7280"     # gray for zero/neutral values
WARNING        = "#B7791F"     # muted amber for caution states

# --- CHART CATEGORY COLORS ---
CHART_PALETTE = [
    "#3D5A3E",  # deep green (driving)
    "#8B6F47",  # warm brown (approach)
    "#2D6A4F",  # forest green (short game)
    "#7C6F9B",  # muted violet (putting)
    "#C53030",  # muted red (fail/recovery)
    "#B7791F",  # muted amber (secondary)
]

CHART_DRIVING    = CHART_PALETTE[0]
CHART_APPROACH   = CHART_PALETTE[1]
CHART_SHORT_GAME = CHART_PALETTE[2]
CHART_PUTTING    = CHART_PALETTE[3]
CHART_FAIL       = CHART_PALETTE[4]
CHART_SECONDARY  = CHART_PALETTE[5]

# --- DONUT / OUTCOME CHART COLORS ---
OUTCOME_COLORS = {
    "Eagle":            "#B7791F",
    "Birdie":           "#2D6A4F",
    "Par":              "#3D5A3E",
    "Bogey":            "#C53030",
    "Double or Worse":  "#7C6F9B",
}

DONUT_SEQUENCE = ["#2D6A4F", "#3D5A3E", "#B7791F", "#C53030"]

# --- TYPOGRAPHY ---
FONT_HEADING = "'Playfair Display', Georgia, serif"
FONT_BODY    = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"

# --- SPACING ---
CARD_RADIUS  = "10px"
CARD_PADDING = "1.25rem 1rem"
SECTION_GAP  = "2.5rem"

# --- CONDITIONAL FORMATTING THRESHOLDS ---
# Centralized so every tab uses identical logic.
THRESHOLDS = {
    "sg_positive":            0,
    "sg_strong":              0.25,
    "pct_fairway":            50,
    "pct_nonplayable":        15,
    "pct_positive_shot":      50,
    "pct_poor_shot":          20,
    "pct_inside_8ft":         60,
    "pct_make_0_3":           95,
    "pct_lag_miss":           20,
    "pct_lag_inside_3":       50,
    "pct_trouble_bogey":      50,
    "pct_poor_drive":         20,
    "pct_positive_sg_drives": 50,
    "pct_bounce_back":        50,
}
