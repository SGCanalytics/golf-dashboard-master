import pandas as pd

# ============================================================
# OVERVIEW ENGINE
# ============================================================

def overview_engine(df, hole_summary, driving_results, approach_results,
                    short_game_results, putting_results, tiger5_results):
    """
    High‑level overview metrics for the Overview tab.

    Inputs:
        - df: full filtered shot-level dataframe
        - hole_summary: output of build_hole_summary()
        - driving_results: dict from driving_engine()
        - approach_results: dict from approach_engine()
        - short_game_results: dict from short_game_engine()
        - putting_results: dict from putting_hero_metrics()
        - tiger5_results: dict from calculate_tiger5()

    Returns:
        dict with:
            - total_sg
            - sg_by_category
            - scoring_average
            - best_round
            - worst_round
            - par_breakdown
            - tiger5_fails
    """

    # -----------------------------
    # TOTAL SG
    # -----------------------------
    total_sg = df['Strokes Gained'].sum()

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
    # TIGER 5 SUMMARY
    # -----------------------------
    tiger5_fails = {k: v['fails'] for k, v in tiger5_results.items()}

    # -----------------------------
    # PACKAGE RESULTS
    # -----------------------------
    return {
        "total_sg": total_sg,
        "sg_by_category": sg_by_category,
        "scoring_average": scoring_average,
        "best_round": best_round,
        "worst_round": worst_round,
        "par_breakdown": par_breakdown,
        "tiger5_fails": tiger5_fails
    }
