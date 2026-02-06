# ============================================================
# HELPERS MODULE
# Shared logic used across multiple engines
# ============================================================

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
# SAFE DIVIDE
# ------------------------------------------------------------
def safe_divide(a, b):
    return a / b if b else 0
