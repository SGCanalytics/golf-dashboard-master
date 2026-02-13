import numpy as np
import pandas as pd
from ui.formatters import round_label

# ============================================================
# APPROACH ENGINE
# ============================================================

BUCKET_LABELS = ["50\u2013100", "100\u2013150", "150\u2013200", ">200"]
ROUGH_BUCKET_LABELS = ["<150", ">150"]


def _bucket(d):
    """Assign approach distance bucket using en-dash labels."""
    if 50 <= d < 100:
        return "50\u2013100"
    elif 100 <= d < 150:
        return "100\u2013150"
    elif 150 <= d < 200:
        return "150\u2013200"
    elif d >= 200:
        return ">200"
    return None


def _rough_bucket(d):
    """Assign rough-specific distance bucket."""
    if d < 150:
        return "<150"
    return ">150"


# Zone labels for performance analysis
ZONE_LABELS = ["Green Zone", "Yellow Zone", "Red Zone"]
ZONE_RANGES = {
    "Green Zone": "75-125",
    "Yellow Zone": "125-175",
    "Red Zone": "175-225"
}


def _zone_bucket(d):
    """
    Assign approach distance to performance zone.

    Zones:
    - Green Zone: 75-125 yards (short approach shots)
    - Yellow Zone: 125-175 yards (mid-range approach shots)
    - Red Zone: 175-225 yards (long approach shots)

    Shots outside these ranges (<75 or >=225) return None and are excluded.
    """
    if 75 <= d < 125:
        return "Green Zone"
    elif 125 <= d < 175:
        return "Yellow Zone"
    elif 175 <= d < 225:
        return "Red Zone"
    return None


def _compute_bucket_metrics(bdf):
    """Compute standard metrics for a bucket slice."""
    if bdf.empty:
        return {"total_sg": 0.0, "sg_per_shot": 0.0, "prox": 0.0,
                "green_hit_pct": 0.0, "shots": 0}
    shots = len(bdf)
    greens = (bdf['Ending Location'] == 'Green').sum()
    return {
        "total_sg": bdf['Strokes Gained'].sum(),
        "sg_per_shot": bdf['Strokes Gained'].mean(),
        "prox": bdf['Ending Distance'].mean(),
        "green_hit_pct": greens / shots * 100 if shots > 0 else 0.0,
        "shots": shots,
    }


def build_approach_results(filtered_df, num_rounds):
    """
    Compute all approach analytics for the Approach tab.
    """

    df = filtered_df[filtered_df['Shot Type'] == 'Approach'].copy()
    num_approach = len(df)

    empty_return = {
        "empty": True,
        "df": df,
        "total_sg": 0.0,
        "sg_per_round": 0.0,
        "sg_fairway": 0.0,
        "sg_rough": 0.0,
        "positive_shot_rate": 0.0,
        "poor_shot_rate": 0.0,
        "fairway_tee_metrics": {b: {"total_sg": 0.0, "sg_per_shot": 0.0,
                                     "prox": 0.0, "green_hit_pct": 0.0,
                                     "shots": 0} for b in BUCKET_LABELS},
        "rough_metrics": {b: {"total_sg": 0.0, "sg_per_shot": 0.0,
                               "prox": 0.0, "green_hit_pct": 0.0,
                               "shots": 0} for b in ROUGH_BUCKET_LABELS},
        "best_bucket": None,
        "worst_bucket": None,
        "profile_df": pd.DataFrame(),
        "heatmap_sg": pd.DataFrame(),
        "heatmap_counts": pd.DataFrame(),
        "outcome_df": pd.DataFrame(),
        "trend_df": pd.DataFrame(),
        "detail_df": pd.DataFrame(),
        "zone_metrics": {
            "Green Zone": {"total_sg": 0.0, "sg_per_shot": 0.0, "prox": 0.0,
                          "green_hit_pct": 0.0, "shots": 0},
            "Yellow Zone": {"total_sg": 0.0, "sg_per_shot": 0.0, "prox": 0.0,
                           "green_hit_pct": 0.0, "shots": 0},
            "Red Zone": {"total_sg": 0.0, "sg_per_shot": 0.0, "prox": 0.0,
                        "green_hit_pct": 0.0, "shots": 0}
        },
        "zone_ranges": ZONE_RANGES,
    }

    if num_approach == 0:
        return empty_return

    # Ensure distances are numeric
    df['Starting Distance'] = pd.to_numeric(df['Starting Distance'], errors='coerce')
    df['Ending Distance'] = pd.to_numeric(df['Ending Distance'], errors='coerce')

    # --- Basic SG ---
    total_sg = df['Strokes Gained'].sum()
    sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0

    # --- Section 1: Hero metrics ---
    fairway_df = df[df['Starting Location'] == 'Fairway']
    rough_df = df[df['Starting Location'] == 'Rough']

    sg_fairway = fairway_df['Strokes Gained'].sum() if not fairway_df.empty else 0.0
    sg_rough = rough_df['Strokes Gained'].sum() if not rough_df.empty else 0.0

    positive_shot_rate = (df['Strokes Gained'] >= 0.0).sum() / num_approach * 100
    poor_shot_rate = (df['Strokes Gained'] <= -0.15).sum() / num_approach * 100

    # --- Bucket assignment ---
    df['Bucket'] = df['Starting Distance'].apply(_bucket)

    # --- Section 2: Fairway/Tee performance by distance ---
    ft_df = df[df['Starting Location'].isin(['Fairway', 'Tee'])]
    fairway_tee_metrics = {}
    for b in BUCKET_LABELS:
        bdf = ft_df[ft_df['Bucket'] == b]
        fairway_tee_metrics[b] = _compute_bucket_metrics(bdf)

    # --- Section 2: Rough performance by distance ---
    rough_metrics = {}
    for rb in ROUGH_BUCKET_LABELS:
        if rb == "<150":
            bdf = rough_df[rough_df['Starting Distance'] < 150]
        else:
            bdf = rough_df[rough_df['Starting Distance'] >= 150]
        rough_metrics[rb] = _compute_bucket_metrics(bdf)

    # --- Zone Performance (all approach shots combined) ---
    df['Zone'] = df['Starting Distance'].apply(_zone_bucket)
    zone_metrics = {}

    for zone in ZONE_LABELS:
        zdf = df[df['Zone'] == zone]
        zone_metrics[zone] = _compute_bucket_metrics(zdf)

    # --- Section 2: Best / worst bucket by Total SG ---
    all_buckets = {}
    for b, m in fairway_tee_metrics.items():
        if m["shots"] > 0:
            all_buckets[f"FT|{b}"] = m["total_sg"]
    for b, m in rough_metrics.items():
        if m["shots"] > 0:
            all_buckets[f"R|{b}"] = m["total_sg"]

    best_bucket = max(all_buckets, key=all_buckets.get) if all_buckets else None
    worst_bucket = min(all_buckets, key=all_buckets.get) if all_buckets else None

    # --- Section 3: Approach Profile (horizontal bar chart data) ---
    profile_rows = []
    for b in BUCKET_LABELS:
        bdf = ft_df[ft_df['Bucket'] == b]
        m = _compute_bucket_metrics(bdf)
        profile_rows.append({
            "Category": f"{b}",
            "Group": "Fairway / Tee",
            "Green Hit %": m["green_hit_pct"],
            "Total SG": m["total_sg"],
            "Proximity": m["prox"],
        })
    for rb in ROUGH_BUCKET_LABELS:
        if rb == "<150":
            bdf = rough_df[rough_df['Starting Distance'] < 150]
        else:
            bdf = rough_df[rough_df['Starting Distance'] >= 150]
        m = _compute_bucket_metrics(bdf)
        profile_rows.append({
            "Category": f"{rb}",
            "Group": "Rough",
            "Green Hit %": m["green_hit_pct"],
            "Total SG": m["total_sg"],
            "Proximity": m["prox"],
        })
    profile_df = pd.DataFrame(profile_rows)

    # --- Section 4: Heatmap — Y=distance bucket, X=starting location ---
    loc_order = ['Tee', 'Fairway', 'Rough', 'Sand']
    heatmap_sg_data = df.groupby(['Bucket', 'Starting Location'])['Strokes Gained'].mean().reset_index()
    heatmap_cnt_data = df.groupby(['Bucket', 'Starting Location'])['Strokes Gained'].count().reset_index()
    heatmap_cnt_data.rename(columns={'Strokes Gained': 'Attempts'}, inplace=True)

    if not heatmap_sg_data.empty:
        heatmap_sg = heatmap_sg_data.pivot_table(
            index='Bucket', columns='Starting Location',
            values='Strokes Gained'
        )
        heatmap_counts = heatmap_cnt_data.pivot_table(
            index='Bucket', columns='Starting Location',
            values='Attempts', fill_value=0
        )
        # Reindex to consistent order; missing combos stay NaN for SG, 0 for counts
        ordered_cols = [c for c in loc_order if c in heatmap_sg.columns]
        bucket_order = [b for b in BUCKET_LABELS if b in heatmap_sg.index]
        heatmap_sg = heatmap_sg.reindex(index=bucket_order, columns=ordered_cols)
        heatmap_counts = heatmap_counts.reindex(index=bucket_order, columns=ordered_cols,
                                                 fill_value=0)
        # Cells with 0 attempts should be NaN in SG so heatmap renders them blank
        heatmap_sg = heatmap_sg.where(heatmap_counts > 0, other=np.nan)
    else:
        heatmap_sg = pd.DataFrame()
        heatmap_counts = pd.DataFrame()

    # --- Section 5: Outcome distribution by ending location ---
    outcome_agg = df.groupby('Ending Location').agg(
        Shots=('Strokes Gained', 'count'),
        **{'Total SG': ('Strokes Gained', 'sum')}
    ).reset_index()
    outcome_agg['Pct'] = outcome_agg['Shots'] / num_approach * 100
    outcome_df = outcome_agg.sort_values('Shots', ascending=False).reset_index(drop=True)

    # --- Section 6: Trend by round (unchanged) ---
    round_trend = df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        **{'Strokes Gained': ('Strokes Gained', 'sum')}
    ).reset_index()
    round_trend['Date'] = pd.to_datetime(round_trend['Date'])
    round_trend = round_trend.sort_values('Date')
    round_trend['Label'] = round_trend.apply(
        lambda r: round_label(r['Date'], r['Course']), axis=1
    )

    # --- Section 7: Shot detail table ---
    detail_df = df[['Player', 'Date', 'Course', 'Hole', 'Shot',
                     'Starting Distance', 'Starting Location',
                     'Ending Distance', 'Ending Location',
                     'Penalty', 'Strokes Gained']].copy()
    detail_df = detail_df.rename(columns={
        'Starting Location': 'Starting Lie',
        'Ending Location': 'Ending Lie',
    })
    detail_df = detail_df.sort_values(['Date', 'Course', 'Hole', 'Shot'],
                                       ascending=[False, True, True, True])

    return {
        "empty": False,
        "df": df,
        "total_sg": total_sg,
        "sg_per_round": sg_per_round,
        # Section 1
        "sg_fairway": sg_fairway,
        "sg_rough": sg_rough,
        "positive_shot_rate": positive_shot_rate,
        "poor_shot_rate": poor_shot_rate,
        # Section 2
        "fairway_tee_metrics": fairway_tee_metrics,
        "rough_metrics": rough_metrics,
        "best_bucket": best_bucket,
        "worst_bucket": worst_bucket,
        # Section 3
        "profile_df": profile_df,
        # Section 4
        "heatmap_sg": heatmap_sg,
        "heatmap_counts": heatmap_counts,
        # Section 5
        "outcome_df": outcome_df,
        # Section 6
        "trend_df": round_trend,
        # Section 7
        "detail_df": detail_df,
        # Section 8: Zone Performance
        "zone_metrics": zone_metrics,
        "zone_ranges": ZONE_RANGES,
    }


################################
# AI Narrative
##############################
def approach_narrative(results):
    sg = results.get("sg_per_round", 0)
    sg_fw = results.get("sg_fairway", 0)
    sg_rgh = results.get("sg_rough", 0)
    pos_rate = results.get("positive_shot_rate", 0)
    poor_rate = results.get("poor_shot_rate", 0)

    lines = ["Approach Performance:"]

    if sg > 0.25:
        lines.append(f"- Excellent approach play, gaining {sg:.2f} strokes per round.")
    elif sg > 0:
        lines.append(f"- Slightly positive approach SG at {sg:.2f} per round.")
    else:
        lines.append(f"- Losing strokes on approach ({sg:.2f} per round).")

    lines.append(f"- SG from Fairway: {sg_fw:.2f}, SG from Rough: {sg_rgh:.2f}")
    lines.append(f"- Positive shot rate: {pos_rate:.0f}%, Poor shot rate: {poor_rate:.0f}%")

    ft_metrics = results.get("fairway_tee_metrics", {})
    for b in BUCKET_LABELS:
        m = ft_metrics.get(b, {})
        lines.append(f"- Fairway/Tee {b}: SG/Shot {m.get('sg_per_shot', 0):.3f}, "
                     f"Proximity {m.get('prox', 0):.1f} ft")

    rough_metrics = results.get("rough_metrics", {})
    for b in ROUGH_BUCKET_LABELS:
        m = rough_metrics.get(b, {})
        lines.append(f"- Rough {b}: SG/Shot {m.get('sg_per_shot', 0):.3f}, "
                     f"Proximity {m.get('prox', 0):.1f} ft")

    return "\n".join(lines)
