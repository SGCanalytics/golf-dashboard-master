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
