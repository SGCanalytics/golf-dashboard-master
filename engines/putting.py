import pandas as pd

# ============================================================
# PUTTING ENGINE 
# ============================================================

def _enrich_putting_df(filtered_df):
    """Filter to putts and add computed columns."""
    putting_df = filtered_df[filtered_df['Shot Type'] == 'Putt'].copy()
    if putting_df.empty:
        return putting_df

    putting_df['Starting Distance'] = pd.to_numeric(
        putting_df['Starting Distance'], errors='coerce'
    )
    putting_df['Ending Distance'] = pd.to_numeric(
        putting_df['Ending Distance'], errors='coerce'
    )
    putting_df['Made'] = (putting_df['Ending Distance'] == 0).astype(int)
    putting_df['Hole Key'] = (
        putting_df['Player'].astype(str) + '|' +
        putting_df['Round ID'].astype(str) + '|' +
        putting_df['Hole'].astype(str)
    )
    return putting_df


def build_putting_results(filtered_df, num_rounds):
    """
    Return a rich dict consumed by putting_tab and overview_engine.
    """
    putting_df = _enrich_putting_df(filtered_df)

    empty_hero = {
        "make_45_pct": 0.0, "sg_510": 0.0,
        "three_putts": 0, "lag_miss_pct": 0.0, "clutch_pct": 0.0
    }
    empty_lag = {"avg_leave": 0.0, "pct_inside_3": 0.0, "pct_over_5": 0.0}

    if putting_df.empty:
        return {
            "empty": True,
            "df": putting_df,
            "total_sg_putting": 0.0,
            "hero_metrics": empty_hero,
            "bucket_table": pd.DataFrame(),
            "lag_metrics": empty_lag,
            "trend_df": pd.DataFrame()
        }

    total_sg = putting_df['Strokes Gained'].sum()

    # --- Hero metrics ---
    # Make % 4-5 ft
    m45 = putting_df[(putting_df['Starting Distance'] >= 4) & (putting_df['Starting Distance'] <= 5)]
    make_45_pct = (m45['Made'].sum() / len(m45) * 100) if len(m45) > 0 else 0.0

    # SG 5-10 ft
    m510 = putting_df[(putting_df['Starting Distance'] >= 5) & (putting_df['Starting Distance'] <= 10)]
    sg_510 = m510['Strokes Gained'].sum() if not m510.empty else 0.0

    # 3-putts (count holes with 3+ putts)
    putt_counts = putting_df.groupby('Hole Key').size()
    three_putts = int((putt_counts >= 3).sum())

    # Lag miss % (putts starting >= 30 ft that leave > 5 ft)
    lag_putts = putting_df[putting_df['Starting Distance'] >= 30]
    if not lag_putts.empty:
        lag_miss_pct = (lag_putts['Ending Distance'] > 5).sum() / len(lag_putts) * 100
    else:
        lag_miss_pct = 0.0

    # Clutch % (birdie putts inside 10 ft — make %)
    clutch_putts = putting_df[putting_df['Starting Distance'] <= 10]
    clutch_pct = (clutch_putts['Made'].sum() / len(clutch_putts) * 100) if len(clutch_putts) > 0 else 0.0

    hero = {
        "make_45_pct": make_45_pct,
        "sg_510": sg_510,
        "three_putts": three_putts,
        "lag_miss_pct": lag_miss_pct,
        "clutch_pct": clutch_pct
    }

    # --- Bucket table ---
    bucket_table = putting_make_pct_by_distance(putting_df)

    # --- Lag metrics ---
    if not lag_putts.empty:
        lag_metrics = {
            "avg_leave": lag_putts['Ending Distance'].mean(),
            "pct_inside_3": (lag_putts['Ending Distance'] <= 3).sum() / len(lag_putts) * 100,
            "pct_over_5": (lag_putts['Ending Distance'] > 5).sum() / len(lag_putts) * 100
        }
    else:
        lag_metrics = empty_lag

    # --- Trend ---
    trend_df = putting_sg_by_round(putting_df)
    if not trend_df.empty:
        trend_df['Label'] = trend_df.apply(
            lambda r: f"{r['Date'].strftime('%m/%d')} {r['Course']}", axis=1
        )
        trend_df = trend_df.rename(columns={'SG_Putting': 'SG'})

    return {
        "empty": False,
        "df": putting_df,
        "total_sg_putting": total_sg,
        "hero_metrics": hero,
        "bucket_table": bucket_table,
        "lag_metrics": lag_metrics,
        "trend_df": trend_df
    }


# ============================================================
# PUTTING HERO METRICS
# ============================================================

def putting_hero_metrics(putting_df, num_rounds):
    """
    Compute high-level putting hero metrics:
        - Total SG Putting
        - Make % 4–5 ft
        - SG 5–10 ft
        - 3-Putts per round
        - Lag misses per round
    Returns a dict of metrics for easy card rendering.
    """
    metrics = {
        'total_sg_putting': 0.0,
        'make_pct_4_5': "-",
        'sg_5_10': 0.0,
        'three_putts_per_round': "-",
        'lag_misses_per_round': "-"
    }

    if putting_df.empty or num_rounds == 0:
        return metrics

    # Total SG Putting
    metrics['total_sg_putting'] = putting_df['Strokes Gained'].sum()

    # Make % 4–5 ft
    mask_4_5 = (putting_df['Starting Distance'] >= 4) & (putting_df['Starting Distance'] <= 5)
    subset_4_5 = putting_df[mask_4_5]
    if not subset_4_5.empty:
        attempts_4_5 = len(subset_4_5)
        makes_4_5 = subset_4_5['Made'].sum()
        metrics['make_pct_4_5'] = f"{makes_4_5 / attempts_4_5 * 100:.1f}%"

    # SG 5–10 ft
    mask_5_10 = (putting_df['Starting Distance'] >= 5) & (putting_df['Starting Distance'] <= 10)
    subset_5_10 = putting_df[mask_5_10]
    if not subset_5_10.empty:
        metrics['sg_5_10'] = subset_5_10['Strokes Gained'].sum()

    # 3-Putts per round
    hole_putt_counts = putting_df.groupby('Hole Key').agg(
        putts=('Score', 'max')
    ).reset_index()

    three_putt_holes = hole_putt_counts[hole_putt_counts['putts'] >= 3]
    metrics['three_putts_per_round'] = (
        f"{len(three_putt_holes) / num_rounds:.1f}"
    )

    # Lag misses per round (start >= 30 ft, end > 3 ft)
    lag_mask = (putting_df['Starting Distance'] >= 30) & (putting_df['Ending Distance'] > 3)
    lag_misses = putting_df[lag_mask]
    metrics['lag_misses_per_round'] = (
        f"{len(lag_misses) / num_rounds:.1f}"
    )

    return metrics


# ============================================================
# MAKE % TABLES
# ============================================================

def putting_make_pct_by_distance(putting_df, bins=None, labels=None):
    """
    Build a make % table by distance buckets.
    Returns DataFrame with:
        - Distance Bucket
        - Attempts
        - Makes
        - Make %
    """
    if putting_df.empty:
        return pd.DataFrame(columns=['Distance Bucket', 'Attempts', 'Makes', 'Make %'])

    if bins is None:
        bins = [0, 3, 5, 8, 10, 15, 20, 30, 1000]
    if labels is None:
        labels = ['0–3', '3–5', '5–8', '8–10', '10–15', '15–20', '20–30', '30+']

    df = putting_df.copy()
    df['Distance Bucket'] = pd.cut(
        df['Starting Distance'],
        bins=bins,
        labels=labels,
        right=False
    )

    grouped = df.groupby('Distance Bucket').agg(
        Attempts=('Made', 'count'),
        Makes=('Made', 'sum')
    ).reset_index()

    grouped['Make %'] = grouped.apply(
        lambda row: f"{row['Makes'] / row['Attempts'] * 100:.1f}%" if row['Attempts'] > 0 else "-",
        axis=1
    )

    return grouped


# ============================================================
# LAG SCATTER DATA
# ============================================================

def putting_lag_scatter_data(putting_df):
    """
    Prepare data for lag putting scatter:
        x = Starting Distance
        y = Ending Distance
        color = Strokes Gained or Made
    """
    if putting_df.empty:
        return putting_df

    return putting_df[['Starting Distance', 'Ending Distance', 'Strokes Gained', 'Made']].copy()


# ============================================================
# SG TREND BY ROUND
# ============================================================

def putting_sg_by_round(putting_df):
    """
    Compute SG Putting per round for trendline chart.
    Returns DataFrame with:
        Round ID, Date, Course, SG Putting
    """
    if putting_df.empty:
        return pd.DataFrame(columns=['Round ID', 'Date', 'Course', 'SG Putting'])

    grouped = putting_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        SG_Putting=('Strokes Gained', 'sum')
    ).reset_index()

    grouped['Date'] = pd.to_datetime(grouped['Date'])
    grouped = grouped.sort_values('Date')

    return grouped


# ============================================================
# CLUTCH INDEX
# ============================================================

def putting_clutch_index(putting_df):
    """
    Example clutch index:
        - Focus on putts inside 10 ft
        - Weight makes more when SG is high
    Returns a single float.
    """
    if putting_df.empty:
        return 0.0

    close_putts = putting_df[putting_df['Starting Distance'] <= 10].copy()
    if close_putts.empty:
        return 0.0

    made_close = close_putts[close_putts['Made'] == 1]
    if made_close.empty:
        return 0.0

    return made_close['Strokes Gained'].mean()

######################
#AI Narative
########################
def putting_narrative(results):
    sg = results.get("total_sg_putting", 0)
    make_4_5 = results.get("make_pct_4_5", "-")
    three_putts = results.get("three_putts_per_round", "-")
    lag_misses = results.get("lag_misses_per_round", "-")

    lines = ["Putting Performance:"]

    if sg > 0.25:
        lines.append(f"- Excellent putting, gaining {sg:.2f} strokes per round.")
    elif sg > 0:
        lines.append(f"- Slightly positive SG putting at {sg:.2f}.")
    else:
        lines.append(f"- Losing strokes on the greens ({sg:.2f}).")

    lines.append(f"- Make % from 4–5 ft: {make_4_5}.")
    lines.append(f"- 3-putts per round: {three_putts}.")
    lines.append(f"- Lag misses per round: {lag_misses}.")

    return "\n".join(lines)
