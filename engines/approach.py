import pandas as pd

# ============================================================
# APPROACH ENGINE
# ============================================================

BUCKET_LABELS = ["50\u2013100", "100\u2013150", "150\u2013200", ">200"]


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


def build_approach_results(filtered_df, num_rounds):
    """
    Compute all approach analytics for the Approach tab.
    """

    df = filtered_df[filtered_df['Shot Type'] == 'Approach'].copy()
    num_approach = len(df)

    empty_hero = {b: {"total_sg": 0.0, "sg_per_shot": 0.0, "prox": 0.0} for b in BUCKET_LABELS}

    if num_approach == 0:
        return {
            "empty": True,
            "df": df,
            "total_sg": 0.0,
            "sg_per_round": 0.0,
            "hero_metrics": empty_hero,
            "bucket_table": pd.DataFrame(),
            "radar_df": pd.DataFrame(),
            "scatter_df": pd.DataFrame(),
            "heatmap_pivot": pd.DataFrame(),
            "trend_df": pd.DataFrame()
        }

    # Ensure distances are numeric
    df['Starting Distance'] = pd.to_numeric(df['Starting Distance'], errors='coerce')
    df['Ending Distance'] = pd.to_numeric(df['Ending Distance'], errors='coerce')

    # --- Basic SG ---
    total_sg = df['Strokes Gained'].sum()
    sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0

    # --- Bucket assignment ---
    df['Bucket'] = df['Starting Distance'].apply(_bucket)

    # --- Hero metrics per bucket ---
    hero_metrics = {}
    for b in BUCKET_LABELS:
        bdf = df[df['Bucket'] == b]
        if bdf.empty:
            hero_metrics[b] = {"total_sg": 0.0, "sg_per_shot": 0.0, "prox": 0.0}
        else:
            hero_metrics[b] = {
                "total_sg": bdf['Strokes Gained'].sum(),
                "sg_per_shot": bdf['Strokes Gained'].mean(),
                "prox": bdf['Ending Distance'].mean()
            }

    # --- Bucket table ---
    bucket_agg = df.groupby('Bucket').agg(
        Shots=('Strokes Gained', 'count'),
        **{'Total SG': ('Strokes Gained', 'sum')},
        **{'SG/Shot': ('Strokes Gained', 'mean')},
        **{'Avg Proximity': ('Ending Distance', 'mean')},
        GIR=('Ending Location', lambda x: (x == 'Green').sum())
    ).reset_index()

    if not bucket_agg.empty:
        bucket_agg['GIR %'] = bucket_agg.apply(
            lambda r: f"{r['GIR'] / r['Shots'] * 100:.0f}%" if r['Shots'] > 0 else "-", axis=1
        )

    bucket_table = bucket_agg

    # --- Radar data ---
    radar_rows = []
    for b in BUCKET_LABELS:
        bdf = df[df['Bucket'] == b]
        if bdf.empty:
            radar_rows.append({"Bucket": b, "SG/Shot": 0, "Proximity": 0, "GGIR%": 0})
        else:
            gir_pct = (bdf['Ending Location'] == 'Green').sum() / len(bdf) * 100
            radar_rows.append({
                "Bucket": b,
                "SG/Shot": bdf['Strokes Gained'].mean(),
                "Proximity": bdf['Ending Distance'].mean(),
                "GGIR%": gir_pct
            })
    radar_df = pd.DataFrame(radar_rows)

    # --- Scatter data ---
    scatter_df = df[['Starting Distance', 'Strokes Gained', 'Starting Location',
                     'Ending Distance', 'Ending Location']].copy()

    # --- Heatmap: SG/shot by bucket x starting location ---
    heatmap_data = df.groupby(['Bucket', 'Starting Location'])['Strokes Gained'].mean().reset_index()
    if not heatmap_data.empty:
        heatmap_pivot = heatmap_data.pivot_table(
            index='Starting Location',
            columns='Bucket',
            values='Strokes Gained',
            fill_value=0
        )
        # Reorder columns to match bucket order
        ordered_cols = [b for b in BUCKET_LABELS if b in heatmap_pivot.columns]
        heatmap_pivot = heatmap_pivot[ordered_cols]
    else:
        heatmap_pivot = pd.DataFrame()

    # --- Trend by round ---
    round_trend = df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        **{'Strokes Gained': ('Strokes Gained', 'sum')}
    ).reset_index()
    round_trend['Date'] = pd.to_datetime(round_trend['Date'])
    round_trend = round_trend.sort_values('Date')
    round_trend['Label'] = round_trend.apply(
        lambda r: f"{r['Date'].strftime('%m/%d/%y')} {r['Course']}", axis=1
    )

    return {
        "empty": False,
        "df": df,
        "total_sg": total_sg,
        "sg_per_round": sg_per_round,
        "hero_metrics": hero_metrics,
        "bucket_table": bucket_table,
        "radar_df": radar_df,
        "scatter_df": scatter_df,
        "heatmap_pivot": heatmap_pivot,
        "trend_df": round_trend
    }


################################
# AI Narrative
##############################
def approach_narrative(results):
    sg = results.get("sg_per_round", 0)
    hero = results.get("hero_metrics", {})

    lines = ["Approach Performance:"]

    if sg > 0.25:
        lines.append(f"- Excellent approach play, gaining {sg:.2f} strokes per round.")
    elif sg > 0:
        lines.append(f"- Slightly positive approach SG at {sg:.2f} per round.")
    else:
        lines.append(f"- Losing strokes on approach ({sg:.2f} per round).")

    for b in BUCKET_LABELS:
        m = hero.get(b, {})
        lines.append(f"- {b}: SG/Shot {m.get('sg_per_shot', 0):.3f}, Proximity {m.get('prox', 0):.1f} ft")

    return "\n".join(lines)
