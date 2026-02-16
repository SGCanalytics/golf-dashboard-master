# ============================================================
# HELPERS MODULE
# Shared logic used across multiple engines
# ============================================================

# ------------------------------------------------------------
# BUCKET CONSTANTS - CANONICAL DEFINITIONS
# ------------------------------------------------------------
SHORT_GAME_BUCKETS = ["<10", "10–20", "20–30", "30–40", "40–50"]
APPROACH_BUCKETS = ["50–100", "100–150", "150–200", ">200"]
ROUGH_BUCKETS = ["<150", ">150"]
ZONE_BUCKETS = ["Green Zone", "Yellow Zone", "Red Zone"]
LEAVE_BUCKETS = ["0–3", "4–6", "7–10", "10–20", "20+"]

ZONE_RANGES = {
    "Green Zone": "75-125",
    "Yellow Zone": "125-175",
    "Red Zone": "175-225"
}

LIE_ORDER = ["Fairway", "Rough", "Sand"]

# ------------------------------------------------------------
# SHORT GAME DISTANCE BUCKETS (0–50 yards)
# ------------------------------------------------------------
def sg_distance_bucket(dist):
    if dist < 10:
        return "<10"
    if dist < 20:
        return "10–20"
    if dist < 30:
        return "20–30"
    if dist < 40:
        return "30–40"
    return "40–50"

# ------------------------------------------------------------
# APPROACH DISTANCE BUCKETS (50-200+ yards)
# ------------------------------------------------------------
def approach_distance_bucket(dist):
    """Assign approach shot distance bucket (50-200+ yards)."""
    if 50 <= dist < 100:
        return "50–100"
    elif 100 <= dist < 150:
        return "100–150"
    elif 150 <= dist < 200:
        return "150–200"
    elif dist >= 200:
        return ">200"
    return None


# ------------------------------------------------------------
# ROUGH DISTANCE BUCKETS (<150 vs >150)
# ------------------------------------------------------------
def rough_distance_bucket(dist):
    """Assign rough-specific distance bucket."""
    if dist < 150:
        return "<150"
    return ">150"


# ------------------------------------------------------------
# ZONE BUCKETS (Green/Yellow/Red Zones: 75-225 yards)
# ------------------------------------------------------------
def zone_distance_bucket(dist):
    """
    Assign approach distance to performance zone.

    Zones:
    - Green Zone: 75-125 yards (short approach shots)
    - Yellow Zone: 125-175 yards (mid-range approach shots)
    - Red Zone: 175-225 yards (long approach shots)

    Returns None for distances outside 75-225 range.
    """
    if 75 <= dist < 125:
        return "Green Zone"
    elif 125 <= dist < 175:
        return "Yellow Zone"
    elif 175 <= dist < 225:
        return "Red Zone"
    return None


# ------------------------------------------------------------
# LEAVE DISTANCE BUCKETS (putting proximity: 0-20+ feet)
# ------------------------------------------------------------
def leave_distance_bucket(dist):
    """Bucket ending distance into leave-distance ranges (feet)."""
    if dist <= 3:
        return "0–3"
    if dist <= 6:
        return "4–6"
    if dist <= 10:
        return "7–10"
    if dist <= 20:
        return "10–20"
    return "20+"

# ------------------------------------------------------------
# SAFE DIVIDE
# ------------------------------------------------------------
def safe_divide(a, b):
    return a / b if b else 0
