# ============================================================
# DESIGN TOKENS — COLOR SYSTEM v1.6
# ============================================================
# Warm Grey · Forest Green · Gold · Premium · Data-first
#
# Three distinct color roles:
#   1. Foundation neutrals — backgrounds, text, borders
#   2. Brand green — UI only (buttons, nav, selected states)
#      NEVER used as a data signal
#   3. Data semantics — score and SG colors only
#      NEVER used for interactive UI elements
# ============================================================

# --- FOUNDATION — Warm Grey ---
# Grey-white base. Brown undertone removed — reads as
# sophisticated and architectural, not warm or casual.
LINEN       = "#F4F3F1"   # page background — warm grey-white
PARCHMENT   = "#ECEAE7"   # recessed areas, sidebar
STONE       = "#DCDAD6"   # borders, dividers, rules
PEWTER      = "#8F9490"   # labels, captions, axis text — cool grey-green
FLINT       = "#5E6460"   # secondary body text — cool grey-slate
INK         = "#252220"   # primary text, headings, key values
WHITE       = "#FFFFFF"   # card surfaces, modals, inputs

# --- BRAND — Forest Green (UI ONLY) ---
# Used exclusively for interactive UI: buttons, selected states,
# active navigation, brand marks.
# NEVER used on data visualisations.
FOREST      = "#2D4A2D"   # primary CTA, selected states, brand
CANOPY      = "#1E3320"   # pressed / hover-dark states
GROVE       = "#3D6640"   # hover / active state
FOREST_TINT = "#EBF0EB"   # hover background wash, selected rows

# --- GOLD — Premium Accent ---
GOLD        = "#B8973A"   # premium accent, key metrics, brand labels
GOLD_LIGHT  = "#D4AF5A"   # highlights, icon fills
GOLD_TINT   = "#F7F4EA"   # subtle wash, hover states

# --- DATA SEMANTIC — Score ---
# Muted, confident tones for score outcomes.
# Since they appear rarely they sit quietly until needed.
UNDER       = "#2D6B4A"   # under par — deep teal-green
EVEN        = "#8A9890"   # even par — warm grey
BOGEY       = "#C07840"   # bogey — warm terracotta
DOUBLE      = "#A84830"   # double+ — deep rust

# --- STROKES GAINED — 5-Level Scale ---
# Teal-to-rust, centred on gold neutral.
# Score colors and SG colors occupy separate hue families —
# teal/terracotta for SG, never overlapping with brand green.
SG_STRONG   = "#2D6B4A"   # +1.0+  elite gain
SG_GAIN     = "#5A9E7A"   # +0.3 to +0.9  above average
SG_NEUTRAL  = "#B8973A"   # ±0.3   baseline (gold)
SG_LOSS     = "#C07840"   # -0.3 to -0.9  below average
SG_WEAK     = "#A84830"   # -1.0+  concern

# --- CHART CATEGORY COLORS ---
CHART_PALETTE = [
    FOREST,      # deep forest (driving)
    "#8B6F47",   # warm brown (approach)
    FLINT,       # cool grey-slate (short game)
    "#7C6F9B",   # muted violet (putting)
    DOUBLE,      # deep rust (fail/recovery)
    GOLD,        # antique gold (secondary)
]

CHART_DRIVING    = CHART_PALETTE[0]
CHART_APPROACH   = CHART_PALETTE[1]
CHART_SHORT_GAME = CHART_PALETTE[2]
CHART_PUTTING    = CHART_PALETTE[3]
CHART_FAIL       = CHART_PALETTE[4]
CHART_SECONDARY  = CHART_PALETTE[5]

# --- OUTCOME / DONUT CHART COLORS ---
OUTCOME_COLORS = {
    "Eagle":           GOLD,
    "Birdie":          UNDER,
    "Par":             EVEN,
    "Bogey":           BOGEY,
    "Double or Worse": DOUBLE,
}

DONUT_SEQUENCE = [UNDER, EVEN, GOLD, BOGEY, DOUBLE]

# --- TYPOGRAPHY — Three-family system ---
FONT_HEADING = "'Cormorant Garamond', Georgia, serif"                      # display / headings / large values
FONT_DATA    = "'DM Mono', monospace"                                      # data labels, axes, code, captions
FONT_BODY    = "'Outfit', -apple-system, BlinkMacSystemFont, sans-serif"   # UI / body / navigation

# --- GRADIENTS ---
GRAD_CARD   = "linear-gradient(160deg, #FFFFFF 0%, #FAFAF9 100%)"
GRAD_HERO   = "linear-gradient(160deg, #FFFFFF 0%, #F7F6F4 100%)"
GRAD_FOREST = "linear-gradient(135deg, #1E3320 0%, #2D4A2D 100%)"
GRAD_GOLD   = "linear-gradient(135deg, #B8973A 0%, #D4AF5A 100%)"

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
    "pct_inside_8ft":         70,
    "pct_make_0_3":           95,
    "pct_lag_miss":           20,
    "pct_lag_inside_3":       50,
    "pct_trouble_bogey":      50,
    "pct_poor_drive":         20,
    "pct_positive_sg_drives": 50,
    "pct_bounce_back":        50,
}

# ============================================================
# BACKWARD-COMPATIBILITY ALIASES
# ============================================================
# Old token names map to new v1.6 values.
# All existing tab code continues to work without changes.
# ============================================================

CHARCOAL       = INK
CHARCOAL_LIGHT = FLINT
SLATE          = PEWTER
OFF_WHITE      = LINEN
WARM_GRAY      = PARCHMENT
BORDER_LIGHT   = STONE
BORDER_MEDIUM  = STONE

ACCENT_PRIMARY   = FOREST
ACCENT_SECONDARY = CANOPY
ACCENT_MUTED     = GROVE
ACCENT_PALE      = FOREST_TINT

POSITIVE      = UNDER
POSITIVE_BG   = "#D4EDDA"   # light teal-green cell background
POSITIVE_TEXT = "#1A4731"   # dark teal-green cell text
NEGATIVE      = DOUBLE
NEGATIVE_BG   = "#F8DDD8"   # light rust cell background
NEGATIVE_TEXT = "#7B2A1C"   # dark rust cell text
NEUTRAL       = EVEN
WARNING       = GOLD
