import pandas as pd

# ============================================================
# SCORING PERFORMANCE ENGINE
# ============================================================

def categorize_holes(hole_summary, filtered_df):
    """
    Identifies which holes belong to each of the three analysis categories:
    - Double Bogey+: score >= par + 2
    - Bogey: score == par + 1
    - Underperformance: score <= par AND (has 3-putt OR short game miss)

    Returns:
        dict with keys: 'double_bogey_plus', 'bogey', 'underperformance'
        Each value is a list of (round_id, hole) tuples
    """
    categorized = {
        'double_bogey_plus': [],
        'bogey': [],
        'underperformance': []
    }

    # Double Bogey+
    db_plus = hole_summary[hole_summary['Hole Score'] >= hole_summary['Par'] + 2]
    categorized['double_bogey_plus'] = list(zip(db_plus['Round ID'], db_plus['Hole']))

    # Bogey
    bogey = hole_summary[hole_summary['Hole Score'] == hole_summary['Par'] + 1]
    categorized['bogey'] = list(zip(bogey['Round ID'], bogey['Hole']))

    # Underperformance: par or better with 3-putt OR short game miss
    par_or_better = hole_summary[hole_summary['Hole Score'] <= hole_summary['Par']].copy()

    underperf_holes = []
    for _, row in par_or_better.iterrows():
        rid = row['Round ID']
        hole = row['Hole']

        # Check for 3-putt
        has_three_putt = row['num_putts'] >= 3

        # Check for short game miss
        has_sg_miss = False
        hole_shots = filtered_df[
            (filtered_df['Round ID'] == rid) &
            (filtered_df['Hole'] == hole) &
            (filtered_df['Shot Type'] == 'Short Game')
        ]
        if not hole_shots.empty:
            has_sg_miss = (hole_shots['Ending Location'] != 'Green').any()

        if has_three_putt or has_sg_miss:
            underperf_holes.append((rid, hole))

    categorized['underperformance'] = underperf_holes

    return categorized


def find_worst_shot(hole_shots_df):
    """
    Finds the shot with the worst (most negative) Strokes Gained for a hole.

    Returns:
        The worst shot row (pandas Series)
    """
    if hole_shots_df.empty:
        return None

    sg_numeric = pd.to_numeric(hole_shots_df['Strokes Gained'], errors='coerce')
    worst_idx = sg_numeric.idxmin()
    return hole_shots_df.loc[worst_idx]


def categorize_shot(shot_row):
    """
    Maps a shot to one of six root cause categories.

    Returns:
        String category name
    """
    shot_type = shot_row['Shot Type']
    starting_dist = pd.to_numeric(shot_row['Starting Distance'], errors='coerce')

    if shot_type == 'Putt':
        if pd.notna(starting_dist) and starting_dist <= 10:
            return 'Short Putts'
        else:
            return 'Lag Putts'  # >10 feet or unknown distance
    elif shot_type == 'Driving':
        return 'Driving'
    elif shot_type == 'Approach':
        return 'Approach'
    elif shot_type == 'Short Game':
        return 'Short Game'
    else:
        return 'Recovery and Other'


def analyze_category(filtered_df, hole_summary, hole_list, category_name):
    """
    Analyzes all holes in a category to determine root causes.

    Returns:
        dict with keys:
        - 'holes': list of hole metadata dicts
        - 'counts': dict mapping root_cause -> count
    """
    holes_data = []
    counts = {
        'Short Putts': 0,
        'Lag Putts': 0,
        'Driving': 0,
        'Approach': 0,
        'Short Game': 0,
        'Recovery and Other': 0
    }

    for rid, hole_num in hole_list:
        # Get hole metadata
        hole_info = hole_summary[
            (hole_summary['Round ID'] == rid) &
            (hole_summary['Hole'] == hole_num)
        ]

        if hole_info.empty:
            continue

        hole_row = hole_info.iloc[0]

        # Get all shots for this hole
        hole_shots = filtered_df[
            (filtered_df['Round ID'] == rid) &
            (filtered_df['Hole'] == hole_num)
        ].copy()

        if hole_shots.empty:
            continue

        # Find worst shot
        worst_shot = find_worst_shot(hole_shots)
        if worst_shot is None:
            continue

        # Categorize the worst shot
        root_cause = categorize_shot(worst_shot)

        # Get worst SG value
        worst_sg = pd.to_numeric(worst_shot['Strokes Gained'], errors='coerce')
        if pd.isna(worst_sg):
            worst_sg = 0.0

        # Store hole data
        holes_data.append({
            'round_id': rid,
            'hole': hole_num,
            'date': hole_row.get('Date', ''),
            'course': hole_row.get('Course', ''),
            'par': hole_row['Par'],
            'score': hole_row['Hole Score'],
            'root_cause': root_cause,
            'worst_sg': float(worst_sg)
        })

        # Increment count
        counts[root_cause] += 1

    return {
        'holes': holes_data,
        'counts': counts
    }


def aggregate_by_round(filtered_df, all_analyzed_holes):
    """
    Creates round-by-round breakdown for trend chart.

    Returns:
        DataFrame with columns for each root cause category + Total Fails
    """
    # Get unique rounds
    round_info = filtered_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    rows = []

    for _, r in round_info.iterrows():
        rid = r['Round ID']
        date_obj = pd.to_datetime(r['Date'])
        label = f"{date_obj.strftime('%m/%d/%y')} {r['Course']}"

        # Count root causes for this round
        round_counts = {
            'Short Putts': 0,
            'Lag Putts': 0,
            'Driving': 0,
            'Approach': 0,
            'Short Game': 0,
            'Recovery and Other': 0
        }

        for hole_data in all_analyzed_holes:
            if hole_data['round_id'] == rid:
                rc = hole_data['root_cause']
                round_counts[rc] += 1

        rows.append({
            'Round ID': rid,
            'Date': date_obj,
            'Course': r['Course'],
            'Label': label,
            'Short Putts': round_counts['Short Putts'],
            'Lag Putts': round_counts['Lag Putts'],
            'Driving': round_counts['Driving'],
            'Approach': round_counts['Approach'],
            'Short Game': round_counts['Short Game'],
            'Recovery and Other': round_counts['Recovery and Other']
        })

    by_round_df = pd.DataFrame(rows)

    if not by_round_df.empty:
        by_round_df = by_round_df.sort_values('Date')
        by_round_df['Total Fails'] = (
            by_round_df['Short Putts'] +
            by_round_df['Lag Putts'] +
            by_round_df['Driving'] +
            by_round_df['Approach'] +
            by_round_df['Short Game'] +
            by_round_df['Recovery and Other']
        )

    return by_round_df


def calculate_penalty_stats(filtered_df, hole_summary, categorized_holes):
    """
    Calculates penalty-related statistics.

    Returns:
        dict with keys: bogey_penalty_pct, db_penalty_pct, db_multiple_bad_pct
    """
    stats = {
        'bogey_penalty_pct': 0.0,
        'db_penalty_pct': 0.0,
        'db_multiple_bad_pct': 0.0
    }

    # Bogey with penalty
    bogey_holes = categorized_holes['bogey']
    bogey_with_penalty = 0
    for rid, hole in bogey_holes:
        hole_shots = filtered_df[
            (filtered_df['Round ID'] == rid) &
            (filtered_df['Hole'] == hole)
        ]
        if (hole_shots['Penalty'] == 'Yes').any():
            bogey_with_penalty += 1

    if len(bogey_holes) > 0:
        stats['bogey_penalty_pct'] = (bogey_with_penalty / len(bogey_holes)) * 100

    # Double Bogey+ with penalty and multiple bad shots
    db_holes = categorized_holes['double_bogey_plus']
    db_with_penalty = 0
    db_with_multiple_bad = 0

    for rid, hole in db_holes:
        hole_shots = filtered_df[
            (filtered_df['Round ID'] == rid) &
            (filtered_df['Hole'] == hole)
        ]

        # Check for penalty
        if (hole_shots['Penalty'] == 'Yes').any():
            db_with_penalty += 1

        # Check for 2+ shots with SG <= -0.5
        sg_numeric = pd.to_numeric(hole_shots['Strokes Gained'], errors='coerce')
        bad_shots = (sg_numeric <= -0.5).sum()
        if bad_shots >= 2:
            db_with_multiple_bad += 1

    if len(db_holes) > 0:
        stats['db_penalty_pct'] = (db_with_penalty / len(db_holes)) * 100
        stats['db_multiple_bad_pct'] = (db_with_multiple_bad / len(db_holes)) * 100

    return stats


def build_shot_details(filtered_df, all_analyzed_holes):
    """
    Builds shot-level detail for the detail section.

    Returns:
        dict mapping root_cause -> list of hole data dicts
    """
    shot_details = {
        'Short Putts': [],
        'Lag Putts': [],
        'Driving': [],
        'Approach': [],
        'Short Game': [],
        'Recovery and Other': []
    }

    for hole_data in all_analyzed_holes:
        rid = hole_data['round_id']
        hole_num = hole_data['hole']
        root_cause = hole_data['root_cause']

        # Get all shots for this hole
        hole_shots = filtered_df[
            (filtered_df['Round ID'] == rid) &
            (filtered_df['Hole'] == hole_num)
        ].copy()

        if hole_shots.empty:
            continue

        # Format shots for display
        shots_data = hole_shots[[
            'Shot', 'Starting Location', 'Starting Distance',
            'Ending Location', 'Ending Distance', 'Penalty',
            'Strokes Gained'
        ]].copy()

        shots_data = shots_data.rename(columns={
            'Shot': 'Shot #',
            'Starting Location': 'Starting Lie',
            'Starting Distance': 'Starting Dist',
            'Ending Location': 'Ending Lie',
            'Ending Distance': 'Ending Dist'
        })

        # Round numeric values
        for col in ['Starting Dist', 'Ending Dist', 'Strokes Gained']:
            if col in shots_data.columns:
                shots_data[col] = pd.to_numeric(shots_data[col], errors='coerce')
                shots_data[col] = shots_data[col].round(1)

        shot_details[root_cause].append({
            'date': str(hole_data['date']),
            'course': hole_data['course'],
            'hole': hole_data['hole'],
            'par': hole_data['par'],
            'score': hole_data['score'],
            'shots': shots_data
        })

    return shot_details


def build_scoring_performance(filtered_df, hole_summary):
    """
    Master function that orchestrates all scoring performance analysis.

    Returns:
        dict with all results needed for the Scoring Performance tab
    """
    # Step 1: Categorize holes
    categorized_holes = categorize_holes(hole_summary, filtered_df)

    # Step 2: Analyze each category
    db_analysis = analyze_category(
        filtered_df, hole_summary,
        categorized_holes['double_bogey_plus'],
        'Double Bogey+'
    )

    bogey_analysis = analyze_category(
        filtered_df, hole_summary,
        categorized_holes['bogey'],
        'Bogey'
    )

    underperf_analysis = analyze_category(
        filtered_df, hole_summary,
        categorized_holes['underperformance'],
        'Underperformance'
    )

    # Step 3: Aggregate total counts
    total_counts = {
        'Short Putts': 0,
        'Lag Putts': 0,
        'Driving': 0,
        'Approach': 0,
        'Short Game': 0,
        'Recovery and Other': 0
    }

    for analysis in [db_analysis, bogey_analysis, underperf_analysis]:
        for rc, count in analysis['counts'].items():
            total_counts[rc] += count

    total_fails = sum(total_counts.values())

    # Step 4: Combine all analyzed holes
    all_analyzed_holes = (
        db_analysis['holes'] +
        bogey_analysis['holes'] +
        underperf_analysis['holes']
    )

    # Step 5: Aggregate by round
    by_round = aggregate_by_round(filtered_df, all_analyzed_holes)

    # Step 6: Calculate penalty stats
    penalty_stats = calculate_penalty_stats(filtered_df, hole_summary, categorized_holes)

    # Step 7: Build shot details
    shot_details = build_shot_details(filtered_df, all_analyzed_holes)

    return {
        'categorized_holes': categorized_holes,
        'double_bogey_analysis': db_analysis,
        'bogey_analysis': bogey_analysis,
        'underperformance_analysis': underperf_analysis,
        'total_counts': total_counts,
        'total_fails': total_fails,
        'by_round': by_round,
        'penalty_stats': penalty_stats,
        'shot_details': shot_details
    }
