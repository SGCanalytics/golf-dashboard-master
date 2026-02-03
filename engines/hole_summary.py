import pandas as pd

# ============================================================
# HOLE SUMMARY ENGINE — CENTRALIZED
# ============================================================

def score_to_name(hole_score, par):
    """Convert numeric score vs par into a label."""
    diff = hole_score - par
    if diff <= -2:
        return 'Eagle'
    elif diff == -1:
        return 'Birdie'
    elif diff == 0:
        return 'Par'
    elif diff == 1:
        return 'Bogey'
    return 'Double or Worse'


def build_hole_summary(filtered_df):
    """
    Compute per-hole summary used across multiple engines:
    - Tiger 5
    - Coach’s Corner
    - Round summaries
    - Scorecards
    - SG by hole
    """

    hole_summary = filtered_df.groupby(
        ['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par']
    ).agg(
        num_shots=('Shot', 'count'),
        num_penalties=('Penalty', lambda x: (x == 'Yes').sum()),
        num_putts=('Shot Type', lambda x: (x == 'Putt').sum()),
        total_sg=('Strokes Gained', 'sum')
    ).reset_index()

    # Hole score = shots + penalties
    hole_summary['Hole Score'] = (
        hole_summary['num_shots'] + hole_summary['num_penalties']
    )

    # Score name (Birdie, Par, Bogey, etc.)
    hole_summary['Score Name'] = hole_summary.apply(
        lambda row: score_to_name(row['Hole Score'], row['Par']),
        axis=1
    )

    return hole_summary
