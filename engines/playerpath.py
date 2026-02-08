import pandas as pd
from engines.overview import build_sg_separators

# ============================================================
# PLAYERPATH ENGINE — INTELLIGENCE LAYER
# ============================================================

# ============================================================
# MENTAL STRENGTH METRICS
# ============================================================

def _calculate_bounce_back(hole_summary):
    """
    Bounce Back: Recovery after mistakes.
    Opportunity: bogey or worse (score_to_par >= +1) on hole h, AND hole != 18
    Success: par or better (score_to_par <= 0) on hole h+1
    """
    if hole_summary.empty:
        return {"rate": 0.0, "opportunities": 0, "successes": 0}
    
    opportunities = 0
    successes = 0
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        round_sorted = round_df.sort_values('Hole').reset_index(drop=True)
        
        for i in range(len(round_sorted) - 1):  # Exclude last hole (18)
            hole = round_sorted.iloc[i]
            next_hole = round_sorted.iloc[i + 1]
            
            score_to_par_h = hole['Hole Score'] - hole['Par']
            score_to_par_next = next_hole['Hole Score'] - next_hole['Par']
            
            if score_to_par_h >= 1:  # Bogey or worse
                opportunities += 1
                if score_to_par_next <= 0:  # Par or better
                    successes += 1
    
    rate = (successes / opportunities * 100) if opportunities > 0 else 0.0
    return {"rate": rate, "opportunities": opportunities, "successes": successes}


def _calculate_drop_off(hole_summary):
    """
    Drop Off: Consecutive mistakes.
    Opportunity: bogey or worse (score_to_par >= +1) on hole h
    Event: bogey or worse (score_to_par >= +1) again on hole h+1
    """
    if hole_summary.empty:
        return {"rate": 0.0, "opportunities": 0, "events": 0}
    
    opportunities = 0
    events = 0
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        round_sorted = round_df.sort_values('Hole').reset_index(drop=True)
        
        for i in range(len(round_sorted) - 1):
            hole = round_sorted.iloc[i]
            next_hole = round_sorted.iloc[i + 1]
            
            score_to_par_h = hole['Hole Score'] - hole['Par']
            score_to_par_next = next_hole['Hole Score'] - next_hole['Par']
            
            if score_to_par_h >= 1:  # Bogey or worse
                opportunities += 1
                if score_to_par_next >= 1:  # Bogey or worse again
                    events += 1
    
    rate = (events / opportunities * 100) if opportunities > 0 else 0.0
    return {"rate": rate, "opportunities": opportunities, "events": events}


def _calculate_gas_pedal(hole_summary):
    """
    Gas Pedal: Capitalizing on strong play.
    Opportunity: birdie or better (score_to_par <= -1) on hole h
    Success: birdie or better (score_to_par <= -1) on hole h+1
    """
    if hole_summary.empty:
        return {"rate": 0.0, "opportunities": 0, "successes": 0}
    
    opportunities = 0
    successes = 0
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        round_sorted = round_df.sort_values('Hole').reset_index(drop=True)
        
        for i in range(len(round_sorted) - 1):
            hole = round_sorted.iloc[i]
            next_hole = round_sorted.iloc[i + 1]
            
            score_to_par_h = hole['Hole Score'] - hole['Par']
            score_to_par_next = next_hole['Hole Score'] - next_hole['Par']
            
            if score_to_par_h <= -1:  # Birdie or better
                opportunities += 1
                if score_to_par_next <= -1:  # Birdie or better again
                    successes += 1
    
    rate = (successes / opportunities * 100) if opportunities > 0 else 0.0
    return {"rate": rate, "opportunities": opportunities, "successes": successes}


def _calculate_bogey_train(hole_summary):
    """
    Bogey Train: Percentage of bogey+ holes that are part of streaks >= 2.
    Streaks cannot cross rounds.
    """
    if hole_summary.empty:
        return {"rate": 0.0, "bogey_train_holes": 0, "total_bogey_plus_holes": 0}
    
    bogey_train_holes = 0
    total_bogey_plus_holes = 0
    all_streak_holes = set()
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        round_sorted = round_df.sort_values('Hole').reset_index(drop=True)
        
        # Identify streaks of consecutive bogey+ holes
        current_streak = []
        streak_holes = []
        
        for i in range(len(round_sorted)):
            hole = round_sorted.iloc[i]
            score_to_par = hole['Hole Score'] - hole['Par']
            
            if score_to_par >= 1:  # Bogey or worse
                total_bogey_plus_holes += 1
                current_streak.append(i)
            else:
                # Streak ended
                if len(current_streak) >= 2:
                    streak_holes.extend(current_streak)
                current_streak = []
        
        # Check end-of-round streak
        if len(current_streak) >= 2:
            streak_holes.extend(current_streak)
        
        # Track holes in streaks
        for idx in streak_holes:
            hole_key = (rid, round_sorted.iloc[idx]['Hole'])
            all_streak_holes.add(hole_key)
    
    bogey_train_holes = len(all_streak_holes)
    rate = (bogey_train_holes / total_bogey_plus_holes * 100) if total_bogey_plus_holes > 0 else 0.0
    
    return {"rate": rate, "bogey_train_holes": bogey_train_holes, "total_bogey_plus_holes": total_bogey_plus_holes}


def _calculate_pressure_finish(filtered_df, hole_summary):
    """
    Pressure Finish: Performance on holes 16-18 vs baseline.
    Returns score_to_par and SG per hole for finish vs baseline.
    """
    if hole_summary.empty:
        return {
            "finish_score_to_par": 0.0,
            "baseline_score_to_par": 0.0,
            "finish_sg_per_hole": 0.0,
            "baseline_sg_per_hole": 0.0,
            "difference_score": 0.0,
            "difference_sg": 0.0
        }
    
    # Filter finish holes (16-18)
    finish_holes = hole_summary[hole_summary['Hole'].isin([16, 17, 18])]
    baseline_holes = hole_summary[~hole_summary['Hole'].isin([16, 17, 18])]
    
    if finish_holes.empty or baseline_holes.empty:
        return {
            "finish_score_to_par": 0.0,
            "baseline_score_to_par": 0.0,
            "finish_sg_per_hole": 0.0,
            "baseline_sg_per_hole": 0.0,
            "difference_score": 0.0,
            "difference_sg": 0.0
        }
    
    # Calculate score_to_par
    finish_holes = finish_holes.copy()
    finish_holes['score_to_par'] = finish_holes['Hole Score'] - finish_holes['Par']
    finish_score_to_par = finish_holes['score_to_par'].mean()
    
    baseline_holes = baseline_holes.copy()
    baseline_holes['score_to_par'] = baseline_holes['Hole Score'] - baseline_holes['Par']
    baseline_score_to_par = baseline_holes['score_to_par'].mean()
    
    # Calculate SG per hole
    finish_sg_total = finish_holes['total_sg'].sum()
    finish_sg_per_hole = finish_sg_total / len(finish_holes) if len(finish_holes) > 0 else 0.0
    
    baseline_sg_total = baseline_holes['total_sg'].sum()
    baseline_sg_per_hole = baseline_sg_total / len(baseline_holes) if len(baseline_holes) > 0 else 0.0
    
    return {
        "finish_score_to_par": finish_score_to_par,
        "baseline_score_to_par": baseline_score_to_par,
        "finish_sg_per_hole": finish_sg_per_hole,
        "baseline_sg_per_hole": baseline_sg_per_hole,
        "difference_score": finish_score_to_par - baseline_score_to_par,
        "difference_sg": finish_sg_per_hole - baseline_sg_per_hole
    }


def _calculate_early_round_composure(filtered_df, hole_summary):
    """
    Early Round Composure: Performance on holes 1-3 vs baseline.
    Returns score_to_par and SG per hole for start vs baseline.
    """
    if hole_summary.empty:
        return {
            "start_score_to_par": 0.0,
            "baseline_score_to_par": 0.0,
            "start_sg_per_hole": 0.0,
            "baseline_sg_per_hole": 0.0,
            "difference_score": 0.0,
            "difference_sg": 0.0
        }
    
    # Filter start holes (1-3)
    start_holes = hole_summary[hole_summary['Hole'].isin([1, 2, 3])]
    baseline_holes = hole_summary[~hole_summary['Hole'].isin([1, 2, 3])]
    
    if start_holes.empty or baseline_holes.empty:
        return {
            "start_score_to_par": 0.0,
            "baseline_score_to_par": 0.0,
            "start_sg_per_hole": 0.0,
            "baseline_sg_per_hole": 0.0,
            "difference_score": 0.0,
            "difference_sg": 0.0
        }
    
    # Calculate score_to_par
    start_holes = start_holes.copy()
    start_holes['score_to_par'] = start_holes['Hole Score'] - start_holes['Par']
    start_score_to_par = start_holes['score_to_par'].mean()
    
    baseline_holes = baseline_holes.copy()
    baseline_holes['score_to_par'] = baseline_holes['Hole Score'] - baseline_holes['Par']
    baseline_score_to_par = baseline_holes['score_to_par'].mean()
    
    # Calculate SG per hole
    start_sg_total = start_holes['total_sg'].sum()
    start_sg_per_hole = start_sg_total / len(start_holes) if len(start_holes) > 0 else 0.0
    
    baseline_sg_total = baseline_holes['total_sg'].sum()
    baseline_sg_per_hole = baseline_sg_total / len(baseline_holes) if len(baseline_holes) > 0 else 0.0
    
    return {
        "start_score_to_par": start_score_to_par,
        "baseline_score_to_par": baseline_score_to_par,
        "start_sg_per_hole": start_sg_per_hole,
        "baseline_sg_per_hole": baseline_sg_per_hole,
        "difference_score": start_score_to_par - baseline_score_to_par,
        "difference_sg": start_sg_per_hole - baseline_sg_per_hole
    }


def _calculate_mistake_penalty_index(filtered_df, hole_summary, tiger5_results):
    """
    Mistake Penalty Index: How expensive are mistakes?
    Average score_to_par on Tiger 5 fail holes vs "clean" holes.
    """
    if hole_summary.empty:
        return {
            "fail_holes_avg": 0.0,
            "clean_holes_avg": 0.0,
            "index": 0.0,
            "fail_holes_count": 0,
            "clean_holes_count": 0
        }
    
    # Identify all holes with Tiger 5 fails
    fail_hole_keys = set()
    tiger5_names = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']
    
    for stat_name in tiger5_names:
        info = tiger5_results.get(stat_name, {})
        if isinstance(info, dict) and 'detail_holes' in info:
            detail_holes = info['detail_holes']
            if not detail_holes.empty:
                for _, row in detail_holes.iterrows():
                    key = (row['Player'], row['Round ID'], row['Hole'])
                    fail_hole_keys.add(key)
    
    # Calculate averages
    hole_summary = hole_summary.copy()
    hole_summary['score_to_par'] = hole_summary['Hole Score'] - hole_summary['Par']
    hole_summary['hole_key'] = list(zip(hole_summary['Player'], hole_summary['Round ID'], hole_summary['Hole']))
    
    fail_holes = hole_summary[hole_summary['hole_key'].isin(fail_hole_keys)]
    clean_holes = hole_summary[~hole_summary['hole_key'].isin(fail_hole_keys)]
    
    fail_holes_avg = fail_holes['score_to_par'].mean() if not fail_holes.empty else 0.0
    clean_holes_avg = clean_holes['score_to_par'].mean() if not clean_holes.empty else 0.0
    
    index = fail_holes_avg - clean_holes_avg
    
    return {
        "fail_holes_avg": fail_holes_avg,
        "clean_holes_avg": clean_holes_avg,
        "index": index,
        "fail_holes_count": len(fail_holes),
        "clean_holes_count": len(clean_holes)
    }

def _analyze_sg_separators(filtered_df, num_rounds):
    """
    Identify which SG separators are causing most variance.
    Returns list of separators sorted by impact.
    """
    separators = build_sg_separators(filtered_df, num_rounds)
    
    # Sort by absolute value to find biggest impacts
    separators_sorted = sorted(separators, key=lambda x: abs(x[1]), reverse=True)
    
    return separators_sorted


def _extract_hero_card_insights(driving_results, approach_results, short_game_results, putting_results):
    """
    Extract key insights from hero cards across all tabs.
    """
    insights = {
        "driving": {},
        "approach": {},
        "short_game": {},
        "putting": {}
    }
    
    # Driving insights
    if driving_results.get('num_drives', 0) > 0:
        insights["driving"] = {
            "driving_sg": driving_results.get('driving_sg', 0.0),
            "non_playable_pct": driving_results.get('non_playable_pct', 0.0),
            "sg_playable": driving_results.get('sg_playable', 0.0)
        }
    
    # Approach insights
    if not approach_results.get('empty', True):
        insights["approach"] = {
            "total_sg": approach_results.get('total_sg', 0.0),
            "sg_fairway": approach_results.get('sg_fairway', 0.0),
            "sg_rough": approach_results.get('sg_rough', 0.0),
            "positive_shot_rate": approach_results.get('positive_shot_rate', 0.0)
        }
    
    # Short game insights
    if not short_game_results.get('empty', True):
        hero = short_game_results.get('hero_metrics', {})
        insights["short_game"] = {
            "sg_total": hero.get('sg_total', 0.0),
            "sg_arg": hero.get('sg_arg', 0.0),
            "pct_inside_8_fr": hero.get('pct_inside_8_fr', 0.0),
            "pct_inside_8_sand": hero.get('pct_inside_8_sand', 0.0)
        }
    
    # Putting insights
    if not putting_results.get('empty', True):
        hero = putting_results.get('hero_metrics', {})
        insights["putting"] = {
            "sg_total": hero.get('sg_total', 0.0),
            "sg_3_6": hero.get('sg_3_6', 0.0),
            "sg_7_10": hero.get('sg_7_10', 0.0),
            "lag_miss_pct": hero.get('lag_miss_pct', 0.0)
        }
    
    return insights


# ============================================================
# NARRATIVE GENERATION
# ============================================================

def _generate_game_overview_narrative(playerpath_data):
    """
    Generate structured game overview covering:
    1. Tiger 5 Performance Summary (total fails, highest fail category)
    2. Root Cause Analysis (what's driving poor performance)
    3. Hero Card Insights (which tabs to focus on based on root causes)
    4. Strokes Gained Separators Review (poor performance areas)
    """
    lines = []
    
    strengths = playerpath_data.get('strengths', [])
    weaknesses = playerpath_data.get('weaknesses', [])
    sg_summary = playerpath_data.get('sg_summary', {})
    tiger5_results = playerpath_data.get('tiger5_results', {})
    hero_insights = playerpath_data.get('hero_insights', {})
    sg_separators = playerpath_data.get('sg_separators', [])
    
    # ============================================================
    # SECTION 1: TIGER 5 PERFORMANCE SUMMARY
    # ============================================================
    tiger5_names = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']
    
    # Calculate total Tiger 5 fails
    total_fails = 0
    fail_counts = {}
    for name in tiger5_names:
        info = tiger5_results.get(name, {})
        if isinstance(info, dict):
            fails = info.get('fails', 0)
            fail_counts[name] = fails
            total_fails += fails
    
    # Find highest Tiger 5 fail
    highest_fail = None
    highest_count = 0
    for name, count in fail_counts.items():
        if count > highest_count:
            highest_count = count
            highest_fail = name
    
    # Add Tiger 5 summary to narrative
    lines.append("**Tiger 5 Performance Summary**")
    lines.append(f"Total Tiger 5 Fails: **{total_fails}**")
    
    if highest_fail and highest_count > 0:
        lines.append(f"Highest Tiger 5 Fail: **{highest_fail}** ({highest_count} failures)")
    
    # List all fail categories
    fail_parts = []
    for name, count in fail_counts.items():
        if count > 0:
            fail_parts.append(f"{name}: {count}")
    if fail_parts:
        lines.append(f"Breakdown: {', '.join(fail_parts)}")
    
    lines.append("")  # Add spacing
    
    # ============================================================
    # SECTION 2: ROOT CAUSE ANALYSIS
    # ============================================================
    lines.append("**Root Cause Analysis**")
    
    # Identify primary root causes based on fail counts
    primary_causes = []
    if fail_counts.get('3 Putts', 0) > 0:
        primary_causes.append("Putting (3 Putts)")
    if fail_counts.get('Double Bogey', 0) > 0:
        primary_causes.append("Scoring on difficult holes (Double Bogey)")
    if fail_counts.get('Par 5 Bogey', 0) > 0:
        primary_causes.append("Par 5 performance")
    if fail_counts.get('Missed Green', 0) > 0:
        primary_causes.append("Short Game (Missed Green)")
    if fail_counts.get('125yd Bogey', 0) > 0:
        primary_causes.append("Approach shots inside 125 yards")
    
    if primary_causes:
        lines.append(f"Primary concerns: {', '.join(primary_causes)}")
    else:
        lines.append("No significant Tiger 5 failures identified.")
    
    lines.append("")  # Add spacing
    
    # ============================================================
    # SECTION 3: HERO CARD INSIGHTS (FROM OTHER TABS)
    # ============================================================
    lines.append("**Hero Card Insights**")
    
    # Check each tab for insights based on root causes
    insights_parts = []
    
    # Putting insights (if 3 Putts is a concern)
    if fail_counts.get('3 Putts', 0) > 0:
        putting = hero_insights.get('putting', {})
        if putting:
            sg_3_6 = putting.get('sg_3_6', 0)
            lag_miss = putting.get('lag_miss_pct', 0)
            insights_parts.append(f"Putting: SG 3-6ft = {sg_3_6:+.2f}, Lag Miss % = {lag_miss:.0f}%")
    
    # Driving/Approach insights (if Double Bogey or 125yd Bogey are concerns)
    if fail_counts.get('Double Bogey', 0) > 0 or fail_counts.get('125yd Bogey', 0) > 0:
        driving = hero_insights.get('driving', {})
        approach = hero_insights.get('approach', {})
        if driving:
            non_playable = driving.get('non_playable_pct', 0)
            sg_playable = driving.get('sg_playable', 0)
            insights_parts.append(f"Driving: Non-Playable % = {non_playable:.0f}%, SG Playable = {sg_playable:+.2f}")
        if approach:
            sg_fairway = approach.get('sg_fairway', 0)
            sg_rough = approach.get('sg_rough', 0)
            insights_parts.append(f"Approach: SG Fairway = {sg_fairway:+.2f}, SG Rough = {sg_rough:+.2f}")
    
    # Short Game insights (if Missed Green is a concern)
    if fail_counts.get('Missed Green', 0) > 0:
        short_game = hero_insights.get('short_game', {})
        if short_game:
            sg_arg = short_game.get('sg_arg', 0)
            pct_inside_8 = short_game.get('pct_inside_8_fr', 0)
            insights_parts.append(f"Short Game: SG ARG = {sg_arg:+.2f}, % Inside 8ft = {pct_inside_8:.0f}%")
    
    if insights_parts:
        for part in insights_parts:
            lines.append(f"• {part}")
    else:
        lines.append("Review individual tabs for detailed hero card metrics.")
    
    lines.append("")  # Add spacing
    
    # ============================================================
    # SECTION 4: STROKES GAINED SEPARATORS REVIEW
    # ============================================================
    lines.append("**Strokes Gained Separators Review**")
    
    # Find separators with poor performance (negative values)
    poor_separators = [(label, val, pr) for label, val, pr in sg_separators if val < 0]
    
    if poor_separators:
        # Sort by most negative
        poor_separators.sort(key=lambda x: x[1])
        lines.append("Poor performance areas:")
        for label, val, pr in poor_separators[:5]:  # Top 5 worst
            lines.append(f"• {label}: {val:+.2f} ({pr:+.2f} per round)")
    else:
        lines.append("No significantly poor Strokes Gained separators identified.")
    
    return "\n".join(lines) if lines else "Analyzing your game data..."


def _generate_mental_strength_narrative(mental_metrics):
    """
    Generate narrative insights for mental strength characteristics.
    """
    lines = []
    
    bounce_back = mental_metrics.get('bounce_back', {})
    drop_off = mental_metrics.get('drop_off', {})
    gas_pedal = mental_metrics.get('gas_pedal', {})
    bogey_train = mental_metrics.get('bogey_train', {})
    pressure_finish = mental_metrics.get('pressure_finish', {})
    early_round = mental_metrics.get('early_round_composure', {})
    mistake_penalty = mental_metrics.get('mistake_penalty_index', {})
    
    # Bounce Back
    if bounce_back.get('opportunities', 0) > 0:
        rate = bounce_back['rate']
        if rate >= 30:
            lines.append(f"**Bounce Back:** Excellent recovery rate ({rate:.0f}%) — you consistently respond well after mistakes.")
        elif rate >= 20:
            lines.append(f"**Bounce Back:** Solid recovery rate ({rate:.0f}%) — good mental resilience.")
        else:
            lines.append(f"**Bounce Back:** Recovery rate ({rate:.0f}%) could improve — focus on resetting after mistakes.")
    
    # Drop Off
    if drop_off.get('opportunities', 0) > 0:
        rate = drop_off['rate']
        if rate <= 20:
            lines.append(f"**Drop Off:** Low consecutive mistake rate ({rate:.0f}%) — mistakes don't compound.")
        elif rate <= 35:
            lines.append(f"**Drop Off:** Moderate consecutive mistake rate ({rate:.0f}%) — watch for mistake clusters.")
        else:
            lines.append(f"**Drop Off:** High consecutive mistake rate ({rate:.0f}%) — mistakes tend to compound.")
    
    # Gas Pedal
    if gas_pedal.get('opportunities', 0) > 0:
        rate = gas_pedal['rate']
        if rate >= 40:
            lines.append(f"**Gas Pedal:** Strong momentum building ({rate:.0f}%) — you capitalize on strong play.")
        elif rate >= 25:
            lines.append(f"**Gas Pedal:** Moderate momentum building ({rate:.0f}%) — room to build on success.")
        else:
            lines.append(f"**Gas Pedal:** Low momentum building ({rate:.0f}%) — focus on maintaining strong play.")
    
    # Bogey Train
    train_rate = bogey_train.get('rate', 0)
    if train_rate >= 50:
        lines.append(f"**Bogey Trains:** High clustering ({train_rate:.0f}%) — bogeys come in streaks. Focus on breaking momentum.")
    elif train_rate >= 30:
        lines.append(f"**Bogey Trains:** Moderate clustering ({train_rate:.0f}%) — some streak tendency.")
    else:
        lines.append(f"**Bogey Trains:** Low clustering ({train_rate:.0f}%) — mistakes are isolated.")
    
    # Pressure Finish
    diff_score = pressure_finish.get('difference_score', 0)
    if diff_score <= -0.2:
        lines.append(f"**Pressure Finish:** Strong finish — performing {abs(diff_score):.2f} strokes better on holes 16-18.")
    elif diff_score >= 0.2:
        lines.append(f"**Pressure Finish:** Finish struggles — performing {diff_score:.2f} strokes worse on holes 16-18.")
    
    # Early Round Composure
    diff_start = early_round.get('difference_score', 0)
    if diff_start <= -0.2:
        lines.append(f"**Early Round:** Strong start — performing {abs(diff_start):.2f} strokes better on holes 1-3.")
    elif diff_start >= 0.2:
        lines.append(f"**Early Round:** Slow start — performing {diff_start:.2f} strokes worse on holes 1-3.")
    
    # Mistake Penalty Index
    penalty_index = mistake_penalty.get('index', 0)
    if penalty_index >= 1.5:
        lines.append(f"**Mistake Cost:** High penalty ({penalty_index:.2f} strokes) — mistakes are expensive. Focus on damage control.")
    elif penalty_index >= 0.5:
        lines.append(f"**Mistake Cost:** Moderate penalty ({penalty_index:.2f} strokes) — mistakes have reasonable impact.")
    else:
        lines.append(f"**Mistake Cost:** Low penalty ({penalty_index:.2f} strokes) — you recover well from mistakes.")
    
    return "\n".join(lines) if lines else "Analyzing mental strength characteristics..."


# ============================================================
# MAIN ENGINE FUNCTION
# ============================================================

def build_playerpath(filtered_df, hole_summary, driving_results, approach_results,
                     short_game_results, putting_results, tiger5_results, grit_score, num_rounds):
    """
    Master function that combines all analyses and returns structured data for the UI.
    """
    
    # Calculate score_to_par for hole_summary if not present
    if 'score_to_par' not in hole_summary.columns:
        hole_summary = hole_summary.copy()
        hole_summary['score_to_par'] = hole_summary['Hole Score'] - hole_summary['Par']
    
    # SG summary
    sg_summary = {
        "Driving": driving_results.get("driving_sg", 0),
        "Approach": approach_results.get("total_sg", 0),
        "Short Game": short_game_results.get("total_sg", 0),
        "Putting": putting_results.get("total_sg_putting", 0)
    }
    
    # Strengths and weaknesses
    strengths = [(cat, val) for cat, val in sg_summary.items() if val > 0]
    weaknesses = [(cat, val) for cat, val in sg_summary.items() if val < 0]
    strengths.sort(key=lambda x: x[1], reverse=True)
    weaknesses.sort(key=lambda x: x[1])
    
    # Mental strength metrics
    mental_metrics = {
        "bounce_back": _calculate_bounce_back(hole_summary),
        "drop_off": _calculate_drop_off(hole_summary),
        "gas_pedal": _calculate_gas_pedal(hole_summary),
        "bogey_train": _calculate_bogey_train(hole_summary),
        "pressure_finish": _calculate_pressure_finish(filtered_df, hole_summary),
        "early_round_composure": _calculate_early_round_composure(filtered_df, hole_summary),
        "mistake_penalty_index": _calculate_mistake_penalty_index(filtered_df, hole_summary, tiger5_results)
    }
    
    # Cross-tab analysis
    sg_separators = _analyze_sg_separators(filtered_df, num_rounds)
    hero_insights = _extract_hero_card_insights(
        driving_results, approach_results, short_game_results, putting_results
    )
    
    # Narrative generation - Build comprehensive playerpath_data
    playerpath_data = {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "sg_summary": sg_summary,
        "tiger5_results": tiger5_results,
        "grit_score": grit_score,
        "hero_insights": hero_insights,
        "sg_separators": sg_separators
    }
    
    narratives = {
        "game_overview": _generate_game_overview_narrative(playerpath_data),
        "mental_strength": None  # Removed - now using metric explanations only
    }
    
    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "sg_summary": sg_summary,
        "mental_metrics": mental_metrics,
        "hero_insights": hero_insights,
        "sg_separators": sg_separators,
        "narratives": narratives,
        "grit_score": grit_score,
        "tiger5_results": tiger5_results
    }
