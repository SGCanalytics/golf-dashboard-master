import pandas as pd

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


def _gir_flags(filtered_df):
    """Flag approach distance buckets with GIR < 50%."""
    approach = filtered_df[filtered_df['Shot Type'] == 'Approach'].copy()
    if approach.empty:
        return []

    approach['Starting Distance'] = pd.to_numeric(approach['Starting Distance'], errors='coerce')

    def bucket(d):
        if 50 <= d < 100:
            return "50\u2013100"
        elif 100 <= d < 150:
            return "100\u2013150"
        elif 150 <= d < 200:
            return "150\u2013200"
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
    Birdie opportunities: holes where the first putt started <= 20 ft.
    Conversions: of those, how many resulted in birdie or better.
    """
    putts = filtered_df[filtered_df['Shot Type'] == 'Putt'].copy()
    if putts.empty or hole_summary.empty:
        return {"opportunities": 0, "conversions": 0, "conversion_pct": 0.0}

    putts['Starting Distance'] = pd.to_numeric(putts['Starting Distance'], errors='coerce')

    # First putt on each hole
    first_putts = putts.sort_values('Shot').groupby(
        ['Player', 'Round ID', 'Hole']
    ).first().reset_index()

    # Opportunities: first putt within 20 ft
    opps = first_putts[first_putts['Starting Distance'] <= 20]
    opportunities = len(opps)

    if opportunities == 0:
        return {"opportunities": 0, "conversions": 0, "conversion_pct": 0.0}

    # Check which of those resulted in birdie or better
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


def _practice_priorities(weaknesses, tiger5_results, gir_flags, putting_flags):
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

    # GIR flags
    for gf in gir_flags:
        priorities.append(f"Improve GIR from {gf['bucket']} ({gf['gir_pct']:.0f}% current).")

    # Putting flags
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
                         tiger5_results, grit_score):
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

    # --- Red flags ---
    gir_flags = _gir_flags(filtered_df)
    sgf = _short_game_flags(filtered_df)
    pf = _putting_flags(filtered_df)

    # --- Decision making ---
    gyr = _green_yellow_red(filtered_df)
    ba = _bogey_avoidance(hole_summary)
    bo = _birdie_opportunities(filtered_df, hole_summary)

    # --- Round flow ---
    flow = _flow_metrics(hole_summary)

    # --- Practice priorities ---
    priorities = _practice_priorities(weaknesses, tiger5_results, gir_flags, pf)

    # --- Narrative ---
    summary = _coach_summary(strengths, weaknesses, grit_score, flow)

    return {
        "coach_summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "gir_flags": gir_flags,
        "short_game_flags": sgf,
        "putting_flags": pf,
        "green_yellow_red": gyr,
        "bogey_avoidance": ba,
        "birdie_opportunities": bo,
        "flow_metrics": flow,
        "practice_priorities": priorities,
        "sg_summary": sg_summary
    }
