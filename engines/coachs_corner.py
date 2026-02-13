import pandas as pd

from engines.tiger5 import build_tiger5_root_cause

# ============================================================
# COACH'S CORNER ENGINE
# ============================================================

APPROACH_BUCKETS = ["50\u2013100", "100\u2013150", "150\u2013200", ">200"]


def _strengths_weaknesses(sg_summary):
    """Return sorted (category, sg_value) tuples for strengths and weaknesses."""
    strengths = [(cat, val) for cat, val in sg_summary.items() if val > 0]
    weaknesses = [(cat, val) for cat, val in sg_summary.items() if val < 0]
    strengths.sort(key=lambda x: x[1], reverse=True)
    weaknesses.sort(key=lambda x: x[1])
    return strengths, weaknesses


# Removed: _green_yellow_red() function - Green/Yellow/Red SG section has been removed
# def _green_yellow_red(filtered_df):
#     """DECADE-style shot classification by SG outcome."""
#     sg_vals = filtered_df['Strokes Gained']
#     green_sg = sg_vals[sg_vals > 0].sum()
#     yellow_sg = sg_vals[(sg_vals >= -0.5) & (sg_vals <= 0)].sum()
#     red_sg = sg_vals[sg_vals < -0.5].sum()
#
#     return [
#         {"light": "Green", "total_sg": green_sg},
#         {"light": "Yellow", "total_sg": yellow_sg},
#         {"light": "Red", "total_sg": red_sg}
#     ]


def _bogey_avoidance(hole_summary):
    """Compute bogey rate overall and by par value."""
    result = {}

    if hole_summary.empty:
        for k in ["Overall", "Par3", "Par4", "Par5"]:
            result[k] = {"bogey_rate": 0.0}
        return result

    # Overall
    total_holes = len(hole_summary)
    bogey_holes = (hole_summary['Hole Score'] > hole_summary['Par']).sum()
    result["Overall"] = {"bogey_rate": bogey_holes / total_holes * 100 if total_holes > 0 else 0.0}

    # By par
    for par_val, key in [(3, "Par3"), (4, "Par4"), (5, "Par5")]:
        par_df = hole_summary[hole_summary['Par'] == par_val]
        if par_df.empty:
            result[key] = {"bogey_rate": 0.0}
        else:
            bogeys = (par_df['Hole Score'] > par_df['Par']).sum()
            result[key] = {"bogey_rate": bogeys / len(par_df) * 100}

    return result


def _birdie_opportunities(filtered_df, hole_summary):
    """
    Birdie opportunities: holes where player reached green in regulation (GIR).
    GIR = first putt shot number <= par - 1

    Examples:
    - Par 3: First putt on shot 2 or less (reached green in 1 shot)
    - Par 4: First putt on shot 3 or less (reached green in 2 shots)
    - Par 5: First putt on shot 4 or less (reached green in 3 shots)

    Conversions: of those GIR holes, how many resulted in birdie or better.
    """
    putts = filtered_df[filtered_df['Shot Type'] == 'Putt'].copy()

    if putts.empty or hole_summary.empty:
        return {"opportunities": 0, "conversions": 0, "conversion_pct": 0.0}

    # Sort putts by hole and shot number
    putts = putts.sort_values(['Player', 'Round ID', 'Hole', 'Shot'])

    # Add putt sequence number for each hole (similar to putting engine pattern)
    # cumcount() starts at 0, so 0 = first putt, 1 = second putt, etc.
    putts['Putt Sequence'] = putts.groupby(
        ['Player', 'Round ID', 'Hole']
    ).cumcount()

    # Get only first putts (Putt Sequence == 0)
    # This preserves all columns including 'Shot'
    first_putts = putts[putts['Putt Sequence'] == 0].copy()

    # Merge with hole summary to get Hole Score ONLY (first_putts already has Par from original data)
    # This avoids duplicate 'Par' column conflict that was causing Shot column to be lost
    first_putts = first_putts.merge(
        hole_summary[['Player', 'Round ID', 'Hole', 'Hole Score']],
        on=['Player', 'Round ID', 'Hole'],
        how='left'
    )

    # Opportunities: first putt shot number <= par - 1 (Green in Regulation)
    # Shot and Par columns are guaranteed to be present (both from original putts data)
    opps = first_putts[first_putts['Shot'] <= first_putts['Par'] - 1]
    opportunities = len(opps)

    if opportunities == 0:
        return {"opportunities": 0, "conversions": 0, "conversion_pct": 0.0}

    # Conversions: birdie or better (Hole Score < Par)
    conversions = int((opps['Hole Score'] < opps['Par']).sum())
    conversion_pct = conversions / opportunities * 100

    return {
        "opportunities": opportunities,
        "conversions": conversions,
        "conversion_pct": conversion_pct
    }


def _flow_metrics(hole_summary):
    """
    Round flow analysis: bounce back, drop off, gas pedal, bogey trains.
    Analyzes consecutive holes within each round.
    """
    result = {
        "bounce_back_pct": 0.0,
        "drop_off_pct": 0.0,
        "gas_pedal_pct": 0.0,
        "bogey_train_count": 0,
        "longest_bogey_train": 0,
        "bogey_trains": []
    }

    if hole_summary.empty:
        return result

    bounce_back_attempts = 0
    bounce_back_successes = 0
    drop_off_attempts = 0
    drop_off_count = 0
    gas_pedal_attempts = 0
    gas_pedal_count = 0
    all_bogey_trains = []

    for rid, round_df in hole_summary.groupby('Round ID'):
        round_sorted = round_df.sort_values('Hole').reset_index(drop=True)
        scores = round_sorted['Hole Score'].values
        pars = round_sorted['Par'].values

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

            # Skip first hole — need previous hole for comparisons
            if i == 0:
                continue

            prev_bogey = scores[i - 1] > pars[i - 1]
            prev_birdie = scores[i - 1] < pars[i - 1]

            # Bounce back: bogey+ followed by birdie+
            if prev_bogey:
                bounce_back_attempts += 1
                if is_birdie_plus:
                    bounce_back_successes += 1

            # Drop off: birdie+ followed by bogey+
            if prev_birdie:
                drop_off_attempts += 1
                if is_bogey_plus:
                    drop_off_count += 1

            # Gas pedal: birdie+ followed by birdie+
            if prev_birdie:
                gas_pedal_attempts += 1
                if is_birdie_plus:
                    gas_pedal_count += 1

        # End-of-round train check
        if current_train >= 2:
            all_bogey_trains.append(current_train)

    result["bounce_back_pct"] = (
        bounce_back_successes / bounce_back_attempts * 100
        if bounce_back_attempts > 0 else 0.0
    )
    result["drop_off_pct"] = (
        drop_off_count / drop_off_attempts * 100
        if drop_off_attempts > 0 else 0.0
    )
    result["gas_pedal_pct"] = (
        gas_pedal_count / gas_pedal_attempts * 100
        if gas_pedal_attempts > 0 else 0.0
    )
    result["bogey_train_count"] = len(all_bogey_trains)
    result["longest_bogey_train"] = max(all_bogey_trains) if all_bogey_trains else 0
    result["bogey_trains"] = all_bogey_trains

    return result


def _practice_priorities(weaknesses, tiger5_results):
    """Generate prioritized practice recommendations."""
    priorities = []

    # SG weaknesses
    for cat, val in weaknesses:
        priorities.append(f"Focus on {cat.lower()} \u2014 losing {abs(val):.2f} strokes.")

    # Tiger 5 issues
    t5_categories = {k: v for k, v in tiger5_results.items() if isinstance(v, dict) and 'fails' in v}
    for name, data in t5_categories.items():
        if data['fails'] > 0:
            priorities.append(f"Reduce {name.lower()} ({data['fails']} failures).")

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
        lines.append(f"Good bounce-back rate ({flow['bounce_back_pct']:.0f}%) \u2014 recovers well after mistakes.")
    elif flow.get("bogey_train_count", 0) > 0:
        lines.append(
            f"Watch for bogey trains ({flow['bogey_train_count']} streaks, "
            f"longest {flow['longest_bogey_train']} holes)."
        )

    return " ".join(lines)


# ============================================================
# PERFORMANCE DRIVERS
# ============================================================

def _safe_pr(val, num_rounds):
    """Safe per-round calculation."""
    return val / num_rounds if num_rounds > 0 else 0.0


def _build_performance_drivers(num_rounds, filtered_df,
                                driving_results, approach_results,
                                short_game_results, putting_results):
    """
    Identify the top 3-5 granular factors costing the most strokes.

    Returns a list of dicts sorted by impact (most negative sg_per_round first):
        {category, label, sg_total, sg_per_round, detail, severity}
    """
    candidates = []

    # ---- DRIVING candidates ----
    # Penalty drives (combined penalty + OB)
    pen_sg = driving_results.get("penalty_sg", 0) + driving_results.get("ob_sg", 0)
    pen_cnt = driving_results.get("penalty_count", 0) + driving_results.get("ob_count", 0)
    if pen_sg < 0 and pen_cnt > 0:
        candidates.append({
            "category": "Driving",
            "label": "Penalty & OB Drives",
            "sg_total": pen_sg,
            "sg_per_round": _safe_pr(pen_sg, num_rounds),
            "detail": f"{pen_cnt} penalties/OB totalling {pen_sg:+.2f} SG",
        })

    # Poor drives (SG <= -0.15 on playable drives)
    poor_sg = driving_results.get("poor_drive_sg", 0)
    poor_pct = driving_results.get("poor_drive_pct", 0)
    if poor_sg < 0:
        candidates.append({
            "category": "Driving",
            "label": "Poor Playable Drives",
            "sg_total": poor_sg,
            "sg_per_round": _safe_pr(poor_sg, num_rounds),
            "detail": f"{poor_pct:.0f}% poor drive rate \u2014 {poor_sg:+.2f} SG total",
        })

    # Non-playable drives (sand/recovery/penalty)
    np_pct = driving_results.get("non_playable_pct", 0)
    obs_sg = driving_results.get("obstruction_sg", 0)
    if obs_sg < 0 and np_pct > 10:
        candidates.append({
            "category": "Driving",
            "label": "Non-Playable Drives",
            "sg_total": obs_sg,
            "sg_per_round": _safe_pr(obs_sg, num_rounds),
            "detail": f"{np_pct:.0f}% non-playable rate \u2014 obstruction SG {obs_sg:+.2f}",
        })

    # ---- APPROACH candidates (per bucket) ----
    ft_metrics = approach_results.get("fairway_tee_metrics", {})
    for bkt, m in ft_metrics.items():
        if m.get("shots", 0) >= 3 and m.get("total_sg", 0) < 0:
            candidates.append({
                "category": "Approach",
                "label": f"Approach {bkt} yds (Fairway)",
                "sg_total": m["total_sg"],
                "sg_per_round": _safe_pr(m["total_sg"], num_rounds),
                "detail": (f"GIR {m['green_hit_pct']:.0f}%, "
                           f"Prox {m['prox']:.1f} ft on {m['shots']} shots"),
            })

    rough_metrics = approach_results.get("rough_metrics", {})
    for bkt, m in rough_metrics.items():
        if m.get("shots", 0) >= 3 and m.get("total_sg", 0) < 0:
            candidates.append({
                "category": "Approach",
                "label": f"Approach {bkt} yds (Rough)",
                "sg_total": m["total_sg"],
                "sg_per_round": _safe_pr(m["total_sg"], num_rounds),
                "detail": (f"GIR {m['green_hit_pct']:.0f}%, "
                           f"Prox {m['prox']:.1f} ft on {m['shots']} shots"),
            })

    # ---- SHORT GAME candidates ----
    hero_sg = short_game_results.get("hero_metrics", {})

    sg_25_50 = hero_sg.get("sg_25_50", 0)
    if sg_25_50 < 0:
        candidates.append({
            "category": "Short Game",
            "label": "Short Game 25\u201350 yds",
            "sg_total": sg_25_50,
            "sg_per_round": _safe_pr(sg_25_50, num_rounds),
            "detail": f"Losing {abs(sg_25_50):.2f} SG from 25-50 yards",
        })

    sg_arg = hero_sg.get("sg_arg", 0)
    if sg_arg < 0:
        pct_fr = hero_sg.get("pct_inside_8_fr", 0)
        pct_sand = hero_sg.get("pct_inside_8_sand", 0)
        candidates.append({
            "category": "Short Game",
            "label": "Around the Green (<25 yds)",
            "sg_total": sg_arg,
            "sg_per_round": _safe_pr(sg_arg, num_rounds),
            "detail": f"Inside 8 ft: {pct_fr:.0f}% (FR), {pct_sand:.0f}% (Sand)",
        })

    # Sand-specific
    sand_df = filtered_df[
        (filtered_df['Shot Type'] == 'Short Game') &
        (filtered_df['Starting Location'] == 'Sand')
    ]
    if len(sand_df) >= 3:
        sand_sg = sand_df['Strokes Gained'].sum()
        if sand_sg < 0:
            candidates.append({
                "category": "Short Game",
                "label": "Sand Shots (Short Game)",
                "sg_total": sand_sg,
                "sg_per_round": _safe_pr(sand_sg, num_rounds),
                "detail": f"{len(sand_df)} sand shots \u2014 {sand_sg:+.2f} SG total",
            })

    # ---- PUTTING candidates ----
    put_hero = putting_results.get("hero_metrics", {})

    sg_3_6 = put_hero.get("sg_3_6", 0)
    if sg_3_6 < 0:
        made = put_hero.get("sg_3_6_made", 0)
        att = put_hero.get("sg_3_6_attempts", 0)
        candidates.append({
            "category": "Putting",
            "label": "Short Putts (3\u20136 ft)",
            "sg_total": sg_3_6,
            "sg_per_round": _safe_pr(sg_3_6, num_rounds),
            "detail": f"Made {made}/{att} \u2014 {sg_3_6:+.2f} SG",
        })

    sg_7_10 = put_hero.get("sg_7_10", 0)
    if sg_7_10 < 0:
        made = put_hero.get("sg_7_10_made", 0)
        att = put_hero.get("sg_7_10_attempts", 0)
        candidates.append({
            "category": "Putting",
            "label": "Mid-Range Putts (7\u201310 ft)",
            "sg_total": sg_7_10,
            "sg_per_round": _safe_pr(sg_7_10, num_rounds),
            "detail": f"Made {made}/{att} \u2014 {sg_7_10:+.2f} SG",
        })

    # Lag putting
    lag = putting_results.get("lag_metrics", {})
    pct_over_5 = lag.get("pct_over_5", 0)
    avg_leave = lag.get("avg_leave", 0)
    # Estimate lag SG from putts >= 20 ft
    put_df = putting_results.get("df", pd.DataFrame())
    if not put_df.empty:
        lag_putts = put_df[put_df['Starting Distance'] >= 20]
        lag_sg = lag_putts['Strokes Gained'].sum() if not lag_putts.empty else 0
    else:
        lag_sg = 0
    if lag_sg < 0:
        candidates.append({
            "category": "Putting",
            "label": "Lag Putting (20+ ft)",
            "sg_total": lag_sg,
            "sg_per_round": _safe_pr(lag_sg, num_rounds),
            "detail": f"Avg leave {avg_leave:.1f} ft, {pct_over_5:.0f}% leaving >5 ft",
        })

    # Differential putting (4-10 ft)
    if not put_df.empty:
        diff_putts = put_df[
            (put_df['Starting Distance'] >= 4) & (put_df['Starting Distance'] <= 10)
        ]
        diff_sg = diff_putts['Strokes Gained'].sum() if not diff_putts.empty else 0
    else:
        diff_sg = 0
    if diff_sg < 0 and abs(diff_sg) > abs(sg_3_6) and abs(diff_sg) > abs(sg_7_10):
        # Only add if it's worse than the individual ranges already captured
        pass  # Already captured by 3-6 and 7-10 buckets above

    # ---- RECOVERY / OTHER candidates ----
    for shot_type in ['Recovery', 'Other']:
        st_df = filtered_df[filtered_df['Shot Type'] == shot_type]
        if len(st_df) >= 3:
            st_sg = st_df['Strokes Gained'].sum()
            if st_sg < -0.5:
                candidates.append({
                    "category": shot_type,
                    "label": f"{shot_type} Shots",
                    "sg_total": st_sg,
                    "sg_per_round": _safe_pr(st_sg, num_rounds),
                    "detail": f"{len(st_df)} shots \u2014 {st_sg:+.2f} SG total",
                })

    # ---- Filter, sort, assign severity ----
    negative = [c for c in candidates if c["sg_total"] < 0]
    negative.sort(key=lambda x: x["sg_per_round"])

    for c in negative:
        pr = c["sg_per_round"]
        # Updated thresholds: ≤-2.0 critical, ≤-1.0 significant, >-1.0 moderate
        if pr <= -2.0:
            c["severity"] = "critical"
        elif pr <= -1.0:
            c["severity"] = "significant"
        else:
            c["severity"] = "moderate"

    return negative[:5]


# ============================================================
# TIGER 5 ROOT CAUSE DEEP DIVE
# ============================================================

def _build_tiger5_deep_dive(shot_type_counts, total_fails,
                             driving_results, approach_results,
                             short_game_results, putting_results):
    """
    For each Tiger 5 root cause category with fails > 0, diagnose the
    underlying issue using the corresponding tab's detailed metrics.

    Returns a list of dicts sorted by fail_count descending:
        {category, fail_count, pct_of_fails, key_metric_label,
         key_metric_value, sentiment, diagnosis, supporting_metrics}
    """
    results = []

    if total_fails == 0:
        return results

    # --- DRIVING ---
    d_count = shot_type_counts.get("Driving", 0)
    if d_count > 0:
        pen_count = driving_results.get("penalty_count", 0) + driving_results.get("ob_count", 0)
        np_pct = driving_results.get("non_playable_pct", 0)
        poor_pct = driving_results.get("poor_drive_pct", 0)
        fw_pct = driving_results.get("fairway_pct", 0)

        # Pick the most telling metric
        if pen_count > 0:
            key_label = "Penalties / OB"
            key_val = str(pen_count)
            diag = (f"Drive penalties and OB shots are a primary source of Tiger 5 "
                    f"failures. {pen_count} penalty events with "
                    f"{driving_results.get('penalty_sg', 0) + driving_results.get('ob_sg', 0):+.2f} SG impact.")
        elif np_pct > 15:
            key_label = "Non-Playable Rate"
            key_val = f"{np_pct:.0f}%"
            diag = (f"Too many drives finishing in sand, recovery, or penalty positions "
                    f"({np_pct:.0f}% non-playable), leading to difficult second shots.")
        else:
            key_label = "Poor Drive Rate"
            key_val = f"{poor_pct:.0f}%"
            diag = (f"Inconsistent driving with {poor_pct:.0f}% poor drives "
                    f"(SG \u2264 -0.15) creating scoring difficulties.")

        supporting = [
            {"label": "Fairway %", "value": f"{fw_pct:.0f}%"},
            {"label": "SG Driving", "value": f"{driving_results.get('driving_sg', 0):+.2f}"},
        ]
        if pen_count > 0:
            supporting.append({"label": "Penalty SG",
                               "value": f"{driving_results.get('penalty_sg', 0) + driving_results.get('ob_sg', 0):+.2f}"})

        results.append({
            "category": "Driving",
            "fail_count": d_count,
            "pct_of_fails": d_count / total_fails * 100,
            "key_metric_label": key_label,
            "key_metric_value": key_val,
            "sentiment": "negative",
            "diagnosis": diag,
            "supporting_metrics": supporting,
        })

    # --- APPROACH ---
    a_count = shot_type_counts.get("Approach", 0)
    if a_count > 0:
        worst_bucket = approach_results.get("worst_bucket")
        ft_metrics = approach_results.get("fairway_tee_metrics", {})
        r_metrics = approach_results.get("rough_metrics", {})

        # Find the worst bucket data
        if worst_bucket and "|" in str(worst_bucket):
            prefix, bkt = worst_bucket.split("|", 1)
            if prefix == "FT":
                m = ft_metrics.get(bkt, {})
                loc_str = "Fairway"
            else:
                m = r_metrics.get(bkt, {})
                loc_str = "Rough"
            gir = m.get("green_hit_pct", 0)
            prox = m.get("prox", 0)
            key_label = f"GIR from {loc_str} {bkt}"
            key_val = f"{gir:.0f}%"
            diag = (f"Approach shots from {loc_str.lower()} at {bkt} yds are the biggest "
                    f"issue \u2014 only {gir:.0f}% GIR with {prox:.1f} ft average proximity.")
        else:
            app_sg = approach_results.get("total_sg", 0)
            key_label = "SG Approach"
            key_val = f"{app_sg:+.2f}"
            diag = f"Approach play losing strokes overall ({app_sg:+.2f} SG total)."
            gir = 0

        supporting = [
            {"label": "SG Approach Total", "value": f"{approach_results.get('total_sg', 0):+.2f}"},
            {"label": "SG from Fairway", "value": f"{approach_results.get('sg_fairway', 0):+.2f}"},
            {"label": "SG from Rough", "value": f"{approach_results.get('sg_rough', 0):+.2f}"},
        ]

        results.append({
            "category": "Approach",
            "fail_count": a_count,
            "pct_of_fails": a_count / total_fails * 100,
            "key_metric_label": key_label,
            "key_metric_value": key_val,
            "sentiment": "negative",
            "diagnosis": diag,
            "supporting_metrics": supporting,
        })

    # --- SHORT GAME ---
    sg_count = shot_type_counts.get("Short Game", 0)
    if sg_count > 0:
        hero = short_game_results.get("hero_metrics", {})
        pct_fr = hero.get("pct_inside_8_fr", 0)
        pct_sand = hero.get("pct_inside_8_sand", 0)
        sg_arg = hero.get("sg_arg", 0)
        sg_25_50 = hero.get("sg_25_50", 0)

        # Determine worst metric
        if pct_sand < 40 and pct_sand < pct_fr:
            key_label = "Inside 8 ft (Sand)"
            key_val = f"{pct_sand:.0f}%"
            diag = (f"Sand saves are a major issue \u2014 only {pct_sand:.0f}% of sand "
                    f"shots finish inside 8 ft, leading to missed up-and-downs.")
        elif pct_fr < 50:
            key_label = "Inside 8 ft (FR)"
            key_val = f"{pct_fr:.0f}%"
            diag = (f"Short game shots from fairway/rough are leaving the ball too far "
                    f"from the hole ({pct_fr:.0f}% inside 8 ft).")
        elif abs(sg_25_50) > abs(sg_arg):
            key_label = "SG 25\u201350 yds"
            key_val = f"{sg_25_50:+.2f}"
            diag = f"Longer short game shots (25-50 yds) costing {abs(sg_25_50):.2f} strokes."
        else:
            key_label = "SG Around Green"
            key_val = f"{sg_arg:+.2f}"
            diag = f"Around-the-green performance losing {abs(sg_arg):.2f} strokes."

        supporting = [
            {"label": "SG Short Game", "value": f"{hero.get('sg_total', 0):+.2f}"},
            {"label": "Inside 8 ft (FR)", "value": f"{pct_fr:.0f}%"},
            {"label": "Inside 8 ft (Sand)", "value": f"{pct_sand:.0f}%"},
        ]

        results.append({
            "category": "Short Game",
            "fail_count": sg_count,
            "pct_of_fails": sg_count / total_fails * 100,
            "key_metric_label": key_label,
            "key_metric_value": key_val,
            "sentiment": "negative",
            "diagnosis": diag,
            "supporting_metrics": supporting,
        })

    # --- SHORT PUTTS ---
    sp_count = shot_type_counts.get("Short Putts", 0)
    if sp_count > 0:
        put_hero = putting_results.get("hero_metrics", {})
        sg_3_6 = put_hero.get("sg_3_6", 0)
        made = put_hero.get("sg_3_6_made", 0)
        att = put_hero.get("sg_3_6_attempts", 0)
        make_pct = (made / att * 100) if att > 0 else 0

        key_label = "Make % (3\u20136 ft)"
        key_val = f"{make_pct:.0f}%"
        diag = (f"Missing critical short putts \u2014 making {made}/{att} from "
                f"3-6 ft ({make_pct:.0f}%). These misses directly cause "
                f"Tiger 5 failures.")

        supporting = [
            {"label": "SG 3\u20136 ft", "value": f"{sg_3_6:+.2f}"},
            {"label": "Make % 0\u20133 ft", "value": f"{put_hero.get('make_0_3_pct', 0):.0f}%"},
        ]

        results.append({
            "category": "Short Putts",
            "fail_count": sp_count,
            "pct_of_fails": sp_count / total_fails * 100,
            "key_metric_label": key_label,
            "key_metric_value": key_val,
            "sentiment": "negative",
            "diagnosis": diag,
            "supporting_metrics": supporting,
        })

    # --- LAG PUTTS ---
    lp_count = shot_type_counts.get("Lag Putts", 0)
    if lp_count > 0:
        lag_m = putting_results.get("lag_metrics", {})
        avg_leave = lag_m.get("avg_leave", 0)
        pct_over_5 = lag_m.get("pct_over_5", 0)
        pct_inside_3 = lag_m.get("pct_inside_3", 0)

        key_label = "Avg Leave Distance"
        key_val = f"{avg_leave:.1f} ft"
        diag = (f"Poor distance control on lag putts \u2014 average leave of "
                f"{avg_leave:.1f} ft with {pct_over_5:.0f}% leaving over 5 ft. "
                f"This sets up three-putt opportunities.")

        supporting = [
            {"label": "% Inside 3 ft", "value": f"{pct_inside_3:.0f}%"},
            {"label": "% Over 5 ft", "value": f"{pct_over_5:.0f}%"},
            {"label": "Lag Miss %", "value": f"{putting_results.get('hero_metrics', {}).get('lag_miss_pct', 0):.0f}%"},
        ]

        results.append({
            "category": "Lag Putts",
            "fail_count": lp_count,
            "pct_of_fails": lp_count / total_fails * 100,
            "key_metric_label": key_label,
            "key_metric_value": key_val,
            "sentiment": "negative",
            "diagnosis": diag,
            "supporting_metrics": supporting,
        })

    results.sort(key=lambda x: x["fail_count"], reverse=True)
    return results


# ============================================================
# PLAYER PATH — STRENGTHS & WEAKNESSES WITH DRILL-DOWN
# ============================================================

def _build_player_path(sg_summary, num_rounds, filtered_df,
                        driving_results, approach_results,
                        short_game_results, putting_results):
    """
    Build detailed strengths and weaknesses with granular drill-down.

    Returns:
        {"strengths": [...], "weaknesses": [...]}
    Each item has: category, sg_total, sg_per_round, headline, detail_items
    """
    strengths = []
    weaknesses = []

    for cat, sg_val in sg_summary.items():
        sg_pr = _safe_pr(sg_val, num_rounds)
        entry = {
            "category": cat,
            "sg_total": sg_val,
            "sg_per_round": sg_pr,
            "headline": cat,
            "detail_items": [],
        }

        if cat == "Driving":
            entry["detail_items"] = _driving_detail(driving_results, sg_val > 0)
        elif cat == "Approach":
            entry["detail_items"] = _approach_detail(approach_results, sg_val > 0)
        elif cat == "Short Game":
            entry["detail_items"] = _short_game_detail(short_game_results, sg_val > 0)
        elif cat == "Putting":
            entry["detail_items"] = _putting_detail(putting_results, sg_val > 0)

        if sg_val > 0:
            strengths.append(entry)
        elif sg_val < 0:
            weaknesses.append(entry)

    # Check Recovery / Other shot types
    for shot_type in ["Recovery", "Other"]:
        st_df = filtered_df[filtered_df['Shot Type'] == shot_type]
        if len(st_df) >= 5:
            st_sg = st_df['Strokes Gained'].sum()
            st_pr = _safe_pr(st_sg, num_rounds)
            entry = {
                "category": shot_type,
                "sg_total": st_sg,
                "sg_per_round": st_pr,
                "headline": f"{shot_type} Shots",
                "detail_items": [
                    {"label": "Total Shots", "value": str(len(st_df)),
                     "sentiment": "neutral"},
                    {"label": "SG Total", "value": f"{st_sg:+.2f}",
                     "sentiment": "positive" if st_sg > 0 else "negative"},
                    {"label": "SG / Shot", "value": f"{st_df['Strokes Gained'].mean():+.3f}",
                     "sentiment": "positive" if st_df['Strokes Gained'].mean() > 0 else "negative"},
                ],
            }
            if st_sg > 0.5:
                strengths.append(entry)
            elif st_sg < -0.5:
                weaknesses.append(entry)

    strengths.sort(key=lambda x: x["sg_total"], reverse=True)
    weaknesses.sort(key=lambda x: x["sg_total"])

    return {"strengths": strengths, "weaknesses": weaknesses}


def _driving_detail(dr, is_strength):
    """Build detail items for driving based on whether it's a strength or weakness."""
    items = []
    fw_pct = dr.get("fairway_pct", 0)
    items.append({
        "label": "Fairway %",
        "value": f"{fw_pct:.0f}%",
        "sentiment": "positive" if fw_pct >= 50 else "negative",
    })

    np_pct = dr.get("non_playable_pct", 0)
    items.append({
        "label": "Non-Playable Rate",
        "value": f"{np_pct:.0f}%",
        "sentiment": "positive" if np_pct <= 15 else "negative",
    })

    if is_strength:
        items.append({
            "label": "Positive SG Rate",
            "value": f"{dr.get('positive_sg_pct', 0):.0f}%",
            "sentiment": "positive",
        })
        items.append({
            "label": "Distance P90",
            "value": f"{dr.get('driving_distance_p90', 0):.0f} yds",
            "sentiment": "accent",
        })
    else:
        pen_count = dr.get("penalty_count", 0) + dr.get("ob_count", 0)
        pen_sg = dr.get("penalty_sg", 0) + dr.get("ob_sg", 0)
        items.append({
            "label": "Penalties / OB",
            "value": f"{pen_count} ({pen_sg:+.2f} SG)",
            "sentiment": "negative" if pen_count > 0 else "neutral",
        })
        items.append({
            "label": "Poor Drive Rate",
            "value": f"{dr.get('poor_drive_pct', 0):.0f}%",
            "sentiment": "negative" if dr.get("poor_drive_pct", 0) > 20 else "positive",
        })
        avl_pct = dr.get("avoidable_loss_pct", 0)
        items.append({
            "label": "Avoidable Loss Rate",
            "value": f"{avl_pct:.0f}%",
            "sentiment": "negative" if avl_pct > 10 else "positive",
        })

    return items


def _approach_detail(ar, is_strength):
    """Build detail items for approach based on whether it's a strength or weakness."""
    items = []

    if is_strength:
        best = ar.get("best_bucket")
        if best and "|" in str(best):
            prefix, bkt = best.split("|", 1)
            loc = "Fairway" if prefix == "FT" else "Rough"
            metrics = ar.get("fairway_tee_metrics" if prefix == "FT" else "rough_metrics", {})
            m = metrics.get(bkt, {})
            items.append({
                "label": f"Best: {loc} {bkt}",
                "value": f"{m.get('total_sg', 0):+.2f} SG",
                "sentiment": "positive",
            })
            items.append({
                "label": f"GIR ({loc} {bkt})",
                "value": f"{m.get('green_hit_pct', 0):.0f}%",
                "sentiment": "positive",
            })

        items.append({
            "label": "Positive Shot Rate",
            "value": f"{ar.get('positive_shot_rate', 0):.0f}%",
            "sentiment": "positive" if ar.get("positive_shot_rate", 0) >= 50 else "neutral",
        })
    else:
        worst = ar.get("worst_bucket")
        if worst and "|" in str(worst):
            prefix, bkt = worst.split("|", 1)
            loc = "Fairway" if prefix == "FT" else "Rough"
            metrics = ar.get("fairway_tee_metrics" if prefix == "FT" else "rough_metrics", {})
            m = metrics.get(bkt, {})
            items.append({
                "label": f"Worst: {loc} {bkt}",
                "value": f"{m.get('total_sg', 0):+.2f} SG",
                "sentiment": "negative",
            })
            items.append({
                "label": f"GIR ({loc} {bkt})",
                "value": f"{m.get('green_hit_pct', 0):.0f}%",
                "sentiment": "negative" if m.get("green_hit_pct", 0) < 50 else "neutral",
            })

        # Fairway vs Rough differential
        sg_fw = ar.get("sg_fairway", 0)
        sg_rgh = ar.get("sg_rough", 0)
        items.append({
            "label": "SG from Fairway",
            "value": f"{sg_fw:+.2f}",
            "sentiment": "positive" if sg_fw > 0 else "negative",
        })
        items.append({
            "label": "SG from Rough",
            "value": f"{sg_rgh:+.2f}",
            "sentiment": "positive" if sg_rgh > 0 else "negative",
        })
        items.append({
            "label": "Poor Shot Rate",
            "value": f"{ar.get('poor_shot_rate', 0):.0f}%",
            "sentiment": "negative" if ar.get("poor_shot_rate", 0) > 20 else "positive",
        })

    return items


def _short_game_detail(sgr, is_strength):
    """Build detail items for short game."""
    hero = sgr.get("hero_metrics", {})
    items = []

    pct_fr = hero.get("pct_inside_8_fr", 0)
    pct_sand = hero.get("pct_inside_8_sand", 0)

    items.append({
        "label": "Inside 8 ft (FR)",
        "value": f"{pct_fr:.0f}%",
        "sentiment": "positive" if pct_fr >= 60 else "negative",
    })
    items.append({
        "label": "Inside 8 ft (Sand)",
        "value": f"{pct_sand:.0f}%",
        "sentiment": "positive" if pct_sand >= 40 else "negative",
    })

    sg_25_50 = hero.get("sg_25_50", 0)
    sg_arg = hero.get("sg_arg", 0)

    if is_strength:
        # Highlight what's working
        if sg_arg > sg_25_50:
            items.append({
                "label": "SG Around Green",
                "value": f"{sg_arg:+.2f}",
                "sentiment": "positive",
            })
        else:
            items.append({
                "label": "SG 25\u201350 yds",
                "value": f"{sg_25_50:+.2f}",
                "sentiment": "positive",
            })
    else:
        # Highlight what's losing strokes
        if sg_25_50 < sg_arg:
            items.append({
                "label": "SG 25\u201350 yds",
                "value": f"{sg_25_50:+.2f}",
                "sentiment": "negative" if sg_25_50 < 0 else "neutral",
            })
        else:
            items.append({
                "label": "SG Around Green",
                "value": f"{sg_arg:+.2f}",
                "sentiment": "negative" if sg_arg < 0 else "neutral",
            })

        # Check heatmap for worst cell
        hm = sgr.get("heatmap_sg_pivot", pd.DataFrame())
        if not hm.empty:
            # Find the worst performing cell
            min_val = None
            min_lie = None
            min_dist = None
            for lie in hm.index:
                for dist_bkt in hm.columns:
                    val = hm.loc[lie, dist_bkt]
                    if pd.notna(val) and (min_val is None or val < min_val):
                        min_val = val
                        min_lie = lie
                        min_dist = dist_bkt
            if min_val is not None and min_val < -0.1:
                items.append({
                    "label": f"Worst: {min_lie} {min_dist}",
                    "value": f"{min_val:+.2f} SG/shot",
                    "sentiment": "negative",
                })

    return items


def _putting_detail(pr, is_strength):
    """Build detail items for putting."""
    hero = pr.get("hero_metrics", {})
    lag = pr.get("lag_metrics", {})
    items = []

    if is_strength:
        sg_3_6 = hero.get("sg_3_6", 0)
        items.append({
            "label": "SG 3\u20136 ft",
            "value": f"{sg_3_6:+.2f} ({hero.get('sg_3_6_made', 0)}/{hero.get('sg_3_6_attempts', 0)})",
            "sentiment": "positive" if sg_3_6 >= 0 else "neutral",
        })
        items.append({
            "label": "Make % 0\u20133 ft",
            "value": f"{hero.get('make_0_3_pct', 0):.0f}%",
            "sentiment": "positive" if hero.get("make_0_3_pct", 0) >= 95 else "neutral",
        })
        items.append({
            "label": "% Inside 3 ft (Lag)",
            "value": f"{lag.get('pct_inside_3', 0):.0f}%",
            "sentiment": "positive" if lag.get("pct_inside_3", 0) >= 50 else "neutral",
        })
    else:
        # Short putts
        sg_3_6 = hero.get("sg_3_6", 0)
        items.append({
            "label": "SG 3\u20136 ft",
            "value": f"{sg_3_6:+.2f} ({hero.get('sg_3_6_made', 0)}/{hero.get('sg_3_6_attempts', 0)})",
            "sentiment": "negative" if sg_3_6 < 0 else "positive",
        })

        # Mid-range putts
        sg_7_10 = hero.get("sg_7_10", 0)
        items.append({
            "label": "SG 7\u201310 ft",
            "value": f"{sg_7_10:+.2f} ({hero.get('sg_7_10_made', 0)}/{hero.get('sg_7_10_attempts', 0)})",
            "sentiment": "negative" if sg_7_10 < 0 else "positive",
        })

        # Lag putting
        items.append({
            "label": "Lag Miss %",
            "value": f"{hero.get('lag_miss_pct', 0):.0f}%",
            "sentiment": "negative" if hero.get("lag_miss_pct", 0) > 20 else "positive",
        })
        items.append({
            "label": "Avg Leave (20+ ft)",
            "value": f"{lag.get('avg_leave', 0):.1f} ft",
            "sentiment": "negative" if lag.get("avg_leave", 0) > 5 else "positive",
        })

    return items


# ============================================================
# MASTER COACH'S CORNER ENGINE
# ============================================================

def build_coachs_corner(filtered_df, hole_summary,
                         driving_results, approach_results,
                         short_game_results, putting_results,
                         tiger5_results, grit_score, num_rounds):
    """
    Combine all engines into a single coaching insight package.
    """

    # --- SG summary ---
    sg_summary = {
        "Driving": driving_results.get("driving_sg", 0),
        "Approach": approach_results.get("total_sg", 0),
        "Short Game": short_game_results.get("total_sg", 0),
        "Putting": putting_results.get("total_sg_putting", 0)
    }

    strengths, weaknesses = _strengths_weaknesses(sg_summary)

    # --- Decision making ---
    # gyr = _green_yellow_red(filtered_df)  # REMOVED
    ba = _bogey_avoidance(hole_summary)
    bo = _birdie_opportunities(filtered_df, hole_summary)

    # --- Round flow ---
    flow = _flow_metrics(hole_summary)

    # --- Practice priorities ---
    priorities = _practice_priorities(weaknesses, tiger5_results)

    # --- Narrative ---
    summary = _coach_summary(strengths, weaknesses, grit_score, flow)

    # --- Performance Drivers (NEW) ---
    perf_drivers = _build_performance_drivers(
        num_rounds, filtered_df,
        driving_results, approach_results,
        short_game_results, putting_results,
    )

    # --- Tiger 5 Root Cause Deep Dive — REMOVED ---
    # shot_type_counts, detail_by_type = build_tiger5_root_cause(
    #     filtered_df, tiger5_results, hole_summary,
    # )
    # total_fails = sum(v for v in shot_type_counts.values())
    # tiger5_deep_dive = _build_tiger5_deep_dive(
    #     shot_type_counts, total_fails,
    #     driving_results, approach_results,
    #     short_game_results, putting_results,
    # )

    # --- PlayerPath (NEW) ---
    player_path = _build_player_path(
        sg_summary, num_rounds, filtered_df,
        driving_results, approach_results,
        short_game_results, putting_results,
    )

    return {
        "coach_summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        # "green_yellow_red": gyr,  # REMOVED
        "bogey_avoidance": ba,
        "birdie_opportunities": bo,
        "flow_metrics": flow,
        "practice_priorities": priorities,
        "sg_summary": sg_summary,
        "grit_score": grit_score,
        # NEW sections
        "performance_drivers": perf_drivers,
        # "tiger5_deep_dive": tiger5_deep_dive,  # REMOVED
        # "tiger5_root_cause_counts": shot_type_counts,  # REMOVED
        "player_path": player_path,
    }
