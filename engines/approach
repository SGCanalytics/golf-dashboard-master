import pandas as pd

# ============================================================
# APPROACH ENGINE
# ============================================================

def approach_engine(filtered_df, num_rounds):
    """
    Compute all approach analytics for the Approach tab.

    Inputs:
        filtered_df: full shot-level dataframe (already filtered by player/date/etc.)
        num_rounds: number of rounds in the filtered dataset

    Returns:
        dict with:
            - num_approach_shots
            - total_sg
            - sg_per_round
            - bucket_sg (dict)
            - bucket_counts (dict)
            - green_hit_count
            - green_miss_count
            - penalty_count
    """

    # Filter to approach shots
    df = filtered_df[filtered_df['Shot Type'] == 'Approach'].copy()
    num_approach = len(df)

    if num_approach == 0:
        return {
            "num_approach_shots": 0,
            "total_sg": 0.0,
            "sg_per_round": 0.0,
            "bucket_sg": {},
            "bucket_counts": {},
            "green_hit_count": 0,
            "green_miss_count": 0,
            "penalty_count": 0
        }

    # -----------------------------
    # BASIC SG METRICS
    # -----------------------------
    total_sg = df['Strokes Gained'].sum()
    sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0

    # -----------------------------
    # GREEN HITS / MISSES
    # -----------------------------
    green_hit_count = len(df[df['Ending Location'] == 'Green'])
    green_miss_count = num_approach - green_hit_count

    # -----------------------------
    # PENALTIES
    # -----------------------------
    penalty_count = len(df[df['Penalty'] == 'Yes'])

    # -----------------------------
    # DISTANCE BUCKETS
    # -----------------------------
    # Buckets: 50–100, 100–150, 150–200, >200
    def bucket(d):
        if 50 <= d < 100:
            return "50–100"
        elif 100 <= d < 150:
            return "100–150"
        elif 150 <= d < 200:
            return "150–200"
        elif d >= 200:
            return ">200"
        return None

    df['Bucket'] = df['Starting Distance'].apply(bucket)

    bucket_sg = df.groupby('Bucket')['Strokes Gained'].sum().to_dict()
    bucket_counts = df['Bucket'].value_counts().to_dict()

    # -----------------------------
    # PACKAGE RESULTS
    # -----------------------------
    results = {
        "num_approach_shots": num_approach,
        "total_sg": total_sg,
        "sg_per_round": sg_per_round,
        "bucket_sg": bucket_sg,
        "bucket_counts": bucket_counts,
        "green_hit_count": green_hit_count,
        "green_miss_count": green_miss_count,
        "penalty_count": penalty_count
    }

    return results

