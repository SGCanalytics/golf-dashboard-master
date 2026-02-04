import os
import pandas as pd
import numpy as np

# ============================================================
# STROKES GAINED ENGINE — BENCHMARK-BASED SG CALCULATOR
# ============================================================

BENCHMARK_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'benchmarks')

BENCHMARK_FILES = {
    'PGA Tour': 'pga_tour.csv',
    'Elite College (+3)': 'elite_college.csv',
    'Competitive Scratch (0)': 'competitive_scratch.csv',
}

# Map raw data location names to benchmark column names
LOCATION_TO_COLUMN = {
    'Tee': 'Tee',
    'Fairway': 'Fairway',
    'Rough': 'Rough',
    'Sand': 'Sand',
    'Recovery': 'Recovery',
    'Green': 'Putt',
}


def load_benchmark(benchmark_name):
    """
    Load a benchmark CSV into a dict-of-dicts for fast lookup.

    Returns:
        lookup: dict  {column_name: {distance_int: expected_strokes_float}}
    """
    filename = BENCHMARK_FILES.get(benchmark_name)
    if filename is None:
        raise ValueError(f"Unknown benchmark: {benchmark_name}")

    path = os.path.join(BENCHMARK_DIR, filename)
    df = pd.read_csv(path)

    columns = ['Tee', 'Fairway', 'Rough', 'Sand', 'Recovery', 'Putt']
    lookup = {}

    for col in columns:
        series = pd.to_numeric(df[col], errors='coerce')
        col_dict = {}
        for dist, val in zip(df['Distance'].astype(int), series):
            if not np.isnan(val):
                col_dict[int(dist)] = float(val)
        lookup[col] = col_dict

    return lookup


def expected_strokes(lookup, location, distance):
    """
    Look up expected strokes to hole out from a given lie and distance.

    Args:
        lookup: benchmark dict from load_benchmark()
        location: raw data location string (e.g. 'Fairway', 'Green')
        distance: numeric distance in yards (or feet for putts)

    Returns:
        float or None if lookup not possible
    """
    # Holed out
    if distance is not None and distance <= 0:
        return 0.0

    col = LOCATION_TO_COLUMN.get(location)
    if col is None:
        return None

    col_dict = lookup.get(col)
    if col_dict is None:
        return None

    # Round distance to nearest integer, clamp to 0-600
    if distance is None:
        return None

    dist_int = max(0, min(600, round(float(distance))))

    return col_dict.get(dist_int)


def calculate_sg_for_shot(lookup, start_location, start_distance,
                          end_location, end_distance, penalty):
    """
    Calculate Strokes Gained for a single shot.

    SG = Expected(start) - Expected(end) - strokes_consumed
    strokes_consumed = 1 for normal shot, 2 for shot + penalty

    Returns:
        float or None if calculation not possible
    """
    exp_start = expected_strokes(lookup, start_location, start_distance)
    if exp_start is None:
        return None

    # Determine end expected strokes
    if end_distance is not None and float(end_distance) <= 0:
        exp_end = 0.0
    else:
        exp_end = expected_strokes(lookup, end_location, end_distance)

    if exp_end is None:
        return None

    # Penalty: 'Yes' means 1 extra stroke consumed
    penalty_strokes = 1 if str(penalty).strip().lower() == 'yes' else 0

    sg = exp_start - exp_end - 1 - penalty_strokes
    return round(sg, 4)


def apply_benchmark_sg(df, benchmark_name):
    """
    Recalculate the 'Strokes Gained' column for the entire DataFrame
    using the selected benchmark.

    Args:
        df: DataFrame with columns Starting Location, Starting Distance,
            Ending Location, Ending Distance, Penalty
        benchmark_name: one of the keys in BENCHMARK_FILES

    Returns:
        DataFrame with updated 'Strokes Gained' column
    """
    lookup = load_benchmark(benchmark_name)

    df = df.copy()

    start_dist = pd.to_numeric(df['Starting Distance'], errors='coerce')
    end_dist = pd.to_numeric(df['Ending Distance'], errors='coerce')

    new_sg = []
    for idx in df.index:
        sg = calculate_sg_for_shot(
            lookup,
            df.at[idx, 'Starting Location'],
            start_dist.at[idx],
            df.at[idx, 'Ending Location'],
            end_dist.at[idx],
            df.at[idx, 'Penalty']
        )
        new_sg.append(sg)

    calculated = pd.Series(new_sg, index=df.index, dtype=float)

    # Use calculated SG where possible, fall back to original
    original_sg = pd.to_numeric(df['Strokes Gained'], errors='coerce')
    df['Strokes Gained'] = calculated.fillna(original_sg)

    return df
