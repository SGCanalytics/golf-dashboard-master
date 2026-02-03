import pandas as pd

# ============================================================
# OVERVIEW ENGINE
# ============================================================

def overview_engine(df, hole_summary, driving_results, approach_results,
                    short_game_results, putting_results, tiger5_results):
    """
    High-level overview metrics for the Overview tab.
    """

    # -----------------------------
    # TOTAL SG
    # -----------------------------
    total_sg = df['Strokes Gained'].sum()

    num_rounds = df['Round ID'].nunique()

    # -----------------------------
    # SG BY CATEGORY
    # -----------------------------
    sg_by_category = {
        "Driving": driving_results.get("driving_sg", 0),
        "Approach": approach_results.get("total_sg", 0),
        "Short Game": short_game_results.get("total_sg", 0),
        "Putting": putting_results.get("total_sg_putting", 0)
    }

    # -----------------------------
    # DERIVED SG METRICS
    # -----------------------------
    sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0

    sg_tee_to_green = (
        sg_by_category.get("Driving", 0) +
        sg_by_category.get("Approach", 0) +
        sg_by_category.get("Short Game", 0)
    )

    # SG putting from >= 30 ft
    putts_30_plus = df[(df['Shot Type'] == 'Putt') &
                       (pd.to_numeric(df['Starting Distance'], errors='coerce') >= 30)]
    sg_putts_over_30 = putts_30_plus['Strokes Gained'].sum() if not putts_30_plus.empty else 0

    # SG putting 5-10 ft
    start_dist = pd.to_numeric(df['Starting Distance'], errors='coerce')
    putts_5_10 = df[(df['Shot Type'] == 'Putt') & (start_dist >= 5) & (start_dist <= 10)]
    sg_putts_5_10 = putts_5_10['Strokes Gained'].sum() if not putts_5_10.empty else 0

    # -----------------------------
    # SCORING AVERAGE
    # -----------------------------
    scoring_average = hole_summary['Hole Score'].mean() if not hole_summary.empty else 0

    # -----------------------------
    # BEST / WORST ROUNDS
    # -----------------------------
    round_scores = hole_summary.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        Total=('Hole Score', 'sum')
    ).reset_index()

    best_round = None
    worst_round = None

    if not round_scores.empty:
        best_row = round_scores.loc[round_scores['Total'].idxmin()]
        worst_row = round_scores.loc[round_scores['Total'].idxmax()]

        best_round = {
            "round_id": best_row['Round ID'],
            "date": best_row['Date'],
            "course": best_row['Course'],
            "score": best_row['Total']
        }

        worst_round = {
            "round_id": worst_row['Round ID'],
            "date": worst_row['Date'],
            "course": worst_row['Course'],
            "score": worst_row['Total']
        }

    # -----------------------------
    # PAR BREAKDOWN (Birdie/Par/Bogey/etc.)
    # -----------------------------
    par_breakdown = hole_summary['Score Name'].value_counts().to_dict()

    # -----------------------------
    # TIGER 5 SUMMARY (filter to category dicts only)
    # -----------------------------
    tiger5_fails = {
        k: v['fails'] for k, v in tiger5_results.items()
        if isinstance(v, dict) and 'fails' in v
    }

    # -----------------------------
    # PACKAGE RESULTS
    # -----------------------------
    return {
        "total_sg": total_sg,
        "sg_per_round": sg_per_round,
        "sg_tee_to_green": sg_tee_to_green,
        "sg_putts_over_30": sg_putts_over_30,
        "sg_putts_5_10": sg_putts_5_10,
        "sg_by_category": sg_by_category,
        "scoring_average": scoring_average,
        "best_round": best_round,
        "worst_round": worst_round,
        "par_breakdown": par_breakdown,
        "tiger5_fails": tiger5_fails
    }
