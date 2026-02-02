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

        # Re-tee detection: more than one tee shot on same hole
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

    Inputs:
        filtered_df: full shot-level dataframe (already filtered by player/date/etc.)
        num_rounds: number of rounds in the filtered dataset

    Returns:
        dict with:
            - num_drives
            - driving_sg
            - driving_sg_per_round
            - fairway, rough, sand, recovery, green counts
            - penalty_count
            - ob_count
            - ob_details (DataFrame)
    """

    # Filter to driving shots
    df = filtered_df[filtered_df['Shot Type'] == 'Driving'].copy()
    num_drives = len(df)

    if num_drives == 0:
        return {
            "num_drives": 0,
            "driving_sg": 0.0,
            "driving_sg_per_round": 0.0,
            "fairway": 0,
            "rough": 0,
            "sand": 0,
            "recovery": 0,
            "green": 0,
            "penalty_count": 0,
            "ob_count": 0,
            "ob_details": pd.DataFrame()
        }

    # -----------------------------
    # BASIC SG METRICS
    # -----------------------------
    driving_sg = df['Strokes Gained'].sum()
    driving_sg_per_round = driving_sg / num_rounds if num_rounds > 0 else 0

    # -----------------------------
    # ENDING LOCATION COUNTS
    # -----------------------------
    end_loc_counts = df['Ending Location'].value_counts()
    fairway = end_loc_counts.get('Fairway', 0)
    rough = end_loc_counts.get('Rough', 0)
    sand = end_loc_counts.get('Sand', 0)
    recovery = end_loc_counts.get('Recovery', 0)
    green = end_loc_counts.get('Green', 0)

    # -----------------------------
    # PENALTIES
    # -----------------------------
    penalty_count = len(df[df['Penalty'] == 'Yes'])

    # -----------------------------
    # OB / RE-TEE DETECTION
    # -----------------------------
    ob_count, ob_details = _detect_ob_retee(filtered_df, df)

    # -----------------------------
    # PACKAGE RESULTS
    # -----------------------------
    results = {
        "num_drives": num_drives,
        "driving_sg": driving_sg,
        "driving_sg_per_round": driving_sg_per_round,
        "fairway": fairway,
        "rough": rough,
        "sand": sand,
        "recovery": recovery,
        "green": green,
        "penalty_count": penalty_count,
        "ob_count": ob_count,
        "ob_details": ob_details
    }

    return results
########################################
#AI Narative
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
    
    
