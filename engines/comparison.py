# ============================================================
# COMPARISON ENGINE — Multi-Group Performance Analysis
# ============================================================
# Supports comparison between:
# 1. Player vs Player
# 2. Round Quality (Under Par vs Par to +3 vs +4+)
# 3. Time Period (Recent N rounds vs Previous N rounds)
# ============================================================

import pandas as pd
import numpy as np


# ============================================================
# CONSTANTS & BUCKETS
# ============================================================

APPROACH_BUCKETS = ["50–100", "100–150", "150–200", ">200"]
PUTTING_BUCKETS = ["<5", "5-10", "10-20", "20-30", "30+"]
SHORT_GAME_BUCKETS = ["<10", "10-20", "20-30", "30-40", "40-50"]
SG_CATEGORIES = ["Driving", "Approach", "Short Game", "Putting"]


# ============================================================
# ROUND QUALITY CLASSIFICATION
# ============================================================

def classify_round_quality(hole_summary):
    """
    Classify rounds into quality tiers based on score vs par.
    
    Returns:
        Series mapping Round ID to quality category:
        - 'Under Par': score < 0 relative to par (great rounds)
        - 'Par to +3': score 0 to +3 (average rounds)
        - '+4+': score >= +4 (poor rounds)
    """
    if hole_summary.empty:
        return pd.Series(dtype=str)
    
    # Calculate score vs par for each round
    round_scores = hole_summary.groupby('Round ID').apply(
        lambda x: (x['Hole Score'].sum() - x['Par'].sum())
    )
    
    def classify(score_vs_par):
        if score_vs_par < 0:
            return 'Under Par'
        elif score_vs_par <= 3:
            return 'Even - +3'
        else:
            return '>+4'
    
    return round_scores.apply(classify)


def get_rounds_by_quality(hole_summary, quality_category):
    """Get set of Round IDs matching the quality category."""
    classifications = classify_round_quality(hole_summary)
    return set(classifications[classifications == quality_category].index)


# ============================================================
# TIME PERIOD SPLITTING
# ============================================================

def split_rounds_by_recency(df, num_recent, num_previous):
    """
    Split rounds by recency.
    
    Args:
        df: filtered DataFrame
        num_recent: number of recent rounds for Group 1
        num_previous: number of previous rounds for Group 2
    
    Returns:
        tuple: (recent_round_ids_set, previous_round_ids_set)
    """
    # Get unique rounds sorted by date
    round_dates = df.groupby('Round ID').agg({
        'Date': 'first'
    }).sort_values('Date')
    
    round_ids = round_dates.index.tolist()
    
    recent_rounds = set(round_ids[-num_recent:]) if num_recent > 0 else set()
    previous_start = max(0, len(round_ids) - num_recent - num_previous)
    previous_end = max(0, len(round_ids) - num_recent)
    previous_rounds = set(round_ids[previous_start:previous_end]) if num_previous > 0 else set()
    
    return recent_rounds, previous_rounds


# ============================================================
# GROUP DATA PROCESSING
# ============================================================

def _process_group_data(df, hole_summary, group_name):
    """
    Process raw data for a single group and return all metrics.
    
    Args:
        df: filtered DataFrame for this group
        hole_summary: hole summary DataFrame for this group
        group_name: name identifier for the group
    
    Returns:
        dict with all metrics for the group
    """
    if df.empty:
        return _empty_group_result(group_name)
    
    num_rounds = df['Round ID'].nunique()
    
    # --- SG by Category (per round) ---
    sg_by_category = _compute_sg_by_category(df, num_rounds)
    
    # --- Approach by Bucket (per round) ---
    approach_by_bucket = _compute_approach_by_bucket(df, num_rounds)
    
    # --- Putting by Bucket (per round) ---
    putting_by_bucket = _compute_putting_by_bucket(df, num_rounds)
    
    # --- Short Game by Bucket (per round) ---
    short_game_by_bucket = _compute_short_game_by_bucket(df, num_rounds)
    
    # --- Hole Outcomes ---
    hole_outcomes = _compute_hole_outcomes(hole_summary)
    
    # --- Tiger 5 Analysis ---
    tiger5_summary = _compute_tiger5_summary(df, hole_summary)
    
    # --- Mental Metrics ---
    mental_metrics = _compute_mental_metrics(df, hole_summary)
    
    # --- Basic Stats ---
    basic_stats = _compute_basic_stats(df, hole_summary)
    
    # --- Scoring Summary ---
    scoring_avg = hole_summary['Hole Score'].mean() if not hole_summary.empty else 0
    
    # Calculate total SG and per-round SG
    total_sg = df['Strokes Gained'].sum() if not df.empty else 0
    sg_per_round = round(total_sg / num_rounds, 2) if num_rounds > 0 else 0
    
    # Calculate low and high scores
    round_scores = hole_summary.groupby('Round ID')['Hole Score'].sum() if not hole_summary.empty else pd.Series()
    low_score = round_scores.min() if not round_scores.empty else 0
    high_score = round_scores.max() if not round_scores.empty else 0
    
    return {
        'name': group_name,
        'num_rounds': num_rounds,
        'scoring_avg': round(scoring_avg, 2),
        'total_sg': round(total_sg, 2),
        'sg_per_round': sg_per_round,
        'low_score': int(low_score),
        'high_score': int(high_score),
        'sg_by_category': sg_by_category,
        'approach_by_bucket': approach_by_bucket,
        'putting_by_bucket': putting_by_bucket,
        'short_game_by_bucket': short_game_by_bucket,
        'hole_outcomes': hole_outcomes,
        'tiger5': tiger5_summary,
        'mental_metrics': mental_metrics,
        'basic_stats': basic_stats,
    }


def _empty_group_result(group_name):
    """Return empty result structure for groups with no data."""
    return {
        'name': group_name,
        'num_rounds': 0,
        'scoring_avg': 0,
        'total_sg': 0,
        'sg_per_round': 0,
        'low_score': 0,
        'high_score': 0,
        'sg_by_category': {cat: 0.0 for cat in SG_CATEGORIES},
        'approach_by_bucket': {b: 0.0 for b in APPROACH_BUCKETS},
        'putting_by_bucket': {b: 0.0 for b in PUTTING_BUCKETS},
        'short_game_by_bucket': {b: 0.0 for b in SHORT_GAME_BUCKETS},
        'hole_outcomes': {'Eagle': 0, 'Birdie': 0, 'Par': 0, 'Bogey': 0, 'Double or Worse': 0},
        'tiger5': {'total_fails': 0, 'grit_score': 0, 'by_category': {}},
        'mental_metrics': {
            'bounce_back': {'rate': 0, 'opportunities': 0, 'successes': 0},
            'drop_off': {'rate': 0, 'opportunities': 0, 'events': 0},
            'gas_pedal': {'rate': 0, 'opportunities': 0, 'successes': 0},
            'bogey_train_rate': {'btr': 0, 'bogey_plus': 0, 'train_holes': 0, 'longest': 0},
        },
        'basic_stats': {'fw_pct': 0, 'gir_pct': 0, 'penalties': 0},
    }


# ============================================================
# SG CATEGORY COMPUTATION
# ============================================================

def _compute_sg_by_category(df, num_rounds=1):
    """Compute average SG per round by major category."""
    if df.empty:
        return {cat: 0.0 for cat in SG_CATEGORIES}
    
    sg_by_cat = df.groupby('Shot Type')['Strokes Gained'].sum()
    
    result = {}
    for cat in SG_CATEGORIES:
        total = float(sg_by_cat.get(cat, 0))
        result[cat] = round(total / num_rounds, 2) if num_rounds > 0 else 0.0
    
    return result


# ============================================================
# APPROACH BUCKET COMPUTATION
# ============================================================

def _approach_bucket(dist):
    """Assign approach distance bucket."""
    if 50 <= dist < 100:
        return "50–100"
    elif 100 <= dist < 150:
        return "100–150"
    elif 150 <= dist < 200:
        return "150–200"
    elif dist >= 200:
        return ">200"
    return None


def _compute_approach_by_bucket(df, num_rounds=1):
    """Compute average SG per round by approach distance bucket."""
    if df.empty:
        return {b: 0.0 for b in APPROACH_BUCKETS}
    
    approach_df = df[df['Shot Type'] == 'Approach'].copy()
    if approach_df.empty:
        return {b: 0.0 for b in APPROACH_BUCKETS}
    
    approach_df['Starting Distance'] = pd.to_numeric(
        approach_df['Starting Distance'], errors='coerce'
    )
    approach_df['Bucket'] = approach_df['Starting Distance'].apply(_approach_bucket)
    
    sg_by_bucket = approach_df.groupby('Bucket')['Strokes Gained'].sum()
    
    result = {}
    for bucket in APPROACH_BUCKETS:
        total = float(sg_by_bucket.get(bucket, 0))
        result[bucket] = round(total / num_rounds, 2) if num_rounds > 0 else 0.0
    
    return result


# ============================================================
# PUTTING BUCKET COMPUTATION
# ============================================================

def _putting_bucket(dist):
    """Assign putting distance bucket."""
    if dist < 5:
        return "<5"
    elif dist < 10:
        return "5-10"
    elif dist < 20:
        return "10-20"
    elif dist < 30:
        return "20-30"
    else:
        return "30+"


def _compute_putting_by_bucket(df, num_rounds=1):
    """Compute average SG per round by putting distance bucket."""
    if df.empty:
        return {b: 0.0 for b in PUTTING_BUCKETS}
    
    putting_df = df[df['Shot Type'] == 'Putt'].copy()
    if putting_df.empty:
        return {b: 0.0 for b in PUTTING_BUCKETS}
    
    putting_df['Starting Distance'] = pd.to_numeric(
        putting_df['Starting Distance'], errors='coerce'
    )
    putting_df['Bucket'] = putting_df['Starting Distance'].apply(_putting_bucket)
    
    sg_by_bucket = putting_df.groupby('Bucket')['Strokes Gained'].sum()
    
    result = {}
    for bucket in PUTTING_BUCKETS:
        total = float(sg_by_bucket.get(bucket, 0))
        result[bucket] = round(total / num_rounds, 2) if num_rounds > 0 else 0.0
    
    return result


# ============================================================
# SHORT GAME BUCKET COMPUTATION
# ============================================================

def _short_game_bucket(dist):
    """Assign short game distance bucket."""
    if dist < 10:
        return "<10"
    elif dist < 20:
        return "10-20"
    elif dist < 30:
        return "20-30"
    elif dist < 40:
        return "30-40"
    else:
        return "40-50"


def _compute_short_game_by_bucket(df, num_rounds=1):
    """Compute average SG per round by short game distance bucket."""
    if df.empty:
        return {b: 0.0 for b in SHORT_GAME_BUCKETS}
    
    sg_df = df[df['Shot Type'] == 'Short Game'].copy()
    if sg_df.empty:
        return {b: 0.0 for b in SHORT_GAME_BUCKETS}
    
    sg_df['Starting Distance'] = pd.to_numeric(
        sg_df['Starting Distance'], errors='coerce'
    )
    sg_df['Bucket'] = sg_df['Starting Distance'].apply(_short_game_bucket)
    
    sg_by_bucket = sg_df.groupby('Bucket')['Strokes Gained'].sum()
    
    result = {}
    for bucket in SHORT_GAME_BUCKETS:
        total = float(sg_by_bucket.get(bucket, 0))
        result[bucket] = round(total / num_rounds, 2) if num_rounds > 0 else 0.0
    
    return result


# ============================================================
# HOLE OUTCOME COMPUTATION
# ============================================================

def _compute_hole_outcomes(hole_summary):
    """Count hole outcomes by score type."""
    if hole_summary.empty:
        return {'Eagle': 0, 'Birdie': 0, 'Par': 0, 'Bogey': 0, 'Double or Worse': 0}
    
    counts = hole_summary['Score Name'].value_counts()
    
    return {
        'Eagle': int(counts.get('Eagle', 0)),
        'Birdie': int(counts.get('Birdie', 0)),
        'Par': int(counts.get('Par', 0)),
        'Bogey': int(counts.get('Bogey', 0)),
        'Double or Worse': int(counts.get('Double or Worse', 0)),
    }


# ============================================================
# TIGER 5 COMPUTATION
# ============================================================

def _compute_tiger5_summary(df, hole_summary):
    """Compute Tiger 5 totals and root causes for a group."""
    if hole_summary.empty:
        return {'total_fails': 0, 'grit_score': 0, 'by_category': {}}
    
    # 3 Putts
    three_putts = (hole_summary['num_putts'] >= 3).sum()
    
    # Double Bogey+
    double_bogey = (hole_summary['Hole Score'] >= hole_summary['Par'] + 2).sum()
    
    # Par 5 Bogey
    par5 = hole_summary[hole_summary['Par'] == 5]
    par5_bogey = (par5['Hole Score'] >= 6).sum() if not par5.empty else 0
    
    # Missed Green (simplified)
    sg_shots = df[df['Shot Type'] == 'Short Game']
    missed_green = 0
    if not sg_shots.empty:
        missed_green = (~sg_shots['Ending Location'].isin(['Green', 'Hole'])).sum()
    
    # 125yd Bogey (simplified)
    approach_125 = df[
        (df['Shot Type'] == 'Approach') &
        (pd.to_numeric(df['Starting Distance'], errors='coerce') <= 125)
    ]
    holes_with_125 = approach_125[['Round ID', 'Hole']].drop_duplicates()
    if not holes_with_125.empty:
        holes_with_125 = holes_with_125.merge(
            hole_summary[['Round ID', 'Hole', 'Hole Score', 'Par']],
            on=['Round ID', 'Hole'],
            how='left'
        )
        _125_bogey = (holes_with_125['Hole Score'] > holes_with_125['Par']).sum()
    else:
        _125_bogey = 0
    
    total_fails = three_putts + double_bogey + par5_bogey + missed_green + _125_bogey
    total_opportunities = (
        len(hole_summary) +  # 3 putt opportunities
        len(hole_summary) +  # double bogey opportunities
        len(par5) +          # par 5 opportunities
        len(sg_shots.groupby(['Round ID', 'Hole']).size()) +  # missed green opportunities
        len(holes_with_125)  # 125yd opportunities
    )
    
    grit_score = (
        ((total_opportunities - total_fails) / total_opportunities * 100)
        if total_opportunities > 0 else 0
    )
    
    return {
        'total_fails': int(total_fails),
        'grit_score': round(grit_score, 1),
        'by_category': {
            '3 Putts': int(three_putts),
            'Double Bogey': int(double_bogey),
            'Par 5 Bogey': int(par5_bogey),
            'Missed Green': int(missed_green),
            '125yd Bogey': int(_125_bogey),
        }
    }


# ============================================================
# MENTAL METRICS COMPUTATION
# ============================================================

def _compute_mental_metrics(df, hole_summary):
    """Compute mental/flow metrics for a group."""
    if hole_summary.empty:
        return {
            'bounce_back': {'rate': 0, 'opportunities': 0, 'successes': 0},
            'drop_off': {'rate': 0, 'opportunities': 0, 'events': 0},
            'gas_pedal': {'rate': 0, 'opportunities': 0, 'successes': 0},
            'bogey_train_rate': {'btr': 0, 'bogey_plus': 0, 'train_holes': 0, 'longest': 0},
        }
    
    # Bounce Back Rate
    bounce_back = _bounce_back_rate(hole_summary)
    
    # Drop Off Rate
    drop_off = _drop_off_rate(hole_summary)
    
    # Gas Pedal Rate
    gas_pedal = _gas_pedal_rate(hole_summary)
    
    # Bogey Train Rate
    bogey_train = _bogey_train_rate(hole_summary)
    
    return {
        'bounce_back': bounce_back,
        'drop_off': drop_off,
        'gas_pedal': gas_pedal,
        'bogey_train_rate': bogey_train,
    }


def _bounce_back_rate(hole_summary):
    """Calculate bounce back rate."""
    opp, success = 0, 0
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        sorted_df = round_df.sort_values('Hole').reset_index(drop=True)
        
        for i in range(len(sorted_df) - 1):
            current_score = sorted_df.iloc[i]['Hole Score']
            current_par = sorted_df.iloc[i]['Par']
            next_score = sorted_df.iloc[i + 1]['Hole Score']
            next_par = sorted_df.iloc[i + 1]['Par']
            
            if current_score >= current_par + 1:  # bogey or worse
                opp += 1
                if next_score <= next_par:  # par or better
                    success += 1
    
    rate = success / opp * 100 if opp > 0 else 0.0
    return {"rate": round(rate, 1), "opportunities": opp, "successes": success}


def _drop_off_rate(hole_summary):
    """Calculate drop off rate."""
    opp, events = 0, 0
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        sorted_df = round_df.sort_values('Hole').reset_index(drop=True)
        
        for i in range(len(sorted_df) - 1):
            prev_score = sorted_df.iloc[i]['Hole Score']
            prev_par = sorted_df.iloc[i]['Par']
            curr_score = sorted_df.iloc[i + 1]['Hole Score']
            curr_par = sorted_df.iloc[i + 1]['Par']
            
            if prev_score >= prev_par + 1:  # previous hole was bogey+
                opp += 1
                if curr_score >= curr_par + 1:  # current hole is also bogey+
                    events += 1
    
    rate = events / opp * 100 if opp > 0 else 0.0
    return {"rate": round(rate, 1), "opportunities": opp, "events": events}


def _gas_pedal_rate(hole_summary):
    """Calculate gas pedal rate."""
    opp, success = 0, 0
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        sorted_df = round_df.sort_values('Hole').reset_index(drop=True)
        
        for i in range(len(sorted_df) - 1):
            prev_score = sorted_df.iloc[i]['Hole Score']
            prev_par = sorted_df.iloc[i]['Par']
            curr_score = sorted_df.iloc[i + 1]['Hole Score']
            curr_par = sorted_df.iloc[i + 1]['Par']
            
            if prev_score <= prev_par - 1:  # birdie or better
                opp += 1
                if curr_score <= curr_par - 1:  # birdie or better
                    success += 1
    
    rate = success / opp * 100 if opp > 0 else 0.0
    return {"rate": round(rate, 1), "opportunities": opp, "successes": success}


def _bogey_train_rate(hole_summary):
    """Calculate bogey train rate."""
    bogey_plus_holes = 0
    bogey_train_holes = 0
    all_trains = []
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        sorted_df = round_df.sort_values('Hole').reset_index(drop=True)
        
        current_train = 0
        for _, row in sorted_df.iterrows():
            score = row['Hole Score']
            par = row['Par']
            
            if score >= par + 1:  # bogey or worse
                bogey_plus_holes += 1
                current_train += 1
            else:
                if current_train >= 2:
                    bogey_train_holes += current_train
                    all_trains.append(current_train)
                current_train = 0
        
        if current_train >= 2:
            bogey_train_holes += current_train
            all_trains.append(current_train)
    
    btr = bogey_train_holes / bogey_plus_holes * 100 if bogey_plus_holes > 0 else 0.0
    
    return {
        "btr": round(btr, 1),
        "bogey_plus": bogey_plus_holes,
        "train_holes": bogey_train_holes,
        "longest": max(all_trains) if all_trains else 0
    }


# ============================================================
# BASIC STATS COMPUTATION
# ============================================================

def _compute_basic_stats(df, hole_summary):
    """Compute basic stats (FW%, GIR%, Penalties)."""
    if df.empty:
        return {'fw_pct': 0, 'gir_pct': 0, 'penalties': 0}
    
    # Fairway % (drives that end in fairway or green)
    drives = df[df['Shot Type'] == 'Driving']
    if not drives.empty:
        fw_hits = drives['Ending Location'].isin(['Fairway', 'Green']).sum()
        fw_pct = fw_hits / len(drives) * 100
    else:
        fw_pct = 0
    
    # GIR % (approaches that hit green)
    approaches = df[df['Shot Type'] == 'Approach']
    if not approaches.empty:
        gir_hits = (approaches['Ending Location'] == 'Green').sum()
        gir_pct = gir_hits / len(approaches) * 100
    else:
        gir_pct = 0
    
    # Penalties
    penalties = (df['Penalty'] == 'Yes').sum()
    
    return {
        'fw_pct': round(fw_pct, 1),
        'gir_pct': round(gir_pct, 1),
        'penalties': int(penalties),
    }


# ============================================================
# MAIN COMPARISON ENGINE
# ============================================================

def build_comparison_data(filtered_df, hole_summary, mode, mode_params):
    """
    Build comparison data for the selected mode.
    
    Args:
        filtered_df: Full filtered DataFrame
        hole_summary: Full hole summary DataFrame
        mode: 'player', 'round_quality', or 'time_period'
        mode_params: dict with mode-specific parameters
    
    Returns:
        dict with:
        - mode: the comparison mode
        - group1: processed data for Group 1
        - group2: processed data for Group 2
        - group1_label: display name for Group 1
        - group2_label: display name for Group 2
    """
    
    if mode == 'player':
        return _compare_players(filtered_df, hole_summary, mode_params)
    
    elif mode == 'round_quality':
        return _compare_round_quality(filtered_df, hole_summary, mode_params)
    
    elif mode == 'time_period':
        return _compare_time_periods(filtered_df, hole_summary, mode_params)
    
    else:
        raise ValueError(f"Unknown comparison mode: {mode}")


def _compare_players(df, hole_summary, params):
    """Compare two players."""
    player1 = params.get('player1', '')
    player2 = params.get('player2', '')
    
    # Filter data for each player
    df1 = df[df['Player'] == player1].copy() if player1 else df.copy()
    df2 = df[df['Player'] == player2].copy() if player2 else df.copy()
    
    # Get hole summaries for each player
    hs1 = hole_summary[hole_summary['Player'] == player1].copy() if player1 else hole_summary.copy()
    hs2 = hole_summary[hole_summary['Player'] == player2].copy() if player2 else hole_summary.copy()
    
    group1_data = _process_group_data(df1, hs1, player1)
    group2_data = _process_group_data(df2, hs2, player2)
    
    return {
        'mode': 'player',
        'group1': group1_data,
        'group2': group2_data,
        'group1_label': player1 or 'All Players',
        'group2_label': player2 or 'All Players',
    }


def _compare_round_quality(df, hole_summary, params):
    """Compare round quality categories."""
    quality1 = params.get('quality1', 'Under Par')
    quality2 = params.get('quality2', '+4+')
    
    # Get round IDs by quality
    rounds_quality1 = get_rounds_by_quality(hole_summary, quality1)
    rounds_quality2 = get_rounds_by_quality(hole_summary, quality2)
    
    # Filter data by round IDs
    df1 = df[df['Round ID'].isin(rounds_quality1)].copy()
    df2 = df[df['Round ID'].isin(rounds_quality2)].copy()
    
    hs1 = hole_summary[hole_summary['Round ID'].isin(rounds_quality1)].copy()
    hs2 = hole_summary[hole_summary['Round ID'].isin(rounds_quality2)].copy()
    
    group1_data = _process_group_data(df1, hs1, quality1)
    group2_data = _process_group_data(df2, hs2, quality2)
    
    return {
        'mode': 'round_quality',
        'group1': group1_data,
        'group2': group2_data,
        'group1_label': quality1,
        'group2_label': quality2,
    }


def _compare_time_periods(df, hole_summary, params):
    """Compare recent vs previous time periods."""
    num_recent = params.get('num_recent', 5)
    num_previous = params.get('num_previous', 5)
    
    # Split rounds by recency
    recent_rounds, previous_rounds = split_rounds_by_recency(df, num_recent, num_previous)
    
    # Filter data by round IDs
    df1 = df[df['Round ID'].isin(recent_rounds)].copy()
    df2 = df[df['Round ID'].isin(previous_rounds)].copy()
    
    hs1 = hole_summary[hole_summary['Round ID'].isin(recent_rounds)].copy()
    hs2 = hole_summary[hole_summary['Round ID'].isin(previous_rounds)].copy()
    
    group1_label = f"Recent {num_recent} Rounds"
    group2_label = f"Previous {num_previous} Rounds"
    
    group1_data = _process_group_data(df1, hs1, group1_label)
    group2_data = _process_group_data(df2, hs2, group2_label)
    
    return {
        'mode': 'time_period',
        'group1': group1_data,
        'group2': group2_data,
        'group1_label': group1_label,
        'group2_label': group2_label,
    }
