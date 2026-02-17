import pandas as pd
from engines.helpers import zone_distance_bucket, safe_divide

# ============================================================
# COACHES TABLE ENGINE
# Per-player aggregation of all key performance metrics
# ============================================================


def _calculate_player_metrics(player, tournament, player_df, player_holes):
    """
    Calculate all metrics for a single player-tournament combination.

    Args:
        player: Player name
        tournament: Tournament name
        player_df: Shot-level data filtered to this player-tournament
        player_holes: Hole-level data filtered to this player-tournament

    Returns:
        dict with all metric values for one row
    """
    # Basic metrics
    num_rounds = player_df['Round ID'].nunique() if not player_df.empty else 0

    if num_rounds == 0 or player_holes.empty:
        # Return zeros for all metrics if no data
        return _empty_player_row(player, tournament)

    # Calculate all metrics
    metrics = {
        'Player': player,
        'Tournament': tournament,
        'Rounds': num_rounds,
    }

    # --- BASIC METRICS ---
    metrics['Avg Score'] = player_holes['Hole Score'].sum() / num_rounds

    # --- TIGER 5 METRICS ---
    tiger5 = _calculate_tiger5_metrics(player_df, player_holes, num_rounds)
    metrics.update(tiger5)

    # --- SCORING FAILS (total of all Tiger 5 categories) ---
    metrics['SF/Rd'] = tiger5['T5 Fails/Rd']

    # --- MOMENTUM METRICS ---
    momentum = _calculate_momentum_metrics(player_holes, num_rounds)
    metrics.update(momentum)

    # --- SG METRICS ---
    sg_metrics = _calculate_sg_metrics(player_df, num_rounds)
    metrics.update(sg_metrics)

    # --- DRIVING DETAILS ---
    driving = _calculate_driving_metrics(player_df, num_rounds)
    metrics.update(driving)

    # --- APPROACH ZONE SG ---
    approach_zones = _calculate_approach_zones(player_df)
    metrics.update(approach_zones)

    # --- SHORT GAME METRICS ---
    short_game = _calculate_short_game_metrics(player_df)
    metrics.update(short_game)

    # --- PUTTING METRICS ---
    putting = _calculate_putting_metrics(player_df)
    metrics.update(putting)

    return metrics


def _empty_player_row(player, tournament):
    """Return a row with all metrics set to 0."""
    return {
        'Player': player,
        'Tournament': tournament,
        'Rounds': 0,
        'Avg Score': 0.0,
        'T5 Fails/Rd': 0.0,
        '3P/Rd': 0.0,
        'DB/Rd': 0.0,
        'P5B/Rd': 0.0,
        'MG/Rd': 0.0,
        '125B/Rd': 0.0,
        'SF/Rd': 0.0,
        'BB%': 0.0,
        'DO%': 0.0,
        'GP%': 0.0,
        'BT': 0,
        'SG/Rd': 0.0,
        'SGD/Rd': 0.0,
        'Obs%': 0.0,
        'Pen%': 0.0,
        'FW%': 0.0,
        'SGA/Rd': 0.0,
        'GZ SG': 0.0,
        'YZ SG': 0.0,
        'RZ SG': 0.0,
        'SGSG/Rd': 0.0,
        'SG25-50': 0.0,
        'SG0-25': 0.0,
        'SGP/Rd': 0.0,
        'SG4-6': 0.0,
        'SG7-10': 0.0,
        'Lag%': 0.0,
        'SGO/Rd': 0.0,
    }


def _calculate_tiger5_metrics(player_df, player_holes, num_rounds):
    """Calculate Tiger 5 metrics per round (pattern from tiger5.py)."""
    # 3 Putts per round
    three_putts = (player_holes['num_putts'] >= 3).sum() if 'num_putts' in player_holes.columns else 0

    # Double Bogeys per round
    double_bogeys = (player_holes['Hole Score'] >= player_holes['Par'] + 2).sum()

    # Par 5 Bogeys per round
    par5_holes = player_holes[player_holes['Par'] == 5]
    par5_bogeys = (par5_holes['Hole Score'] >= 6).sum() if not par5_holes.empty else 0

    # Missed Green per round (short game shots not ending on green)
    sg_shots = player_df[player_df['Shot Type'] == 'Short Game'].copy()
    if not sg_shots.empty:
        sg_shots['missed_green'] = sg_shots['Ending Location'] != 'Green'
        by_hole = sg_shots.groupby(['Round ID', 'Hole']).agg(
            any_missed=('missed_green', 'any')
        ).reset_index()
        missed_green_count = by_hole['any_missed'].sum()
    else:
        missed_green_count = 0

    # 125yd Bogey per round (pattern from tiger5.py lines 77-106)
    cond = (
        (player_df['Starting Distance'] <= 125) &
        (player_df['Starting Location'] != 'Recovery') &
        (
            ((player_df['Shot'] == 3) & (player_df['Par'] == 5)) |
            ((player_df['Shot'] == 2) & (player_df['Par'] == 4)) |
            ((player_df['Shot'] == 1) & (player_df['Par'] == 3))
        )
    )
    candidates = player_df[cond][['Round ID', 'Hole']].drop_duplicates()
    if not candidates.empty:
        with_score = candidates.merge(
            player_holes[['Round ID', 'Hole', 'Hole Score', 'Par']],
            on=['Round ID', 'Hole'], how='left'
        )
        bogey_125 = (with_score['Hole Score'] > with_score['Par']).sum()
    else:
        bogey_125 = 0

    # Total Tiger 5 fails
    total_t5 = three_putts + double_bogeys + par5_bogeys + missed_green_count + bogey_125

    return {
        'T5 Fails/Rd': total_t5 / num_rounds,
        '3P/Rd': three_putts / num_rounds,
        'DB/Rd': double_bogeys / num_rounds,
        'P5B/Rd': par5_bogeys / num_rounds,
        'MG/Rd': missed_green_count / num_rounds,
        '125B/Rd': bogey_125 / num_rounds,
    }


def _calculate_momentum_metrics(player_holes, num_rounds):
    """Calculate momentum metrics (pattern from coachs_corner.py lines 114-203)."""
    bounce_back_attempts = 0
    bounce_back_successes = 0
    drop_off_attempts = 0
    drop_off_count = 0
    gas_pedal_attempts = 0
    gas_pedal_count = 0
    all_bogey_trains = []

    for rid in player_holes['Round ID'].unique():
        round_holes = player_holes[player_holes['Round ID'] == rid].sort_values('Hole')
        scores = round_holes['Hole Score'].values
        pars = round_holes['Par'].values

        current_train = 0

        for i in range(len(scores)):
            is_bogey_plus = scores[i] > pars[i]
            is_birdie_plus = scores[i] < pars[i]

            # Track bogey trains
            if is_bogey_plus:
                current_train += 1
            else:
                if current_train >= 2:
                    all_bogey_trains.append(current_train)
                current_train = 0

            if i == 0:
                continue

            prev_bogey = scores[i-1] > pars[i-1]
            prev_birdie = scores[i-1] < pars[i-1]

            # Bounce back
            if prev_bogey:
                bounce_back_attempts += 1
                if scores[i] <= pars[i]:
                    bounce_back_successes += 1

            # Drop off
            if prev_birdie:
                drop_off_attempts += 1
                if is_bogey_plus:
                    drop_off_count += 1

            # Gas pedal
            if prev_birdie:
                gas_pedal_attempts += 1
                if is_birdie_plus:
                    gas_pedal_count += 1

        # End-of-round train check
        if current_train >= 2:
            all_bogey_trains.append(current_train)

    bounce_back_pct = safe_divide(bounce_back_successes, bounce_back_attempts) * 100
    drop_off_pct = safe_divide(drop_off_count, drop_off_attempts) * 100
    gas_pedal_pct = safe_divide(gas_pedal_count, gas_pedal_attempts) * 100
    bogey_train_count = len(all_bogey_trains)

    return {
        'BB%': bounce_back_pct,
        'DO%': drop_off_pct,
        'GP%': gas_pedal_pct,
        'BT': bogey_train_count,
    }


def _calculate_sg_metrics(player_df, num_rounds):
    """Calculate SG metrics by shot type."""
    # Total SG
    total_sg = player_df['Strokes Gained'].sum()

    # SG by shot type
    sg_driving = player_df[player_df['Shot Type'] == 'Driving']['Strokes Gained'].sum()
    sg_approach = player_df[player_df['Shot Type'] == 'Approach']['Strokes Gained'].sum()
    sg_short_game = player_df[player_df['Shot Type'] == 'Short Game']['Strokes Gained'].sum()
    sg_putting = player_df[player_df['Shot Type'] == 'Putt']['Strokes Gained'].sum()
    sg_other = player_df[player_df['Shot Type'] == 'Other']['Strokes Gained'].sum()

    return {
        'SG/Rd': total_sg / num_rounds,
        'SGD/Rd': sg_driving / num_rounds,
        'SGA/Rd': sg_approach / num_rounds,
        'SGSG/Rd': sg_short_game / num_rounds,
        'SGP/Rd': sg_putting / num_rounds,
        'SGO/Rd': sg_other / num_rounds,
    }


def _calculate_driving_metrics(player_df, num_rounds):
    """Calculate driving detail metrics (pattern from driving.py)."""
    drives = player_df[player_df['Shot Type'] == 'Driving'].copy()

    if drives.empty:
        return {'Obs%': 0.0, 'Pen%': 0.0, 'FW%': 0.0}

    total_drives = len(drives)

    # Obstruction rate (non-playable: Sand, Recovery, Penalty)
    non_playable = drives['Ending Location'].isin(['Sand', 'Recovery', 'Penalty']).sum()
    obstruction_rate = safe_divide(non_playable, total_drives) * 100

    # Penalty rate
    penalty_count = (drives['Penalty'] == 'Yes').sum()
    penalty_rate = safe_divide(penalty_count, total_drives) * 100

    # Fairways hit %
    fairway_count = (drives['Ending Location'] == 'Fairway').sum()
    fairway_pct = safe_divide(fairway_count, total_drives) * 100

    return {
        'Obs%': obstruction_rate,
        'Pen%': penalty_rate,
        'FW%': fairway_pct,
    }


def _calculate_approach_zones(player_df):
    """Calculate approach zone SG (pattern from approach.py lines 114-119)."""
    approach_shots = player_df[player_df['Shot Type'] == 'Approach'].copy()

    if approach_shots.empty:
        return {'GZ SG': 0.0, 'YZ SG': 0.0, 'RZ SG': 0.0}

    # Ensure numeric
    approach_shots['Starting Distance'] = pd.to_numeric(
        approach_shots['Starting Distance'], errors='coerce'
    )

    # Assign zones
    approach_shots['Zone'] = approach_shots['Starting Distance'].apply(zone_distance_bucket)

    # Green Zone (75-125 yds)
    green_zone = approach_shots[approach_shots['Zone'] == 'Green Zone']
    green_zone_sg = green_zone['Strokes Gained'].sum() if not green_zone.empty else 0.0

    # Yellow Zone (125-175 yds)
    yellow_zone = approach_shots[approach_shots['Zone'] == 'Yellow Zone']
    yellow_zone_sg = yellow_zone['Strokes Gained'].sum() if not yellow_zone.empty else 0.0

    # Red Zone (175-225 yds)
    red_zone = approach_shots[approach_shots['Zone'] == 'Red Zone']
    red_zone_sg = red_zone['Strokes Gained'].sum() if not red_zone.empty else 0.0

    return {
        'GZ SG': green_zone_sg,
        'YZ SG': yellow_zone_sg,
        'RZ SG': red_zone_sg,
    }


def _calculate_short_game_metrics(player_df):
    """Calculate short game distance-based SG (pattern from short_game.py)."""
    sg_shots = player_df[player_df['Shot Type'] == 'Short Game'].copy()

    if sg_shots.empty:
        return {'SG25-50': 0.0, 'SG0-25': 0.0}

    # Ensure numeric
    sg_shots['Starting Distance'] = pd.to_numeric(
        sg_shots['Starting Distance'], errors='coerce'
    )

    # SG 25-50 yards
    sg_25_50 = sg_shots[sg_shots['Starting Distance'] >= 25]['Strokes Gained'].sum()

    # SG 0-25 yards
    sg_0_25 = sg_shots[sg_shots['Starting Distance'] < 25]['Strokes Gained'].sum()

    return {
        'SG25-50': sg_25_50,
        'SG0-25': sg_0_25,
    }


def _calculate_putting_metrics(player_df):
    """Calculate putting detail metrics (pattern from putting.py lines 43-95)."""
    putts = player_df[player_df['Shot Type'] == 'Putt'].copy()

    if putts.empty:
        return {'SG4-6': 0.0, 'SG7-10': 0.0, 'Lag%': 0.0}

    # Ensure numeric
    putts['Starting Distance'] = pd.to_numeric(putts['Starting Distance'], errors='coerce')
    putts['Ending Distance'] = pd.to_numeric(putts['Ending Distance'], errors='coerce')

    # SG 4-6 ft
    sg_4_6_putts = putts[
        (putts['Starting Distance'] >= 4) & (putts['Starting Distance'] <= 6)
    ]
    sg_4_6 = sg_4_6_putts['Strokes Gained'].sum() if not sg_4_6_putts.empty else 0.0

    # SG 7-10 ft
    sg_7_10_putts = putts[
        (putts['Starting Distance'] >= 7) & (putts['Starting Distance'] <= 10)
    ]
    sg_7_10 = sg_7_10_putts['Strokes Gained'].sum() if not sg_7_10_putts.empty else 0.0

    # Poor Lag % (first putts >= 20 ft leaving > 5 ft)
    putts['Hole Key'] = (
        putts['Player'].astype(str) + '|' +
        putts['Round ID'].astype(str) + '|' +
        putts['Hole'].astype(str)
    )
    putts = putts.sort_values(['Hole Key', 'Shot'])
    putts['Putt Number'] = putts.groupby('Hole Key').cumcount() + 1

    first_putts = putts[putts['Putt Number'] == 1]
    lag_first = first_putts[first_putts['Starting Distance'] >= 20]
    poor_lag_pct = safe_divide(
        (lag_first['Ending Distance'] > 5).sum(), len(lag_first)
    ) * 100

    return {
        'SG4-6': sg_4_6,
        'SG7-10': sg_7_10,
        'Lag%': poor_lag_pct,
    }


def build_coaches_table_results(filtered_df, hole_summary):
    """
    Build per-player performance metrics for coaches table.

    Args:
        filtered_df: Shot-level data (may include multiple players/tournaments)
        hole_summary: Hole-level aggregated data

    Returns:
        {
            "players_df": pd.DataFrame with one row per player-tournament,
            "tournaments": list of unique tournament names (sorted),
            "empty": bool indicating if data is empty,
            "column_groups": dict mapping group names to column lists
        }
    """
    if filtered_df.empty or hole_summary.empty:
        return {
            "empty": True,
            "players_df": pd.DataFrame(),
            "tournaments": [],
            "column_groups": _get_column_groups(),
        }

    rows = []

    # Loop through each unique (player, tournament) combination
    for player in sorted(filtered_df['Player'].unique()):
        for tournament in sorted(filtered_df[filtered_df['Player'] == player]['Tournament'].unique()):
            # Filter to this player-tournament combination
            player_tournament_df = filtered_df[
                (filtered_df['Player'] == player) &
                (filtered_df['Tournament'] == tournament)
            ].copy()

            # Get the Round IDs for this player-tournament combination
            player_tournament_rounds = player_tournament_df['Round ID'].unique()

            # Filter hole_summary by player and these Round IDs
            player_tournament_holes = hole_summary[
                (hole_summary['Player'] == player) &
                (hole_summary['Round ID'].isin(player_tournament_rounds))
            ].copy()

            # Calculate all metrics for this player-tournament
            metrics = _calculate_player_metrics(
                player,
                tournament,
                player_tournament_df,
                player_tournament_holes
            )
            rows.append(metrics)

    # Build DataFrame
    players_df = pd.DataFrame(rows)

    # Get unique tournaments for dropdown
    tournaments = sorted(filtered_df['Tournament'].unique())

    return {
        "empty": False,
        "players_df": players_df,
        "tournaments": tournaments,
        "column_groups": _get_column_groups(),
    }


def _get_column_groups():
    """Return the column grouping structure for the UI."""
    return {
        "basic": ["Player", "Tournament", "Rounds", "Avg Score"],
        "tiger5": ["T5 Fails/Rd", "3P/Rd", "DB/Rd", "P5B/Rd", "MG/Rd", "125B/Rd"],
        "scoring": ["SF/Rd", "BB%", "DO%", "GP%", "BT"],
        "total_sg": ["SG/Rd"],
        "driving": ["SGD/Rd", "Obs%", "Pen%", "FW%"],
        "approach": ["SGA/Rd", "GZ SG", "YZ SG", "RZ SG"],
        "short_game": ["SGSG/Rd", "SG25-50", "SG0-25"],
        "putting": ["SGP/Rd", "SG4-6", "SG7-10", "Lag%"],
        "other": ["SGO/Rd"]
    }
