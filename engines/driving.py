import pandas as pd

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


def build_driving_results(filtered_df, num_rounds):
    """
    Compute all driving analytics for the Driving tab.
    """

    df = filtered_df[filtered_df['Shot Type'] == 'Driving'].copy()
    num_drives = len(df)

    empty_results = {
        "num_drives": 0,
        "driving_sg": 0.0,
        "driving_sg_per_round": 0.0,
        "fairway": 0, "rough": 0, "sand": 0, "recovery": 0, "green": 0,
        "fairway_pct": 0.0,
        "obstruction_count": 0,
        "obstruction_pct": 0.0,
        "penalty_count": 0,
        "ob_count": 0,
        "ob_details": pd.DataFrame(),
        "penalty_total": 0,
        "penalty_rate_pct": 0.0,
        "sg_by_result": pd.DataFrame(columns=['Result', 'Count', 'Total SG']),
        "trend": pd.DataFrame(columns=['Label', 'SG', 'Fairway %']),
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
    obstruction_count = sand + recovery
    obstruction_pct = obstruction_count / num_drives * 100

    # --- Penalties + OB ---
    penalty_count = int((df['Penalty'] == 'Yes').sum())
    ob_count, ob_details = _detect_ob_retee(filtered_df, df)
    penalty_total = penalty_count + ob_count
    penalty_rate_pct = penalty_total / num_drives * 100

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
        lambda r: f"{r['Date'].strftime('%m/%d')} {r['Course']}", axis=1
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
        "obstruction_count": obstruction_count,
        "obstruction_pct": obstruction_pct,
        "penalty_count": penalty_count,
        "ob_count": ob_count,
        "ob_details": ob_details,
        "penalty_total": penalty_total,
        "penalty_rate_pct": penalty_rate_pct,
        "sg_by_result": sg_by_result,
        "trend": round_trend,
        "df": df
    }


########################################
# AI Narrative
######################################
def driving_narrative(results):
    sg = results.get("driving_sg_per_round", 0)
    fairway = results.get("fairway", 0)
    rough = results.get("rough", 0)
    ob = results.get("ob_count", 0)
    penalties = results.get("penalty_count", 0)

    lines = ["Driving Performance:"]

    if sg > 0.25:
        lines.append(f"- Strong off the tee, gaining {sg:.2f} strokes per round.")
    elif sg > 0:
        lines.append(f"- Slightly positive SG off the tee at {sg:.2f} per round.")
    else:
        lines.append(f"- Losing strokes off the tee ({sg:.2f} per round).")

    lines.append(f"- Fairway hits: {fairway}, Rough: {rough}.")

    if ob > 0:
        lines.append(f"- {ob} OB/re-tee events — these are costing strokes.")
    if penalties > 0:
        lines.append(f"- {penalties} penalties from tee shots.")

    return "\n".join(lines)
