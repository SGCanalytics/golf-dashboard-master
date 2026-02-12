import pandas as pd
from ui.formatters import round_label

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
    Maps a shot to one of EIGHT root cause categories.

    Putting categories:
    - Short Putts: 0-6 feet
    - Mid-range Putts: 7-15 feet
    - Lag Putts: 16+ feet

    Returns:
        String category name
    """
    shot_type = shot_row['Shot Type']
    starting_dist = pd.to_numeric(shot_row['Starting Distance'], errors='coerce')

    if shot_type == 'Putt':
        if pd.notna(starting_dist):
            if starting_dist <= 6:
                return 'Short Putts'
            elif starting_dist <= 15:
                return 'Mid-range Putts'
            else:
                return 'Lag Putts'  # 16+ feet
        else:
            return 'Mid-range Putts'  # Default for unknown putt distance
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
        - 'sg_sums': dict mapping root_cause -> sum of worst_sg values
    """
    holes_data = []
    counts = {
        'Short Putts': 0,
        'Mid-range Putts': 0,
        'Lag Putts': 0,
        'Driving': 0,
        'Approach': 0,
        'Short Game': 0,
        'Recovery and Other': 0
    }

    # Track SG sums per root cause
    sg_sums = {
        'Short Putts': 0.0,
        'Mid-range Putts': 0.0,
        'Lag Putts': 0.0,
        'Driving': 0.0,
        'Approach': 0.0,
        'Short Game': 0.0,
        'Recovery and Other': 0.0
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

        # Get Tournament from filtered_df (not in hole_summary)
        tournament_info = filtered_df[
            (filtered_df['Round ID'] == rid) &
            (filtered_df['Hole'] == hole_num)
        ]
        tournament = tournament_info.iloc[0]['Tournament'] if not tournament_info.empty else ''

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
            'tournament': tournament,
            'date': hole_row.get('Date', ''),
            'course': hole_row.get('Course', ''),
            'par': hole_row['Par'],
            'score': hole_row['Hole Score'],
            'root_cause': root_cause,
            'worst_sg': float(worst_sg)
        })

        # Increment count
        counts[root_cause] += 1

        # Accumulate SG sum
        sg_sums[root_cause] += float(worst_sg)

    return {
        'holes': holes_data,
        'counts': counts,
        'sg_sums': sg_sums
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
        label = round_label(date_obj, r['Course'])

        # Count root causes for this round
        round_counts = {
            'Short Putts': 0,
            'Mid-range Putts': 0,
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
            'Mid-range Putts': round_counts['Mid-range Putts'],
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
            by_round_df['Mid-range Putts'] +
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


def build_scoring_impact(by_round_df):
    """
    Compare actual round scores vs potential scores if 50% of scoring fails
    were eliminated (each eliminated fail = 1 stroke saved).

    Pattern matches Tiger 5's build_tiger5_scoring_impact() function.

    Args:
        by_round_df: DataFrame with columns including 'Total Fails' and 'Total Score'

    Returns:
        DataFrame with columns: Label, Date, Total Score, Potential Score,
                                Total Fails, Fails Removed
    """
    if by_round_df.empty:
        return pd.DataFrame()

    impact = by_round_df.copy()
    impact['Fails Removed'] = (impact['Total Fails'] * 0.5).apply(
        lambda x: int(round(x))
    )
    impact['Potential Score'] = impact['Total Score'] - impact['Fails Removed']

    return impact[['Label', 'Date', 'Total Score', 'Potential Score',
                   'Total Fails', 'Fails Removed']].copy()


def build_shot_details(filtered_df, all_analyzed_holes):
    """
    Builds shot-level detail for the detail section.

    Returns:
        dict mapping root_cause -> list of hole data dicts
    """
    shot_details = {
        'Short Putts': [],
        'Mid-range Putts': [],
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
            'tournament': str(hole_data['tournament']),
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

    # Step 3: Aggregate total counts and SG sums
    total_counts = {
        'Short Putts': 0,
        'Mid-range Putts': 0,
        'Lag Putts': 0,
        'Driving': 0,
        'Approach': 0,
        'Short Game': 0,
        'Recovery and Other': 0
    }

    # Track total SG sums across all root causes
    total_sg_sums = {
        'Short Putts': 0.0,
        'Mid-range Putts': 0.0,
        'Lag Putts': 0.0,
        'Driving': 0.0,
        'Approach': 0.0,
        'Short Game': 0.0,
        'Recovery and Other': 0.0
    }

    for analysis in [db_analysis, bogey_analysis, underperf_analysis]:
        for rc, count in analysis['counts'].items():
            total_counts[rc] += count
        for rc, sg_sum in analysis['sg_sums'].items():
            total_sg_sums[rc] += sg_sum

    total_fails = sum(total_counts.values())

    # Calculate category breakdown counts
    category_counts = {
        'double_bogey_plus': len(categorized_holes['double_bogey_plus']),
        'bogey': len(categorized_holes['bogey']),
        'underperformance': len(categorized_holes['underperformance'])
    }

    # Calculate category breakdown SG sums
    category_sg_sums = {
        'double_bogey_plus': sum(db_analysis['sg_sums'].values()),
        'bogey': sum(bogey_analysis['sg_sums'].values()),
        'underperformance': sum(underperf_analysis['sg_sums'].values())
    }

    # Step 4: Combine all analyzed holes
    all_analyzed_holes = (
        db_analysis['holes'] +
        bogey_analysis['holes'] +
        underperf_analysis['holes']
    )

    # Step 5: Aggregate by round
    by_round = aggregate_by_round(filtered_df, all_analyzed_holes)

    # Add Total Score to by_round for scoring impact calculation
    if not by_round.empty:
        # Calculate total score per round from hole_summary
        round_scores = hole_summary.groupby('Round ID').agg(
            Total_Score=('Hole Score', 'sum')
        ).reset_index()
        by_round = by_round.merge(
            round_scores.rename(columns={'Total_Score': 'Total Score'}),
            on='Round ID',
            how='left'
        )

    # Step 6: Calculate penalty stats
    penalty_stats = calculate_penalty_stats(filtered_df, hole_summary, categorized_holes)

    # Step 7: Build scoring impact data
    scoring_impact = build_scoring_impact(by_round)

    # Step 8: Build shot details
    shot_details = build_shot_details(filtered_df, all_analyzed_holes)

    return {
        'categorized_holes': categorized_holes,
        'double_bogey_analysis': db_analysis,
        'bogey_analysis': bogey_analysis,
        'underperformance_analysis': underperf_analysis,
        'total_counts': total_counts,
        'total_sg_sums': total_sg_sums,
        'total_fails': total_fails,
        'category_counts': category_counts,
        'category_sg_sums': category_sg_sums,
        'by_round': by_round,
        'penalty_stats': penalty_stats,
        'scoring_impact': scoring_impact,
        'shot_details': shot_details
    }
