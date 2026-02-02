import pandas as pd

# ============================================================
# COACH'S CORNER ENGINE
# ============================================================

def _strengths_from_sg(sg_dict):
    strengths = []
    for category, value in sg_dict.items():
        if value > 0.25:
            strengths.append(f"{category}: gaining strokes consistently")
        elif value > 0.10:
            strengths.append(f"{category}: slight positive trend")
    return strengths


def _weaknesses_from_sg(sg_dict):
    weaknesses = []
    for category, value in sg_dict.items():
        if value < -0.25:
            weaknesses.append(f"{category}: losing significant strokes")
        elif value < -0.10:
            weaknesses.append(f"{category}: slight negative trend")
    return weaknesses


def _practice_priorities(strengths, weaknesses, tiger5_fails):
    priorities = []

    # SG weaknesses
    for w in weaknesses:
        cat = w.split(":")[0]
        priorities.append(f"Focus on {cat.lower()} — trending negative in SG.")

    # Tiger 5
    if tiger5_fails.get("3 Putts", 0) > 0:
        priorities.append("Reduce 3-putts — improve lag putting and short-range consistency.")
    if tiger5_fails.get("Double Bogey", 0) > 0:
        priorities.append("Limit big numbers — improve decision-making and recovery shots.")
    if tiger5_fails.get("Par 5 Bogey", 0) > 0:
        priorities.append("Par 5 scoring — improve layup strategy and wedge control.")
    if tiger5_fails.get("Missed Green", 0) > 0:
        priorities.append("Short game reliability — improve contact and trajectory control.")
    if tiger5_fails.get("125yd Bogey", 0) > 0:
        priorities.append("Scoring clubs — tighten dispersion inside 125 yards.")

    return priorities


def _narrative_summary(strengths, weaknesses, priorities, grit_score):
    summary = []

    summary.append("Overall Performance:")
    if grit_score >= 80:
        summary.append(f"- Excellent grit score ({grit_score:.1f}%). You avoid big mistakes and stay composed.")
    elif grit_score >= 60:
        summary.append(f"- Solid grit score ({grit_score:.1f}%). Some room to tighten up mistakes.")
    else:
        summary.append(f"- Grit score ({grit_score:.1f}%) indicates opportunities to reduce costly errors.")

    if strengths:
        summary.append("\nStrengths:")
        for s in strengths:
            summary.append(f"- {s}")

    if weaknesses:
        summary.append("\nWeaknesses:")
        for w in weaknesses:
            summary.append(f"- {w}")

    if priorities:
        summary.append("\nPractice Priorities:")
        for p in priorities:
            summary.append(f"- {p}")

    return "\n".join(summary)


# ============================================================
# MASTER COACH'S CORNER ENGINE (RENAMED FOR APP.PY)
# ============================================================

def build_coachs_corner(
    driving_results,
    approach_results,
    short_game_results,
    putting_results,
    tiger5_results,
    grit_score
):
    """
    Combine all engines into a single coaching insight package.
    """

    # SG per round summary
    sg_summary = {
        "Driving": driving_results.get("driving_sg_per_round", 0),
        "Approach": approach_results.get("sg_per_round", 0),
        "Short Game": short_game_results.get("sg_per_round", 0),
        "Putting": putting_results.get("total_sg_putting", 0)
    }

    strengths = _strengths_from_sg(sg_summary)
    weaknesses = _weaknesses_from_sg(sg_summary)

    tiger5_fails = {k: v['fails'] for k, v in tiger5_results.items()}

    priorities = _practice_priorities(strengths, weaknesses, tiger5_fails)

    narrative = _narrative_summary(strengths, weaknesses, priorities, grit_score)

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "practice_priorities": priorities,
        "narrative_summary": narrative,
        "sg_summary": sg_summary,
        "tiger5_summary": tiger5_fails
    }
