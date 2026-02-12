import pandas as pd
from ui.formatters import round_label, format_date

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

    # SG Other + Recovery (combined)
    other_recovery_shots = df[(df['Shot Type'] == 'Other') | (df['Shot Type'] == 'Recovery')]
    sg_other_recovery = other_recovery_shots['Strokes Gained'].sum() if not other_recovery_shots.empty else 0

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
        "sg_other_recovery": sg_other_recovery,
        "scoring_average": scoring_average,
        "best_round": best_round,
        "worst_round": worst_round,
        "par_breakdown": par_breakdown,
        "tiger5_fails": tiger5_fails
    }


# ============================================================
# SG SEPARATORS — GRANULAR BREAKDOWNS
# ============================================================

def build_sg_separators(df, num_rounds):
    """Calculate granular SG separator metrics with per-round values and best/worst identification."""
    if df.empty:
        return [], None, None

    start_dist = pd.to_numeric(df['Starting Distance'], errors='coerce')

    def _calc(mask):
        total = df.loc[mask, 'Strokes Gained'].sum()
        per_round = total / num_rounds if num_rounds > 0 else 0
        return total, per_round

    separators = []
    separator_dict = {}  # Track all totals for best/worst calculation

    # SG Putting 4-6 Feet (CHANGED from 3-6)
    m = (df['Shot Type'] == 'Putt') & (start_dist >= 4) & (start_dist <= 6)
    t, pr = _calc(m)
    key = 'putt_4_6'
    separators.append(('SG Putting 4–6ft', t, pr, key))
    separator_dict[key] = t

    # SG Putting 20+ Feet (CHANGED from 25+)
    m = (df['Shot Type'] == 'Putt') & (start_dist >= 20)
    t, pr = _calc(m)
    key = 'putt_20_plus'
    separators.append(('SG Putting 20+ft', t, pr, key))
    separator_dict[key] = t

    # SG Approach 100-150 yards
    m = (df['Shot Type'] == 'Approach') & (start_dist >= 100) & (start_dist <= 150)
    t, pr = _calc(m)
    key = 'app_100_150'
    separators.append(('SG Approach 100–150yd', t, pr, key))
    separator_dict[key] = t

    # SG Approach 150-200 yards
    m = (df['Shot Type'] == 'Approach') & (start_dist >= 150) & (start_dist <= 200)
    t, pr = _calc(m)
    key = 'app_150_200'
    separators.append(('SG Approach 150–200yd', t, pr, key))
    separator_dict[key] = t

    # SG Approach Rough <150 yards
    m = (df['Shot Type'] == 'Approach') & (df['Starting Location'] == 'Rough') & (start_dist < 150)
    t, pr = _calc(m)
    key = 'app_rough_150'
    separators.append(('SG Approach Rough <150yd', t, pr, key))
    separator_dict[key] = t

    # SG Playable Drives = drives ending in Fairway, Rough, or Sand
    m = (df['Shot Type'] == 'Driving') & (df['Ending Location'].isin(['Fairway', 'Rough', 'Sand']))
    t, pr = _calc(m)
    key = 'playable_drives'
    separators.append(('SG Playable Drives', t, pr, key))
    separator_dict[key] = t

    # SG Around the Green = Short Game with starting distance <= 25 yards
    m = (df['Shot Type'] == 'Short Game') & (start_dist <= 25)
    t, pr = _calc(m)
    key = 'around_green'
    separators.append(('SG Around the Green', t, pr, key))
    separator_dict[key] = t

    # Determine best and worst
    best_key = max(separator_dict, key=separator_dict.get) if separator_dict else None
    worst_key = min(separator_dict, key=separator_dict.get) if separator_dict else None

    return separators, best_key, worst_key


# ============================================================
# SG TREND BY ROUND
# ============================================================

def build_sg_trend(df):
    """Per-round SG breakdown by category for trend chart."""
    if df.empty:
        return pd.DataFrame()

    cat_map = {
        'Driving': 'Driving',
        'Approach': 'Approach',
        'Short Game': 'Short Game',
        'Putt': 'Putting',
        'Recovery': 'Other',
        'Other': 'Other'
    }

    df_copy = df.copy()
    df_copy['SG Category'] = df_copy['Shot Type'].map(cat_map).fillna('Other')

    round_info = df_copy.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    sg_by_round_cat = df_copy.groupby(
        ['Round ID', 'SG Category']
    )['Strokes Gained'].sum().reset_index()

    sg_pivot = sg_by_round_cat.pivot(
        index='Round ID', columns='SG Category', values='Strokes Gained'
    ).fillna(0).reset_index()

    trend = round_info.merge(sg_pivot, on='Round ID', how='left').fillna(0)
    trend['Date'] = pd.to_datetime(trend['Date'])
    trend = trend.sort_values('Date')
    trend['Label'] = trend.apply(
        lambda r: round_label(r['Date'], r['Course']), axis=1
    )

    for cat in ['Driving', 'Approach', 'Short Game', 'Putting']:
        if cat not in trend.columns:
            trend[cat] = 0.0

    return trend


# ============================================================
# SCORING AVERAGE & SG BY HOLE PAR
# ============================================================

def build_scoring_by_par(hole_summary):
    """Scoring average and SG by hole par."""
    if hole_summary.empty:
        return pd.DataFrame()

    by_par = hole_summary.groupby('Par').agg(
        Holes=('Hole Score', 'count'),
        Scoring_Avg=('Hole Score', 'mean'),
        Total_SG=('total_sg', 'sum'),
        SG_Per_Hole=('total_sg', 'mean')
    ).reset_index()

    by_par.columns = ['Par', 'Holes Played', 'Scoring Avg', 'Total SG', 'SG / Hole']
    by_par['Scoring Avg'] = by_par['Scoring Avg'].round(2)
    by_par['Total SG'] = by_par['Total SG'].round(2)
    by_par['SG / Hole'] = by_par['SG / Hole'].round(3)

    return by_par


# ============================================================
# HOLE OUTCOME DISTRIBUTION
# ============================================================

def build_hole_outcomes(hole_summary):
    """Count and percentage of each scoring outcome."""
    if hole_summary.empty:
        return pd.DataFrame()

    score_order = ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double or Worse']

    counts = hole_summary['Score Name'].value_counts()
    total = counts.sum()

    rows = []
    for name in score_order:
        c = int(counts.get(name, 0))
        rows.append({
            'Score': name,
            'Count': c,
            'Pct': round(c / total * 100, 1) if total > 0 else 0
        })

    return pd.DataFrame(rows)


# ============================================================
# HOLE-BY-HOLE SG PIVOT BY SHOT TYPE
# ============================================================

def build_sg_by_hole_pivot(df, hole_summary):
    """Hole-by-hole SG pivot table by shot type with Par and Score rows."""
    if df.empty:
        return pd.DataFrame()

    cat_map = {
        'Driving': 'Driving',
        'Approach': 'Approach',
        'Short Game': 'Short Game',
        'Putt': 'Putting',
        'Recovery': 'Other',
        'Other': 'Other'
    }

    df_copy = df.copy()
    df_copy['SG Category'] = df_copy['Shot Type'].map(cat_map).fillna('Other')

    pivot = df_copy.groupby(
        ['Hole', 'SG Category']
    )['Strokes Gained'].sum().reset_index()

    pivot_table = pivot.pivot(
        index='SG Category', columns='Hole', values='Strokes Gained'
    ).fillna(0)

    # Sort columns (holes) numerically
    pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)

    # Order shot type rows
    type_order = ['Driving', 'Approach', 'Short Game', 'Putting', 'Other']
    existing_types = [t for t in type_order if t in pivot_table.index]
    pivot_table = pivot_table.loc[existing_types]

    # Add Total SG row
    total_row = pivot_table.sum()
    total_row.name = 'Total SG'
    pivot_table = pd.concat([pivot_table, total_row.to_frame().T])

    # Add Total column (sum across all holes for each row)
    pivot_table['Total'] = pivot_table.sum(axis=1)

    # Add Hole Par and Hole Score rows from hole_summary
    if not hole_summary.empty:
        # Average par per hole (handles multiple rounds)
        par_by_hole = hole_summary.groupby('Hole')['Par'].mean()
        # Average score per hole (handles multiple rounds)
        score_by_hole = hole_summary.groupby('Hole')['Hole Score'].mean()

        # Create Hole Par row
        par_row = pd.Series(index=pivot_table.columns, dtype=float)
        for hole in pivot_table.columns:
            if hole == 'Total':
                par_row[hole] = par_by_hole.sum()
            elif hole in par_by_hole.index:
                par_row[hole] = par_by_hole[hole]
            else:
                par_row[hole] = 0
        par_row.name = 'Hole Par'

        # Create Hole Score row
        score_row = pd.Series(index=pivot_table.columns, dtype=float)
        for hole in pivot_table.columns:
            if hole == 'Total':
                score_row[hole] = score_by_hole.sum()
            elif hole in score_by_hole.index:
                score_row[hole] = score_by_hole[hole]
            else:
                score_row[hole] = 0
        score_row.name = 'Hole Score'

        # Insert at the top
        pivot_table = pd.concat([
            par_row.to_frame().T,
            score_row.to_frame().T,
            pivot_table
        ])

    pivot_table = pivot_table.round(2)

    # Clean up for display
    pivot_table.index.name = 'Shot Type'
    new_cols = []
    for c in pivot_table.columns:
        try:
            new_cols.append(int(c))
        except (ValueError, TypeError):
            new_cols.append(c)
    pivot_table.columns = new_cols
    pivot_table = pivot_table.reset_index()

    return pivot_table


# ============================================================
# TIGER 5 FAIL SHOT DETAILS
# ============================================================

def build_tiger5_fail_shots(df, tiger5_results):
    """Build shot-level detail for each Tiger 5 fail type."""
    fail_shots = {}

    tiger5_names = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']

    for stat_name in tiger5_names:
        detail = tiger5_results[stat_name]
        if detail['fails'] == 0:
            fail_shots[stat_name] = []
            continue

        detail_holes = detail['detail_holes']
        holes_list = []

        for _, row in detail_holes.iterrows():
            rid = row['Round ID']
            hole = row['Hole']
            date = row.get('Date', '')
            course = row.get('Course', '')

            hole_shots = df[
                (df['Round ID'] == rid) & (df['Hole'] == hole)
            ].copy()

            # Filter based on fail type
            if stat_name == '3 Putts':
                shots = hole_shots[hole_shots['Shot Type'] == 'Putt']
            elif stat_name in ['Double Bogey', 'Par 5 Bogey']:
                shots = hole_shots
            elif stat_name == 'Missed Green':
                shots = hole_shots[hole_shots['Shot Type'] == 'Short Game']
            elif stat_name == '125yd Bogey':
                shots = hole_shots[
                    hole_shots['Shot Type'].isin(['Approach', 'Short Game', 'Putt'])
                ]
            else:
                shots = hole_shots

            if not shots.empty:
                shots_data = shots[[
                    'Shot', 'Starting Location', 'Starting Distance',
                    'Ending Location', 'Ending Distance', 'Penalty',
                    'Strokes Gained'
                ]].copy()

                shots_data = shots_data.rename(columns={
                    'Shot': 'Shot #',
                    'Starting Location': 'Starting Lie',
                    'Starting Distance': 'Starting Dist',
                    'Ending Location': 'Ending Lie',
                    'Ending Distance': 'Ending Dist',
                })

                shots_data['Shot #'] = shots_data['Shot #'].astype(int)
                shots_data['Starting Dist'] = pd.to_numeric(
                    shots_data['Starting Dist'], errors='coerce'
                ).round(1)
                shots_data['Ending Dist'] = pd.to_numeric(
                    shots_data['Ending Dist'], errors='coerce'
                ).round(1)
                shots_data['Strokes Gained'] = pd.to_numeric(
                    shots_data['Strokes Gained'], errors='coerce'
                ).round(2)

                holes_list.append({
                    'date': format_date(pd.to_datetime(date)),
                    'course': course,
                    'hole': int(hole),
                    'shots': shots_data
                })

        fail_shots[stat_name] = holes_list

    return fail_shots


# ============================================================
# SHOT LEVEL DETAIL BY ROUND
# ============================================================

def build_shot_detail(df):
    """Shot-level detail for all shots, grouped by round."""
    if df.empty:
        return {}

    rounds = {}
    round_info = df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    round_info['Date'] = pd.to_datetime(round_info['Date'])
    round_info = round_info.sort_values('Date', ascending=False)

    for _, r in round_info.iterrows():
        rid = r['Round ID']
        label = f"{format_date(r['Date'])} - {r['Course']}"

        round_shots = df[df['Round ID'] == rid][[
            'Hole', 'Par', 'Shot', 'Starting Distance', 'Starting Location',
            'Ending Distance', 'Ending Location', 'Penalty', 'Strokes Gained'
        ]].copy()

        round_shots = round_shots.rename(columns={
            'Shot': 'Shot #',
            'Starting Location': 'Starting Lie',
            'Ending Location': 'Ending Lie'
        })

        round_shots['Hole'] = round_shots['Hole'].astype(int)
        round_shots['Par'] = round_shots['Par'].astype(int)
        round_shots['Shot #'] = round_shots['Shot #'].astype(int)
        round_shots['Starting Distance'] = pd.to_numeric(
            round_shots['Starting Distance'], errors='coerce'
        ).round(1)
        round_shots['Ending Distance'] = pd.to_numeric(
            round_shots['Ending Distance'], errors='coerce'
        ).round(1)
        round_shots['Strokes Gained'] = pd.to_numeric(
            round_shots['Strokes Gained'], errors='coerce'
        ).round(2)
        round_shots = round_shots.sort_values(['Hole', 'Shot #'])

        rounds[label] = round_shots

    return rounds
