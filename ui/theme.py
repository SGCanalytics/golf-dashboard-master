# ============================================================
# DESIGN TOKENS — PREMIUM NEUTRAL PALETTE
# ============================================================
# Single source of truth for all visual constants.
# No school-specific colors. Neutral, sophisticated, timeless.
# ============================================================

# --- PRIMARY PALETTE ---
CHARCOAL       = "#2B2B2B"
CHARCOAL_LIGHT = "#3D3D3D"
SLATE          = "#64748B"
WHITE          = "#FFFFFF"
OFF_WHITE      = "#FAFAFA"
WARM_GRAY      = "#F5F3F0"
BORDER_LIGHT   = "#E2E2E2"
BORDER_MEDIUM  = "#D1D5DB"

# --- ACCENT COLORS ---
ACCENT_PRIMARY   = "#3B82F6"   # vivid blue — primary accent
ACCENT_SECONDARY = "#6366F1"   # indigo — secondary accent
ACCENT_MUTED     = "#93C5FD"   # light blue for subtle highlights

# --- SEMANTIC / CONDITIONAL FORMATTING COLORS ---
POSITIVE       = "#059669"     # emerald green
POSITIVE_BG    = "#D1FAE5"     # light green cell background
POSITIVE_TEXT  = "#065F46"     # dark green cell text
NEGATIVE       = "#DC2626"     # red
NEGATIVE_BG    = "#FEE2E2"     # light red cell background
NEGATIVE_TEXT  = "#991B1B"     # dark red cell text
NEUTRAL        = "#6B7280"     # gray for zero/neutral values
WARNING        = "#F59E0B"     # amber for caution states

# --- CHART CATEGORY COLORS ---
CHART_PALETTE = [
    "#3B82F6",  # blue
    "#2B2B2B",  # charcoal
    "#059669",  # green
    "#8B5CF6",  # violet
    "#DC2626",  # red
    "#F59E0B",  # amber
]

CHART_DRIVING    = CHART_PALETTE[0]
CHART_APPROACH   = CHART_PALETTE[1]
CHART_SHORT_GAME = CHART_PALETTE[2]
CHART_PUTTING    = CHART_PALETTE[3]
CHART_FAIL       = CHART_PALETTE[4]
CHART_SECONDARY  = CHART_PALETTE[5]

# --- DONUT / OUTCOME CHART COLORS ---
OUTCOME_COLORS = {
    "Eagle":            "#F59E0B",
    "Birdie":           "#059669",
    "Par":              "#2B2B2B",
    "Bogey":            "#DC2626",
    "Double or Worse":  "#8B5CF6",
}

DONUT_SEQUENCE = ["#059669", "#3B82F6", "#F59E0B", "#DC2626"]

# --- TYPOGRAPHY ---
FONT_HEADING = "'Playfair Display', Georgia, serif"
FONT_BODY    = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"

# --- SPACING ---
CARD_RADIUS  = "12px"
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
