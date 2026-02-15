import pandas as pd
import numpy as np
from ui.formatters import round_label

# ============================================================
# DRIVING ENGINE
# ============================================================

def _detect_ob_retee(filtered_df, driving_df):
    """
    Detect OB / re-tee patterns:
    - Look at each hole where there is a drive
    - If Shot 1 starts on Tee, and a later shot also starts on Tee on same hole,
      count that as an OB / re-tee event.
    Returns:
        ob_count (int), ob_details (DataFrame)
    """
    ob_count = 0
    ob_rows = []

    drive_holes = driving_df[['Player', 'Round ID', 'Hole', 'Course', 'Date']].drop_duplicates()

    for _, row in drive_holes.iterrows():
        hole_shots = filtered_df[
            (filtered_df['Player'] == row['Player']) &
            (filtered_df['Round ID'] == row['Round ID']) &
            (filtered_df['Hole'] == row['Hole'])
        ].sort_values('Shot')

        tee_shots = hole_shots[hole_shots['Starting Location'] == 'Tee']
        if len(tee_shots) >= 2:
            ob_count += 1
            ob_rows.append({
                'Player': row['Player'],
                'Round ID': row['Round ID'],
                'Date': row['Date'],
                'Course': row['Course'],
                'Hole': row['Hole']
            })

    ob_details = pd.DataFrame(ob_rows)
    return ob_count, ob_details


def build_driving_results(filtered_df, num_rounds, hole_summary):
    """
    Compute all driving analytics for the Driving tab.
    """

    df = filtered_df[filtered_df['Shot Type'] == 'Driving'].copy()
    num_drives = len(df)

    empty_trend = pd.DataFrame(columns=['Label', 'SG', 'Fairway %'])
    empty_sg_by_result = pd.DataFrame(columns=['Result', 'Count', 'Total SG'])

    empty_results = {
        "num_drives": 0,
        "driving_sg": 0.0,
        "driving_sg_per_round": 0.0,
        "fairway": 0, "rough": 0, "sand": 0, "recovery": 0, "green": 0,
        "fairway_pct": 0.0,
        # Non-playable
        "non_playable_count": 0,
        "non_playable_pct": 0.0,
        # Playable SG
        "sg_playable": 0.0,
        "sg_playable_per_round": 0.0,
        # Driving distance
        "driving_distance_p90": 0.0,
        # Penalties + OB
        "penalty_count": 0,
        "penalty_sg": 0.0,
        "ob_count": 0,
        "ob_sg": 0.0,
        "ob_details": pd.DataFrame(),
        # Obstruction
        "obstruction_count": 0,
        "obstruction_pct": 0.0,
        "obstruction_sg": 0.0,
        # Avoidable loss
        "avoidable_loss_count": 0,
        "avoidable_loss_pct": 0.0,
        "avoidable_loss_sg": 0.0,
        # Consistency
        "sg_std": 0.0,
        "positive_sg_pct": 0.0,
        "positive_sg_total": 0.0,
        "poor_drive_pct": 0.0,
        "poor_drive_sg": 0.0,
        # Scoring impacts
        "trouble_to_bogey_attempts": 0,
        "trouble_to_bogey_fails": 0,
        "trouble_to_bogey_pct": 0.0,
        "double_penalty_attempts": 0,
        "double_penalty_fails": 0,
        "double_penalty_pct": 0.0,
        "avg_score_by_end_loc": pd.DataFrame(columns=['Ending Location', 'Avg vs Par']),
        # SG by result
        "sg_by_result": empty_sg_by_result,
        "trend": empty_trend,
        "df": pd.DataFrame()
    }

    if num_drives == 0:
        return empty_results

    # --- Basic SG ---
    driving_sg = df['Strokes Gained'].sum()
    driving_sg_per_round = driving_sg / num_rounds if num_rounds > 0 else 0

    # --- Ending location counts ---
    end_loc_counts = df['Ending Location'].value_counts()
    fairway = int(end_loc_counts.get('Fairway', 0))
    rough = int(end_loc_counts.get('Rough', 0))
    sand = int(end_loc_counts.get('Sand', 0))
    recovery = int(end_loc_counts.get('Recovery', 0))
    green = int(end_loc_counts.get('Green', 0))

    # --- Derived percentages ---
    fairway_pct = fairway / num_drives * 100

    # --- Non-playable rate ---
    non_playable_mask = (
        df['Ending Location'].isin(['Recovery', 'Sand']) |
        (df['Penalty'] == 'Yes')
    )
    non_playable_count = int(non_playable_mask.sum())
    non_playable_pct = non_playable_count / num_drives * 100

    # --- SG Playable Drives (Fairway or Rough, no penalty) ---
    playable_mask = (
        df['Ending Location'].isin(['Fairway', 'Rough']) &
        (df['Penalty'] != 'Yes')
    )
    sg_playable = df.loc[playable_mask, 'Strokes Gained'].sum()
    sg_playable_per_round = sg_playable / num_rounds if num_rounds > 0 else 0

    # --- Driving Distance (P90) ---
    valid_distance_mask = (df['Penalty'] != 'Yes')
    calc_distances = (
        df.loc[valid_distance_mask, 'Starting Distance'] -
        df.loc[valid_distance_mask, 'Ending Distance']
    )
    driving_distance_p90 = float(np.percentile(calc_distances, 90)) if len(calc_distances) > 0 else 0.0

    # --- Penalties + OB ---
    ob_count, ob_details = _detect_ob_retee(filtered_df, df)

    # OB drives: identify by holes with re-tee; take the first tee shot per OB hole
    ob_sg = 0.0
    if ob_count > 0 and not ob_details.empty:
        for _, ob_row in ob_details.iterrows():
            ob_hole_drives = df[
                (df['Player'] == ob_row['Player']) &
                (df['Round ID'] == ob_row['Round ID']) &
                (df['Hole'] == ob_row['Hole'])
            ]
            ob_sg += ob_hole_drives['Strokes Gained'].sum()

    # Non-OB penalties
    if ob_count > 0 and not ob_details.empty:
        ob_keys = set(
            ob_details.apply(
                lambda r: (r['Player'], r['Round ID'], r['Hole']), axis=1
            )
        )
        penalty_mask = (df['Penalty'] == 'Yes')
        non_ob_penalty_mask = penalty_mask & ~df.apply(
            lambda r: (r['Player'], r['Round ID'], r['Hole']) in ob_keys, axis=1
        )
    else:
        non_ob_penalty_mask = (df['Penalty'] == 'Yes')

    penalty_count = int(non_ob_penalty_mask.sum())
    penalty_sg = df.loc[non_ob_penalty_mask, 'Strokes Gained'].sum()

    # Build penalty details DataFrame (excluding OB)
    penalty_details = pd.DataFrame()
    if penalty_count > 0:
        penalty_details = df[non_ob_penalty_mask][[
            'Player', 'Date', 'Course', 'Hole',
            'Starting Distance', 'Ending Location', 'Strokes Gained'
        ]].copy()

    # --- Obstruction rate ---
    obstruction_mask = df['Ending Location'].isin(['Sand', 'Recovery'])
    obstruction_count = int(obstruction_mask.sum())
    obstruction_pct = obstruction_count / num_drives * 100
    obstruction_sg = df.loc[obstruction_mask, 'Strokes Gained'].sum()

    # --- Avoidable Loss ---
    avoidable_mask = (
        (df['Strokes Gained'] <= -0.25) &
        df['Ending Location'].isin(['Fairway', 'Rough', 'Sand']) &
        (df['Penalty'] != 'Yes')
    )
    avoidable_loss_count = int(avoidable_mask.sum())
    avoidable_loss_pct = avoidable_loss_count / num_drives * 100
    avoidable_loss_sg = df.loc[avoidable_mask, 'Strokes Gained'].sum()

    # --- Driving Consistency ---
    sg_std = df['Strokes Gained'].std() if num_drives > 1 else 0.0

    positive_sg_mask = df['Strokes Gained'] >= 0
    positive_sg_count = int(positive_sg_mask.sum())
    positive_sg_pct = positive_sg_count / num_drives * 100
    positive_sg_total = df.loc[positive_sg_mask, 'Strokes Gained'].sum()

    poor_mask = df['Strokes Gained'] <= -0.15
    poor_drive_count = int(poor_mask.sum())
    poor_drive_pct = poor_drive_count / num_drives * 100
    poor_drive_sg = df.loc[poor_mask, 'Strokes Gained'].sum()

    # --- Scoring Impacts ---
    # Build a mapping: (Player, Round ID, Hole) → drive ending location
    drive_end_map = df.groupby(['Player', 'Round ID', 'Hole'])['Ending Location'].first()

    # Trouble to Bogey: drives ending in Recovery → bogey or worse rate
    recovery_drives = df[df['Ending Location'] == 'Recovery'][
        ['Player', 'Round ID', 'Hole']
    ].drop_duplicates()
    trouble_to_bogey_attempts = len(recovery_drives)
    trouble_to_bogey_fails = 0

    if trouble_to_bogey_attempts > 0 and not hole_summary.empty:
        for _, rd in recovery_drives.iterrows():
            hole_row = hole_summary[
                (hole_summary['Player'] == rd['Player']) &
                (hole_summary['Round ID'] == rd['Round ID']) &
                (hole_summary['Hole'] == rd['Hole'])
            ]
            if not hole_row.empty:
                h = hole_row.iloc[0]
                if h['Hole Score'] >= h['Par'] + 1:
                    trouble_to_bogey_fails += 1

    trouble_to_bogey_pct = (
        trouble_to_bogey_fails / trouble_to_bogey_attempts * 100
        if trouble_to_bogey_attempts > 0 else 0.0
    )

    # Double+ rate on penalty holes (excluding OB)
    penalty_drives = df[non_ob_penalty_mask][
        ['Player', 'Round ID', 'Hole']
    ].drop_duplicates()
    double_penalty_attempts = len(penalty_drives)
    double_penalty_fails = 0

    if double_penalty_attempts > 0 and not hole_summary.empty:
        for _, pd_row in penalty_drives.iterrows():
            hole_row = hole_summary[
                (hole_summary['Player'] == pd_row['Player']) &
                (hole_summary['Round ID'] == pd_row['Round ID']) &
                (hole_summary['Hole'] == pd_row['Hole'])
            ]
            if not hole_row.empty:
                h = hole_row.iloc[0]
                if h['Hole Score'] >= h['Par'] + 2:
                    double_penalty_fails += 1

    double_penalty_pct = (
        double_penalty_fails / double_penalty_attempts * 100
        if double_penalty_attempts > 0 else 0.0
    )

    # Average score by drive ending location vs par
    avg_score_rows = []
    if not hole_summary.empty:
        for loc in ['Fairway', 'Rough', 'Sand', 'Recovery']:
            loc_drives = df[df['Ending Location'] == loc][
                ['Player', 'Round ID', 'Hole']
            ].drop_duplicates()
            if len(loc_drives) == 0:
                continue
            merged = loc_drives.merge(
                hole_summary[['Player', 'Round ID', 'Hole', 'Hole Score', 'Par']],
                on=['Player', 'Round ID', 'Hole'],
                how='inner'
            )
            if not merged.empty:
                avg_vs_par = (merged['Hole Score'] - merged['Par']).mean()
                avg_score_rows.append({
                    'Ending Location': loc,
                    'Avg vs Par': avg_vs_par
                })

    avg_score_by_end_loc = pd.DataFrame(avg_score_rows) if avg_score_rows else pd.DataFrame(
        columns=['Ending Location', 'Avg vs Par']
    )

    # --- SG by ending location result ---
    sg_by_result = df.groupby('Ending Location').agg(
        Count=('Strokes Gained', 'count'),
        **{'Total SG': ('Strokes Gained', 'sum')}
    ).reset_index()
    sg_by_result.columns = ['Result', 'Count', 'Total SG']

    # --- Trend by round ---
    round_trend = df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        SG=('Strokes Gained', 'sum'),
        Fairway_Count=('Ending Location', lambda x: (x == 'Fairway').sum()),
        Total_Drives=('Strokes Gained', 'count')
    ).reset_index()
    round_trend['Date'] = pd.to_datetime(round_trend['Date'])
    round_trend = round_trend.sort_values('Date')
    round_trend['Fairway %'] = round_trend['Fairway_Count'] / round_trend['Total_Drives'] * 100
    round_trend['Label'] = round_trend.apply(
        lambda r: round_label(r['Date'], r['Course']), axis=1
    )

    return {
        "num_drives": num_drives,
        "driving_sg": driving_sg,
        "driving_sg_per_round": driving_sg_per_round,
        "fairway": fairway,
        "rough": rough,
        "sand": sand,
        "recovery": recovery,
        "green": green,
        "fairway_pct": fairway_pct,
        # Non-playable
        "non_playable_count": non_playable_count,
        "non_playable_pct": non_playable_pct,
        # Playable SG
        "sg_playable": sg_playable,
        "sg_playable_per_round": sg_playable_per_round,
        # Driving distance
        "driving_distance_p90": driving_distance_p90,
        # Penalties + OB
        "penalty_count": penalty_count,
        "penalty_sg": penalty_sg,
        "ob_count": ob_count,
        "ob_sg": ob_sg,
        "ob_details": ob_details,
        "penalty_details": penalty_details,
        # Obstruction
        "obstruction_count": obstruction_count,
        "obstruction_pct": obstruction_pct,
        "obstruction_sg": obstruction_sg,
        # Avoidable loss
        "avoidable_loss_count": avoidable_loss_count,
        "avoidable_loss_pct": avoidable_loss_pct,
        "avoidable_loss_sg": avoidable_loss_sg,
        # Consistency
        "sg_std": sg_std,
        "positive_sg_pct": positive_sg_pct,
        "positive_sg_total": positive_sg_total,
        "poor_drive_pct": poor_drive_pct,
        "poor_drive_sg": poor_drive_sg,
        # Scoring impacts
        "trouble_to_bogey_attempts": trouble_to_bogey_attempts,
        "trouble_to_bogey_fails": trouble_to_bogey_fails,
        "trouble_to_bogey_pct": trouble_to_bogey_pct,
        "double_penalty_attempts": double_penalty_attempts,
        "double_penalty_fails": double_penalty_fails,
        "double_penalty_pct": double_penalty_pct,
        "avg_score_by_end_loc": avg_score_by_end_loc,
        # SG by result & trend
        "sg_by_result": sg_by_result,
        "trend": round_trend,
        "df": df
    }
