import pandas as pd

from ui.theme import (
    POSITIVE, NEGATIVE, NEUTRAL, ACCENT_PRIMARY, SLATE,
    FONT_BODY, FONT_HEADING, CARD_RADIUS, CARD_PADDING
)

# ============================================================
# COACH'S CORNER ENGINE — COMPLETE OVERHAUL
# ============================================================


# ============================================================
# MENTAL METRICS CALCULATIONS
# ============================================================


def _bounce_back_rate(hole_summary):
    """
    Bounce Back Rate: 
    - Opportunity: bogey or worse (score_to_par >= +1) on hole h
    - Success: par or better (score_to_par <= 0) on hole h+1
    - Hole 18 bogey+ does NOT count (no next hole)
    """
    opp, success = 0, 0
    
    if hole_summary.empty:
        return {"rate": 0.0, "opportunities": 0, "successes": 0}
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        sorted_df = round_df.sort_values('Hole').reset_index(drop=True)
        
        for i in range(len(sorted_df) - 1):
            current_score = sorted_df.iloc[i]['Hole Score']
            current_par = sorted_df.iloc[i]['Par']
            next_score = sorted_df.iloc[i + 1]['Hole Score']
            next_par = sorted_df.iloc[i + 1]['Par']
            
            # Opportunity: bogey or worse on hole h (but not hole 18)
            if current_score >= current_par + 1:
                opp += 1
                # Success: par or better on hole h+1
                if next_score <= next_par:
                    success += 1
    
    rate = success / opp * 100 if opp > 0 else 0.0
    return {"rate": rate, "opportunities": opp, "successes": success}


def _drop_off_rate(hole_summary):
    """
    Drop-Off Rate:
    - Drop-Off Opportunity: bogey or worse (score_to_par >= +1) on hole h
    - Drop-Off Event: bogey or worse again on hole h+1
    """
    opp, events = 0, 0
    
    if hole_summary.empty:
        return {"rate": 0.0, "opportunities": 0, "events": 0}
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        sorted_df = round_df.sort_values('Hole').reset_index(drop=True)
        
        for i in range(len(sorted_df) - 1):
            prev_score = sorted_df.iloc[i]['Hole Score']
            prev_par = sorted_df.iloc[i]['Par']
            curr_score = sorted_df.iloc[i + 1]['Hole Score']
            curr_par = sorted_df.iloc[i + 1]['Par']
            
            # Opportunity: bogey or worse on previous hole
            if prev_score >= prev_par + 1:
                opp += 1
                # Event: bogey or worse on current hole
                if curr_score >= curr_par + 1:
                    events += 1
    
    rate = events / opp * 100 if opp > 0 else 0.0
    return {"rate": rate, "opportunities": opp, "events": events}


def _gas_pedal_rate(hole_summary):
    """
    Gas Pedal Rate:
    - Gas Pedal Opportunity: birdie or better (score_to_par <= -1) on hole h
    - Gas Pedal Success: birdie or better (score_to_par <= -1) on hole h+1
    Measures positive momentum.
    """
    opp, success = 0, 0
    
    if hole_summary.empty:
        return {"rate": 0.0, "opportunities": 0, "successes": 0}
    
    for rid, round_df in hole_summary.groupby('Round ID'):
        sorted_df = round_df.sort_values('Hole').reset_index(drop=True)
        
        for i in range(len(sorted_df) - 1):
            prev_score = sorted_df.iloc[i]['Hole Score']
            prev_par = sorted_df.iloc[i]['Par']
            curr_score = sorted_df.iloc[i + 1]['Hole Score']
            curr_par = sorted_df.iloc[i + 1]['Par']
            
            # Opportunity: birdie or better on previous hole
            if prev_score <= prev_par - 1:
                opp += 1
                # Success: birdie or better on current hole
                if curr_score <= curr_par - 1:
                    success += 1
    
    rate = success / opp * 100 if opp > 0 else 0.0
    return {"rate": rate, "opportunities": opp, "successes": success}


def _bogey_train_rate(hole_summary):
    """
    Bogey Train Rate (BTR):
    - BTR = bogey_train_holes / bogey_plus_holes
    - Bogey train streak: 2+ consecutive holes with score_to_par >= +1
    - Cannot cross rounds (hole 18 to hole 1 does NOT continue)
    """
    bogey_plus_holes = 0
    bogey_train_holes = 0
    all_trains = []
    
    if hole_summary.empty:
        return {"btr": 0.0, "bogey_plus": 0, "train_holes": 0, "trains": [], "longest": 0}
    
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
        
        # End of round check
        if current_train >= 2:
            bogey_train_holes += current_train
            all_trains.append(current_train)
    
    btr = bogey_train_holes / bogey_plus_holes * 100 if bogey_plus_holes > 0 else 0.0
    
    return {
        "btr": btr,
        "bogey_plus": bogey_plus_holes,
        "train_holes": bogey_train_holes,
        "trains": all_trains,
        "longest": max(all_trains) if all_trains else 0
    }


def _pressure_finish_performance(hole_summary, filtered_df):
    """
    Pressure Finish Performance:
    - Score relative to par on holes 16-18 vs baseline
    - SG per hole on holes 16-18 vs baseline SG per hole
    """
    # Holes 16-18
    finishing = hole_summary[hole_summary['Hole'].isin([16, 17, 18])]
    finish_holes = len(finishing)
    finish_score_to_par = (
        finishing['Hole Score'] - finishing['Par']
    ).sum() if finish_holes > 0 else 0
    
    # Baseline
    baseline_holes = len(hole_summary)
    baseline_score_to_par = (
        hole_summary['Hole Score'] - hole_summary['Par']
    ).sum() if baseline_holes > 0 else 0
    
    # SG calculation
    finish_shots = filtered_df[filtered_df['Hole'].isin([16, 17, 18])]
    finish_sg = pd.to_numeric(finish_shots['Strokes Gained'], errors='coerce').sum()
    
    baseline_sg = pd.to_numeric(
        filtered_df['Strokes Gained'], errors='coerce'
    ).sum()
    
    # Per-hole calculations
    finish_sg_per_hole = finish_sg / finish_holes if finish_holes > 0 else 0
    baseline_sg_per_hole = baseline_sg / baseline_holes if baseline_holes > 0 else 0
    
    # Score per hole
    finish_score_per_hole = finish_score_to_par / finish_holes if finish_holes > 0 else 0
    baseline_score_per_hole = baseline_score_to_par / baseline_holes if baseline_holes > 0 else 0
    
    return {
        "finish_score_to_par": finish_score_to_par,
        "finish_holes": finish_holes,
        "finish_sg": finish_sg,
        "finish_sg_per_hole": finish_sg_per_hole,
        "baseline_sg_per_hole": baseline_sg_per_hole,
        "sg_vs_baseline": finish_sg_per_hole - baseline_sg_per_hole,
        "finish_score_per_hole": finish_score_per_hole,
        "baseline_score_per_hole": baseline_score_per_hole,
        "score_vs_baseline": finish_score_per_hole - baseline_score_per_hole
    }


def _early_round_composure(hole_summary, filtered_df):
    """
    Early Round Composure:
    - Score relative to par on holes 1-3 vs baseline
    - SG per hole on holes 1-3 vs baseline
    """
    # Holes 1-3
    early = hole_summary[hole_summary['Hole'].isin([1, 2, 3])]
    early_holes = len(early)
    early_score_to_par = (
        early['Hole Score'] - early['Par']
    ).sum() if early_holes > 0 else 0
    
    # Baseline
    baseline_holes = len(hole_summary)
    baseline_score_to_par = (
        hole_summary['Hole Score'] - hole_summary['Par']
    ).sum() if baseline_holes > 0 else 0
    
    # SG calculation
    early_shots = filtered_df[filtered_df['Hole'].isin([1, 2, 3])]
    early_sg = pd.to_numeric(early_shots['Strokes Gained'], errors='coerce').sum()
    
    baseline_sg = pd.to_numeric(
        filtered_df['Strokes Gained'], errors='coerce'
    ).sum()
    
    # Per-hole calculations
    early_sg_per_hole = early_sg / early_holes if early_holes > 0 else 0
    baseline_sg_per_hole = baseline_sg / baseline_holes if baseline_holes > 0 else 0
    
    # Score per hole
    early_score_per_hole = early_score_to_par / early_holes if early_holes > 0 else 0
    baseline_score_per_hole = baseline_score_to_par / baseline_holes if baseline_holes > 0 else 0
    
    return {
        "early_score_to_par": early_score_to_par,
        "early_holes": early_holes,
        "early_sg": early_sg,
        "early_sg_per_hole": early_sg_per_hole,
        "baseline_sg_per_hole": baseline_sg_per_hole,
        "sg_vs_baseline": early_sg_per_hole - baseline_sg_per_hole,
        "early_score_per_hole": early_score_per_hole,
        "baseline_score_per_hole": baseline_score_per_hole,
        "score_vs_baseline": early_score_per_hole - baseline_score_per_hole
    }


def _mistake_penalty_index(hole_summary, tiger5_results):
    """
    Mistake Penalty Index (MPI):
    - Score relative to par on Tiger 5 fail holes vs clean holes
    - Measures: "When they make a mental mistake, how big is the damage?"
    """
    # Get T5 fail holes
    t5_fail_holes = set()
    tiger5_names = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']
    
    for name in tiger5_names:
        info = tiger5_results.get(name, {})
        if isinstance(info, dict) and 'detail_holes' in info:
            detail = info['detail_holes']
            if not detail.empty:
                for _, row in detail.iterrows():
                    t5_fail_holes.add((row['Round ID'], row['Hole']))
    
    # Calculate on T5 fail holes
    fail_mask = hole_summary.apply(
        lambda x: (x['Round ID'], x['Hole']) in t5_fail_holes, axis=1
    )
    fail_scores = hole_summary[fail_mask]
    fail_holes = len(fail_scores)
    fail_score_to_par = (
        fail_scores['Hole Score'] - fail_scores['Par']
    ).sum() if fail_holes > 0 else 0
    
    # Clean holes
    clean_mask = hole_summary.apply(
        lambda x: (x['Round ID'], x['Hole']) not in t5_fail_holes, axis=1
    )
    clean_scores = hole_summary[clean_mask]
    clean_holes = len(clean_scores)
    clean_score_to_par = (
        clean_scores['Hole Score'] - clean_scores['Par']
    ).sum() if clean_holes > 0 else 0
    
    # Per-hole calculations
    fail_per_hole = fail_score_to_par / fail_holes if fail_holes > 0 else 0
    clean_per_hole = clean_score_to_par / clean_holes if clean_holes > 0 else 0
    
    return {
        "fail_score_to_par": fail_score_to_par,
        "fail_holes": fail_holes,
        "clean_score_to_par": clean_score_to_par,
        "clean_holes": clean_holes,
        "fail_per_hole": fail_per_hole,
        "clean_per_hole": clean_per_hole,
        "penalty_index": fail_per_hole - clean_per_hole,
        "total_t5_fails": len(t5_fail_holes)
    }


# ============================================================
# DYNAMIC NARRATIVE GENERATORS
# ============================================================


def _generate_tiger5_narrative(tiger5_results, shot_type_counts):
    """
    Generate dynamic Tiger 5 root causes narrative.
    Similar structure to the Tiger 5 root cause analysis.
    """
    narrative = []
    
    if not shot_type_counts:
        return narrative
    
    sorted_causes = sorted(
        shot_type_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    total_fails = sum(shot_type_counts.values())
    
    # Main challenge bullet
    if sorted_causes[0][1] > 0:
        top_cause = sorted_causes[0]
        narrative.append({
            "type": "Primary Challenge",
            "title": f"{top_cause[0]} Vulnerability",
            "detail": f"{top_cause[1]} Tiger 5 fails linked to {top_cause[0].lower()}",
            "narrative": f"{top_cause[0]} is your biggest source of Tiger 5 mistakes, "
                        f"contributing to {top_cause[1]} failures across all categories."
        })
    
    # Secondary challenge
    if len(sorted_causes) > 1 and sorted_causes[1][1] > 0:
        second = sorted_causes[1]
        narrative.append({
            "type": "Secondary Issue",
            "title": f"{second[0]} Consistency",
            "detail": f"{second[1]} Tiger 5 fails from {second[0].lower()}",
            "narrative": f"{second[0]} also contributes to scoring issues, "
                        f"accounting for {second[1]} additional failures."
        })
    
    # Tertiary if exists
    if len(sorted_causes) > 2 and sorted_causes[2][1] > 0:
        third = sorted_causes[2]
        narrative.append({
            "type": "Tertiary Factor",
            "title": f"{third[0]} Management",
            "detail": f"{third[1]} fails from {third[0].lower()}",
            "narrative": f"Watch {third[0].lower()} situations to prevent compounding errors."
        })
    
    # Total context
    narrative.append({
        "type": "Total Impact",
        "title": "Tiger 5 Summary",
        "detail": f"{total_fails} total Tiger 5 failures",
        "narrative": f"Reducing Tiger 5 mistakes by just 50% could lower scores by "
                    f"{int(total_fails * 0.5)} strokes across your rounds."
    })
    
    return narrative


def _generate_game_overview_narrative(tiger5_results, sg_summary, 
                                      shot_type_counts, mental_metrics,
                                      tiger5_by_round_df):
    """
    Dynamically generate strengths and weaknesses narrative.
    Analyzes data patterns and explains WHY each factor matters.
    """
    strengths = []
    weaknesses = []
    
    # === TIGER 5 HERO CARDS ANALYSIS ===
    t5_analysis = []
    tiger5_names = ['3 Putts', 'Double Bogey', 'Par 5 Bogey', 'Missed Green', '125yd Bogey']
    
    for name in tiger5_names:
        data = tiger5_results.get(name, {})
        if isinstance(data, dict) and 'attempts' in data:
            attempts = data['attempts']
            fails = data['fails']
            success_rate = (attempts - fails) / attempts * 100 if attempts > 0 else 0
            t5_analysis.append({
                'category': name,
                'attempts': attempts,
                'fails': fails,
                'success_rate': success_rate
            })
    
    t5_sorted = sorted(t5_analysis, key=lambda x: x['success_rate'], reverse=True)
    
    # Dynamic strength: Top T5 performance
    if t5_sorted and t5_sorted[0]['success_rate'] >= 85 and t5_sorted[0]['attempts'] >= 2:
        best = t5_sorted[0]
        strengths.append({
            'type': 'Tiger 5 Hero',
            'title': f"{best['category']} Mastery",
            'detail': f"{best['success_rate']:.0f}% success rate "
                     f"({best['attempts'] - best['fails']}/{best['attempts']} clean)",
            'narrative': f"Your ability to avoid {best['category'].lower()} is exceptional. "
                        f"This discipline prevents big numbers and keeps rounds intact."
        })
    
    # Dynamic weakness: Worst T5
    if t5_sorted and t5_sorted[-1]['fails'] > 0:
        worst = t5_sorted[-1]
        weaknesses.append({
            'type': 'Tiger 5 Vulnerability',
            'title': f"{worst['category']} Challenge",
            'detail': f"{worst['fails']} failures "
                     f"({worst['success_rate']:.0f}% success rate)",
            'narrative': f"{worst['category']} is costing you strokes. "
                        f"Eliminating just one per round could drop your score by 1-2 strokes."
        })
    
    # === TIGER 5 ROOT CAUSES ANALYSIS ===
    root_sorted = sorted(shot_type_counts.items(), key=lambda x: x[1], reverse=True)
    
    if root_sorted and root_sorted[0][1] > 0:
        worst_root = root_sorted[0]  # Highest failure count
        weaknesses.append({
            'type': 'Root Cause Issue',
            'title': f"{worst_root[0]} Reliability",
            'detail': f"{worst_root[1]} Tiger 5 fails linked to {worst_root[0].lower()}",
            'narrative': f"{worst_root[0]} is your primary source of mistakes. "
                        f"Targeted practice on {worst_root[0].lower()} scenarios could yield immediate results."
        })
    
    if len(root_sorted) > 1 and root_sorted[-1][1] > 0:
        best_root = root_sorted[-1]  # Lowest failure count
        strengths.append({
            'type': 'Root Cause Strength',
            'title': f"{best_root[0]} Control",
            'detail': f"Only {best_root[1]} Tiger 5 fails originate from {best_root[0].lower()}",
            'narrative': f"You demonstrate excellent discipline in {best_root[0].lower()}, "
                        f"rarely letting it contribute to big mistakes."
        })
    
    # === STROKES GAINED ANALYSIS ===
    sg_positive = [(k, v) for k, v in sg_summary.items() if v > 0]
    sg_negative = [(k, v) for k, v in sg_summary.items() if v < 0]
    sg_positive.sort(key=lambda x: x[1], reverse=True)
    sg_negative.sort(key=lambda x: x[1])
    
    if sg_positive:
        best_sg = sg_positive[0]
        strengths.append({
            'type': 'SG Strength',
            'title': f"{best_sg[0]} Excellence",
            'detail': f"+{best_sg[1]:.2f} strokes gained",
            'narrative': f"Your {best_sg[0].lower()} is a true weapon, "
                        f"gaining {best_sg[1]:.2f} strokes on the field."
        })
    
    if sg_negative:
        worst_sg = sg_negative[0]
        if worst_sg[1] < -0.3:  # Threshold for concern
            weaknesses.append({
                'type': 'SG Weakness',
                'title': f"{worst_sg[0]} Opportunity",
                'detail': f"{worst_sg[1]:.2f} strokes lost",
                'narrative': f"{worst_sg[0]} is costing you strokes. "
                            f"Improving here could significantly lower your scores."
            })
    
    # === MENTAL METRICS ANALYSIS ===
    bounce_back = mental_metrics.get('bounce_back', {}).get('rate', 0)
    gas_pedal = mental_metrics.get('gas_pedal', {}).get('rate', 0)
    bogey_train = mental_metrics.get('bogey_train_rate', {}).get('btr', 0)
    mpi = mental_metrics.get('mistake_penalty', {}).get('penalty_index', 0)
    
    if bounce_back >= 25:
        strengths.append({
            'type': 'Mental Strength',
            'title': 'Resilience',
            'detail': f"{bounce_back:.0f}% bounce-back rate",
            'narrative': "After a mistake, you typically respond with quality play. "
                        "This mental resilience prevents small mistakes from becoming big numbers."
        })
    elif bounce_back > 0 and bounce_back < 15:
        weaknesses.append({
            'type': 'Mental Challenge',
            'title': 'Bounce Back',
            'detail': f"Only {bounce_back:.0f}% rate",
            'narrative': "Difficulty recovering after bad holes. "
                        "Focus on reset routines to prevent compounding errors."
        })
    
    if gas_pedal >= 30:
        strengths.append({
            'type': 'Mental Strength',
            'title': 'Positive Momentum',
            'detail': f"{gas_pedal:.0f}% gas pedal rate",
            'narrative': "You capitalize on good holes by following up with more quality play. "
                        "This momentum builds birdie chances and separates good rounds from great ones."
        })
    
    if bogey_train >= 50 and bogey_train > 0:
        weaknesses.append({
            'type': 'Mental Challenge',
            'title': 'Bogey Trains',
            'detail': f"{bogey_train:.0f}% bogey train rate",
            'narrative': "Bogeys tend to come in clusters. "
                        "Breaking the streak early is key to preventing big scores."
        })
    
    if mpi > 0.5:
        weaknesses.append({
            'type': 'Mental Challenge',
            'title': 'Mistake Amplification',
            'detail': f"+{mpi:.2f} penalty index",
            'narrative': "When you make a Tiger 5 mistake, the damage is amplified. "
                        "Focus on limiting the severity of mistakes to minimize scoring impact."
        })
    elif mpi <= 0 and mpi > -0.2:
        strengths.append({
            'type': 'Mental Strength',
            'title': 'Mistake Recovery',
            'detail': f"{mpi:.2f} penalty index",
            'narrative': "You limit the damage after mistakes. "
                        "This composure prevents big numbers from derailing rounds."
        })
    
    return {
        'strengths': strengths,
        'weaknesses': weaknesses
    }


def _generate_performance_drivers(tiger5_results, sg_summary, mental_metrics,
                                   shot_type_counts, hole_summary):
    """
    "Impress Me" section: Identify top 3 drivers of final score
    and provide actionable recommendations.
    """
    drivers = []
    
    # Calculate total Tiger 5 impact
    total_t5_fails = sum(
        v.get('fails', 0) for k, v in tiger5_results.items()
        if isinstance(v, dict) and k not in ['grit_score', 'by_round']
    )
    
    # Driver 1: Tiger 5 Discipline
    if total_t5_fails >= 2:
        impact_score = min(3, total_t5_fails / 2)  # Scale 0-3
        drivers.append({
            'rank': 1,
            'factor': 'Tiger 5 Discipline',
            'impact_score': impact_score,
            'detail': f"{total_t5_fails} Tiger 5 failures",
            'recommendation': 'Eliminate one Tiger 5 mistake per round through focused practice. '
                             'Review each failure for a common pattern.',
            'priority': 'HIGH'
        })
    
    # Driver 2: Primary SG Weakness
    if sg_summary:
        worst_sg = min(sg_summary.items(), key=lambda x: x[1])
        if worst_sg[1] < -0.5:
            drivers.append({
                'rank': 2,
                'factor': f"{worst_sg[0]} Performance",
                'impact_score': min(3, abs(worst_sg[1])),
                'detail': f"Losing {abs(worst_sg[1]):.2f} strokes in {worst_sg[0]}",
                'recommendation': f'Prioritize {worst_sg[0].lower()} practice. '
                                 f'Set specific targets for improvement.',
                'priority': 'HIGH' if abs(worst_sg[1]) > 1 else 'MEDIUM'
            })
    
    # Driver 3: Mental Flow (Bounce Back or Bogey Trains)
    bounce_back = mental_metrics.get('bounce_back', {}).get('rate', 50)
    bogey_train = mental_metrics.get('bogey_train_rate', {}).get('btr', 0)
    
    if bounce_back < 15:
        drivers.append({
            'rank': 3,
            'factor': 'Mental Resilience',
            'impact_score': 2,
            'detail': f"Only {bounce_back:.0f}% bounce-back rate",
            'recommendation': 'Develop a post-mistake routine. '
                             'Visualize success before the next shot.',
            'priority': 'MEDIUM'
        })
    elif bogey_train > 50:
        drivers.append({
            'rank': 3,
            'factor': 'Streak Management',
            'impact_score': 2,
            'detail': f"{bogey_train:.0f}% bogey train rate",
            'recommendation': 'Focus on getting "up and down" on the first bogey '
                             'to prevent streak continuation.',
            'priority': 'MEDIUM'
        })
    
    # Driver 4: Closing Ability
    finish_sg = mental_metrics.get('pressure_finish', {}).get('sg_vs_baseline', 0)
    if finish_sg < -0.2:
        drivers.append({
            'rank': 4,
            'factor': 'Pressure Finish',
            'impact_score': 1.5,
            'detail': f"{-finish_sg:.2f} SG drop on holes 16-18",
            'recommendation': 'Practice pressure putts and closing birdie chances. '
                             'Play "what if" scenarios on the practice green.',
            'priority': 'LOW'
        })
    
    # Sort by impact score and return top 3
    drivers.sort(key=lambda x: x['impact_score'], reverse=True)
    return drivers[:3]


# ============================================================
# SHOT CHARACTERISTICS
# ============================================================


def _shot_characteristics(filtered_df):
    """
    Build shot-level breakdown by characteristics.
    Returns tables for Recovery, Penalty, and Other shots.
    """
    # Recovery shots
    recovery = filtered_df[filtered_df['Starting Location'] == 'Recovery'].copy()
    if not recovery.empty:
        recovery['Category'] = 'Recovery'
        recovery = recovery[[
            'Hole', 'Shot', 'Shot Type', 'Starting Location',
            'Starting Distance', 'Ending Location', 'Ending Distance',
            'Strokes Gained', 'Category'
        ]].copy()
    
    # Penalty shots
    penalty = filtered_df[filtered_df['Penalty'] == 'Yes'].copy()
    if not penalty.empty:
        penalty['Category'] = 'Penalty'
        penalty = penalty[[
            'Hole', 'Shot', 'Shot Type', 'Starting Location',
            'Starting Distance', 'Ending Location', 'Ending Distance',
            'Strokes Gained', 'Category'
        ]].copy()
    
    # Other shots (exclude recovery and penalty)
    other = filtered_df[
        (filtered_df['Starting Location'] != 'Recovery') & 
        (filtered_df['Penalty'] != 'Yes')
    ].copy()
    if not other.empty:
        other['Category'] = 'Other'
        other = other[[
            'Hole', 'Shot', 'Shot Type', 'Starting Location',
            'Starting Distance', 'Ending Location', 'Ending Distance',
            'Strokes Gained', 'Category'
        ]].copy()
    
    # Aggregate stats
    def _aggregate_stats(df):
        if df.empty:
            return None
        sg_sum = pd.to_numeric(df['Strokes Gained'], errors='coerce').sum()
        return {
            'count': len(df),
            'sg_total': sg_sum,
            'sg_avg': sg_sum / len(df)
        }
    
    return {
        'recovery': {
            'data': recovery,
            'stats': _aggregate_stats(recovery)
        },
        'penalty': {
            'data': penalty,
            'stats': _aggregate_stats(penalty)
        },
        'other': {
            'data': other,
            'stats': _aggregate_stats(other)
        }
    }


# ============================================================
# LEGACY FUNCTIONS (Kept for backward compatibility)
# ============================================================


APPROACH_BUCKETS = ["50–100", "100–150", "150–200", ">200"]


def _strengths_weaknesses(sg_summary):
    """Return sorted (category, sg_value) tuples for strengths and weaknesses."""
    strengths = [(cat, val) for cat, val in sg_summary.items() if val > 0]
    weaknesses = [(cat, val) for cat, val in sg_summary.items() if val < 0]
    strengths.sort(key=lambda x: x[1], reverse=True)
    weaknesses.sort(key=lambda x: x[1])
    return strengths, weaknesses


def _gir_flags(filtered_df):
    """Flag approach distance buckets with GIR < 50%."""
    approach = filtered_df[filtered_df['Shot Type'] == 'Approach'].copy()
    if approach.empty:
        return []

    approach['Starting Distance'] = pd.to_numeric(approach['Starting Distance'], errors='coerce')

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

    approach['Bucket'] = approach['Starting Distance'].apply(bucket)
    flags = []
    for b in APPROACH_BUCKETS:
        bdf = approach[approach['Bucket'] == b]
        if bdf.empty:
            continue
        gir_pct = (bdf['Ending Location'] == 'Green').sum() / len(bdf) * 100
        if gir_pct < 50:
            flags.append({"bucket": b, "gir_pct": gir_pct})
    return flags


def _short_game_flags(filtered_df):
    """Compute % of short game shots landing inside 8 ft by lie type."""
    sg = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()
    if sg.empty:
        return {"inside8_fr_pct": 0.0, "inside8_sand_pct": 0.0}

    sg['Ending Distance'] = pd.to_numeric(sg['Ending Distance'], errors='coerce')

    fr = sg[sg['Starting Location'].isin(['Fairway', 'Rough'])]
    sand = sg[sg['Starting Location'] == 'Sand']

    fr_pct = (fr['Ending Distance'] <= 8).sum() / len(fr) * 100 if not fr.empty else 0.0
    sand_pct = (sand['Ending Distance'] <= 8).sum() / len(sand) * 100 if not sand.empty else 0.0

    return {"inside8_fr_pct": fr_pct, "inside8_sand_pct": sand_pct}


def _putting_flags(filtered_df):
    """Extract putting red flag metrics."""
    putts = filtered_df[filtered_df['Shot Type'] == 'Putt'].copy()
    if putts.empty:
        return {"make_45_pct": 0.0, "sg_510": 0.0, "lag_miss_pct": 0.0, "three_putts_inside_20": 0}

    putts['Starting Distance'] = pd.to_numeric(putts['Starting Distance'], errors='coerce')
    putts['Ending Distance'] = pd.to_numeric(putts['Ending Distance'], errors='coerce')
    putts['Made'] = (putts['Ending Distance'] == 0).astype(int)

    # Make % 4-5 ft
    m45 = putts[(putts['Starting Distance'] >= 4) & (putts['Starting Distance'] <= 5)]
    make_45_pct = m45['Made'].sum() / len(m45) * 100 if len(m45) > 0 else 0.0

    # SG 5-10 ft
    m510 = putts[(putts['Starting Distance'] >= 5) & (putts['Starting Distance'] <= 10)]
    sg_510 = m510['Strokes Gained'].sum() if not m510.empty else 0.0

    # Lag miss % (start >= 30 ft, leave > 5 ft)
    lag = putts[putts['Starting Distance'] >= 30]
    lag_miss_pct = (lag['Ending Distance'] > 5).sum() / len(lag) * 100 if not lag.empty else 0.0

    # 3-putts where first putt started <= 20 ft
    putts['Hole Key'] = (
        putts['Player'].astype(str) + '|' +
        putts['Round ID'].astype(str) + '|' +
        putts['Hole'].astype(str)
    )
    hole_putt_counts = putts.groupby('Hole Key').size()
    three_putt_holes = set(hole_putt_counts[hole_putt_counts >= 3].index)

    first_putts = putts.sort_values('Shot').groupby('Hole Key').first()
    three_putts_inside_20 = 0
    for hk in three_putt_holes:
        if hk in first_putts.index:
            if first_putts.loc[hk, 'Starting Distance'] <= 20:
                three_putts_inside_20 += 1

    return {
        "make_45_pct": make_45_pct,
        "sg_510": sg_510,
        "lag_miss_pct": lag_miss_pct,
        "three_putts_inside_20": three_putts_inside_20
    }


def _green_yellow_red(filtered_df):
    """DECADE-style shot classification by SG outcome."""
    sg_vals = filtered_df['Strokes Gained']
    green_sg = sg_vals[sg_vals > 0].sum()
    yellow_sg = sg_vals[(sg_vals >= -0.5) & (sg_vals <= 0)].sum()
    red_sg = sg_vals[sg_vals < -0.5].sum()

    return [
        {"light": "Green", "total_sg": green_sg},
        {"light": "Yellow", "total_sg": yellow_sg},
        {"light": "Red", "total_sg": red_sg}
    ]


def _bogey_avoidance(hole_summary):
    """Compute bogey rate overall and by par value."""
    result = {}

    if hole_summary.empty:
        for k in ["Overall", "Par3", "Par4", "Par5"]:
            result[k] = {"bogey_rate": 0.0}
        return result

    total_holes = len(hole_summary)
    bogey_holes = (hole_summary['Hole Score'] > hole_summary['Par']).sum()
    result["Overall"] = {"bogey_rate": bogey_holes / total_holes * 100 if total_holes > 0 else 0.0}

    for par_val, key in [(3, "Par3"), (4, "Par4"), (5, "Par5")]:
        par_df = hole_summary[hole_summary['Par'] == par_val]
        if par_df.empty:
            result[key] = {"bogey_rate": 0.0}
        else:
            bogeys = (par_df['Hole Score'] > par_df['Par']).sum()
            result[key] = {"bogey_rate": bogeys / len(par_df) * 100}

    return result


def _birdie_opportunities(filtered_df, hole_summary):
    """Birdie opportunities and conversions."""
    putts = filtered_df[filtered_df['Shot Type'] == 'Putt'].copy()
    if putts.empty or hole_summary.empty:
        return {"opportunities": 0, "conversions": 0, "conversion_pct": 0.0}

    putts['Starting Distance'] = pd.to_numeric(putts['Starting Distance'], errors='coerce')

    first_putts = putts.sort_values('Shot').groupby(
        ['Player', 'Round ID', 'Hole']
    ).first().reset_index()

    opps = first_putts[first_putts['Starting Distance'] <= 20]
    opportunities = len(opps)

    if opportunities == 0:
        return {"opportunities": 0, "conversions": 0, "conversion_pct": 0.0}

    opps_with_score = opps[['Player', 'Round ID', 'Hole']].merge(
        hole_summary[['Player', 'Round ID', 'Hole', 'Hole Score', 'Par']],
        on=['Player', 'Round ID', 'Hole'],
        how='left'
    )

    conversions = int((opps_with_score['Hole Score'] < opps_with_score['Par']).sum())
    conversion_pct = conversions / opportunities * 100

    return {
        "opportunities": opportunities,
        "conversions": conversions,
        "conversion_pct": conversion_pct
    }


def _practice_priorities(weaknesses, tiger5_results, gir_flags, putting_flags):
    """Generate prioritized practice recommendations."""
    priorities = []

    for cat, val in weaknesses:
        priorities.append(f"Focus on {cat.lower()} — losing {abs(val):.2f} strokes.")

    t5_categories = {k: v for k, v in tiger5_results.items() if isinstance(v, dict) and 'fails' in v}
    for name, data in t5_categories.items():
        if data['fails'] > 0:
            priorities.append(f"Reduce {name.lower()} ({data['fails']} failures).")

    for gf in gir_flags:
        priorities.append(f"Improve GIR from {gf['bucket']} ({gf['gir_pct']:.0f}% current).")

    if putting_flags.get("three_putts_inside_20", 0) > 0:
        priorities.append(
            f"Eliminate 3-putts inside 20 ft ({putting_flags['three_putts_inside_20']} occurrences)."
        )

    return priorities


def _coach_summary(strengths, weaknesses, grit_score, flow):
    """Build narrative summary text."""
    lines = []

    if grit_score >= 80:
        lines.append(f"Excellent grit score ({grit_score:.1f}%). Staying composed and avoiding big mistakes.")
    elif grit_score >= 60:
        lines.append(f"Solid grit score ({grit_score:.1f}%). Some room to tighten up costly errors.")
    else:
        lines.append(f"Grit score ({grit_score:.1f}%) indicates opportunities to reduce costly errors.")

    if strengths:
        top = strengths[0]
        lines.append(f"Top strength: {top[0]} ({top[1]:+.2f} SG).")

    if weaknesses:
        worst = weaknesses[0]
        lines.append(f"Biggest area for improvement: {worst[0]} ({worst[1]:+.2f} SG).")

    if flow.get("bounce_back_pct", 0) >= 20:
        lines.append(f"Good bounce-back rate ({flow['bounce_back_pct']:.0f}%) — recovers well after mistakes.")
    elif flow.get("bogey_train_count", 0) > 0:
        lines.append(
            f"Watch for bogey trains ({flow['bogey_train_count']} streaks, "
            f"longest {flow['longest_bogey_train']} holes)."
        )

    return " ".join(lines)


# ============================================================
# MASTER COACH'S CORNER ENGINE
# ============================================================


def build_coachs_corner(filtered_df, hole_summary,
                        driving_results, approach_results,
                        short_game_results, putting_results,
                        tiger5_results, grit_score,
                        tiger5_root_causes=None,
                        tiger5_by_round_df=None):
    """
    Complete Coach's Corner analysis with all new mental metrics.
    
    Returns comprehensive dict with all sections:
    - tiger5_narrative: Dynamic Tiger 5 root causes
    - mental_metrics: All mental characteristics
    - game_overview: Dynamic strength/weakness analysis
    - performance_drivers: Top 3 drivers with recommendations
    - shot_characteristics: Recovery, penalty, other breakdown
    - legacy: All existing metrics for compatibility
    """
    
    # --- SG summary ---
    sg_summary = {
        "Driving": driving_results.get("driving_sg", 0),
        "Approach": approach_results.get("total_sg", 0),
        "Short Game": short_game_results.get("total_sg", 0),
        "Putting": putting_results.get("total_sg_putting", 0)
    }
    
    strengths, weaknesses = _strengths_weaknesses(sg_summary)
    
    # --- Extract shot type counts from Tiger 5 root causes ---
    shot_type_counts = {}
    if tiger5_root_causes and isinstance(tiger5_root_causes, tuple):
        shot_type_counts = tiger5_root_causes[0] if tiger5_root_causes[0] else {}
    elif tiger5_root_causes and isinstance(tiger5_root_causes, dict):
        shot_type_counts = tiger5_root_causes
    
    # --- Calculate all mental metrics ---
    mental_metrics = {
        "bounce_back": _bounce_back_rate(hole_summary),
        "drop_off": _drop_off_rate(hole_summary),
        "gas_pedal": _gas_pedal_rate(hole_summary),
        "bogey_train_rate": _bogey_train_rate(hole_summary),
        "pressure_finish": _pressure_finish_performance(hole_summary, filtered_df),
        "early_round": _early_round_composure(hole_summary, filtered_df),
        "mistake_penalty": _mistake_penalty_index(hole_summary, tiger5_results)
    }
    
    # --- Generate dynamic narratives ---
    tiger5_narrative = _generate_tiger5_narrative(tiger5_results, shot_type_counts)
    
    game_overview = _generate_game_overview_narrative(
        tiger5_results, sg_summary, shot_type_counts, 
        mental_metrics, tiger5_by_round_df
    )
    
    performance_drivers = _generate_performance_drivers(
        tiger5_results, sg_summary, mental_metrics,
        shot_type_counts, hole_summary
    )
    
    # --- Shot characteristics ---
    shot_chars = _shot_characteristics(filtered_df)
    
    # --- Legacy metrics (kept for compatibility) ---
    gir_flags = _gir_flags(filtered_df)
    sgf = _short_game_flags(filtered_df)
    pf = _putting_flags(filtered_df)
    gyr = _green_yellow_red(filtered_df)
    ba = _bogey_avoidance(hole_summary)
    bo = _birdie_opportunities(filtered_df, hole_summary)
    priorities = _practice_priorities(weaknesses, tiger5_results, gir_flags, pf)
    summary = _coach_summary(strengths, weaknesses, grit_score, mental_metrics.get('bounce_back', {}))
    
    return {
        # === NEW SECTIONS ===
        "tiger5_narrative": tiger5_narrative,
        "mental_metrics": mental_metrics,
        "game_overview": game_overview,
        "performance_drivers": performance_drivers,
        "shot_characteristics": shot_chars,
        
        # === LEGACY SECTIONS ===
        "coach_summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "gir_flags": gir_flags,
        "short_game_flags": sgf,
        "putting_flags": pf,
        "green_yellow_red": gyr,
        "bogey_avoidance": ba,
        "birdie_opportunities": bo,
        "practice_priorities": priorities,
        "sg_summary": sg_summary
    }
