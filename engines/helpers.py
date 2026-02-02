# ============================================================
# HELPERS MODULE
# Shared logic used across multiple engines
# ============================================================

# ------------------------------------------------------------
# SCORE → NAME
# ------------------------------------------------------------
def score_to_name(score, par):
    diff = score - par
    if diff <= -2:
        return "Eagle or Better"
    if diff == -1:
        return "Birdie"
    if diff == 0:
        return "Par"
    if diff == 1:
        return "Bogey"
    if diff == 2:
        return "Double Bogey"
    return "Triple+"

# ------------------------------------------------------------
# NORMALIZE LIE TYPE
# ------------------------------------------------------------
def normalize_lie(lie):
    if not isinstance(lie, str):
        return "Unknown"

    lie = lie.strip().lower()

    mapping = {
        "fairway": "Fairway",
        "fw": "Fairway",
        "first cut": "Rough",
        "rough": "Rough",
        "rf": "Rough",
        "fringe": "Rough",
        "sand": "Sand",
        "bunker": "Sand",
        "trap": "Sand",
        "recovery": "Recovery",
        "trees": "Recovery",
        "punchout": "Recovery",
        "green": "Green",
        "putting green": "Green",
        "tee": "Tee",
        "tee box": "Tee"
    }

    return mapping.get(lie, "Unknown")

# ------------------------------------------------------------
# DETERMINE SHOT TYPE (if needed)
# ------------------------------------------------------------
def determine_shot_type(row):
    dist = row.get("Starting Distance", 0)
    loc = row.get("Starting Location", "")

    if loc == "Tee":
        return "Driving"
    if dist > 50:
        return "Approach"
    if dist <= 50 and loc != "Green":
        return "Short Game"
    return "Putt"

# ------------------------------------------------------------
# DISTANCE BUCKETS
# ------------------------------------------------------------
def bucket_distance(dist):
    if dist < 50:
        return "<50"
    if dist < 100:
        return "50–100"
    if dist < 150:
        return "100–150"
    if dist < 200:
        return "150–200"
    return "200+"

# ------------------------------------------------------------
# SAFE DIVIDE
# ------------------------------------------------------------
def safe_divide(a, b):
    return a / b if b else 0
