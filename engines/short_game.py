import pandas as pd

# ============================================================
# SHORT GAME ENGINE
# ============================================================

def short_game_engine(filtered_df, num_rounds):
    """
    Compute all short game analytics for the Short Game tab.

    Inputs:
        filtered_df: full shot-level dataframe (already filtered by player/date/etc.)
        num_rounds: number of rounds in the filtered dataset

    Returns:
        dict with:
            - num_short_game_shots
            - total_sg
            - sg_per_round
            - up_and_down_attempts
            - up_and_down_successes
            - up_and_down_pct
            - penalty_count
            - miss_locations (dict)
    """

    # Filter to short game shots
    df = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()
    num_sg = len(df)

    if num_sg == 0:
        return {
            "num_short_game_shots": 0,
            "total_sg": 0.0,
            "sg_per_round": 0.0,
            "up_and_down_attempts": 0,
            "up_and_down_successes": 0,
            "up_and_down_pct": "-",
            "penalty_count": 0,
            "miss_locations": {}
        }

    # -----------------------------
    # BASIC SG METRICS
    # -----------------------------
    total_sg = df['Strokes Gained'].sum()
    sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0

    # -----------------------------
    # UP & DOWN CALCULATION
    # -----------------------------
    # A short game shot is an "attempt" if it does NOT start on the green.
    # It is a "success" if the *next* shot ends in the hole (Ending Distance == 0).

    attempts = 0
    successes = 0

    for _, row in df.iterrows():
        attempts += 1

        # Find next shot on same hole
        next_shot = filtered_df[
            (filtered_df['Player'] == row['Player']) &
            (filtered_df['Round ID'] == row['Round ID']) &
            (filtered_df['Hole'] == row['Hole']) &
            (filtered_df['Shot'] == row['Shot'] + 1)
        ]

        if not next_shot.empty and next_shot.iloc[0]['Ending Distance'] == 0:
            successes += 1

    up_and_down_pct = (
        f"{successes / attempts * 100:.1f}%" if attempts > 0 else "-"
    )

    # -----------------------------
    # PENALTIES
    # -----------------------------
    penalty_count = len(df[df['Penalty'] == 'Yes'])

    # -----------------------------
    # MISS LOCATIONS
    # -----------------------------
    miss_locations = df['Ending Location'].value_counts().to_dict()

    # -----------------------------
    # PACKAGE RESULTS
    # -----------------------------
    results = {
        "num_short_game_shots": num_sg,
        "total_sg": total_sg,
        "sg_per_round": sg_per_round,
        "up_and_down_attempts": attempts,
        "up_and_down_successes": successes,
        "up_and_down_pct": up_and_down_pct,
        "penalty_count": penalty_count,
        "miss_locations": miss_locations
    }

    return results
#################################
# AI Narative
##############################
def short_game_narrative(results):
    sg = results.get("sg_per_round", 0)
    attempts = results.get("up_and_down_attempts", 0)
    successes = results.get("up_and_down_successes", 0)
    pct = results.get("up_and_down_pct", "-")
    penalties = results.get("penalty_count", 0)

    lines = ["Short Game Performance:"]

    if sg > 0.25:
        lines.append(f"- Strong short game, gaining {sg:.2f} strokes per round.")
    elif sg > 0:
        lines.append(f"- Slightly positive SG around the green at {sg:.2f}.")
    else:
        lines.append(f"- Losing strokes around the green ({sg:.2f}).")

    lines.append(f"- Up & Down: {successes}/{attempts} ({pct}).")

    if penalties > 0:
        lines.append(f"- {penalties} penalties from short game shots.")

    return "\n".join(lines)
