import pandas as pd
from engines.helpers import safe_divide
from ui.formatters import round_label

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

    # Putt ordinal within each hole (1st putt, 2nd putt, etc.)
    putting_df = putting_df.sort_values(['Hole Key', 'Shot'])
    putting_df['Putt Number'] = putting_df.groupby('Hole Key').cumcount() + 1

    # Total putts on the hole (joined back to every row)
    putting_df['Putts On Hole'] = putting_df.groupby('Hole Key')['Shot'].transform('count')

    return putting_df


# ============================================================
# HERO METRICS
# ============================================================

def _build_hero_metrics(putting_df, num_rounds):
    """Compute the five hero card metrics."""
    sg_total = putting_df['Strokes Gained'].sum()
    sg_per_round = safe_divide(sg_total, num_rounds)

    # SG Putting 4-6 ft
    m46 = putting_df[
        (putting_df['Starting Distance'] >= 4) &
        (putting_df['Starting Distance'] <= 6)
    ]
    sg_4_6 = m46['Strokes Gained'].sum() if not m46.empty else 0.0
    sg_4_6_made = int(m46['Made'].sum()) if not m46.empty else 0
    sg_4_6_attempts = len(m46)

    # SG Putting 7-10 ft
    m710 = putting_df[
        (putting_df['Starting Distance'] >= 7) &
        (putting_df['Starting Distance'] <= 10)
    ]
    sg_7_10 = m710['Strokes Gained'].sum() if not m710.empty else 0.0
    sg_7_10_made = int(m710['Made'].sum()) if not m710.empty else 0
    sg_7_10_attempts = len(m710)

    # Lag Miss % — first putts >= 20 ft that leave > 5 ft
    first_putts = putting_df[putting_df['Putt Number'] == 1]
    lag_first = first_putts[first_putts['Starting Distance'] >= 20]
    lag_miss_pct = (
        safe_divide((lag_first['Ending Distance'] > 5).sum(), len(lag_first)) * 100
    )

    # Make % 0-3 ft
    m03 = putting_df[
        (putting_df['Starting Distance'] > 0) &
        (putting_df['Starting Distance'] <= 3)
    ]
    make_0_3_pct = safe_divide(m03['Made'].sum(), len(m03)) * 100
    make_0_3_made = int(m03['Made'].sum()) if not m03.empty else 0
    make_0_3_attempts = len(m03)

    return {
        "sg_total": sg_total,
        "sg_per_round": sg_per_round,
        "sg_4_6": sg_4_6,
        "sg_4_6_made": sg_4_6_made,
        "sg_4_6_attempts": sg_4_6_attempts,
        "sg_7_10": sg_7_10,
        "sg_7_10_made": sg_7_10_made,
        "sg_7_10_attempts": sg_7_10_attempts,
        "lag_miss_pct": lag_miss_pct,
        "make_0_3_pct": make_0_3_pct,
        "make_0_3_made": make_0_3_made,
        "make_0_3_attempts": make_0_3_attempts,
    }


# ============================================================
# BUCKET TABLE (Section 2 — table)
# ============================================================

def _build_bucket_table(putting_df):
    """Make %, SG, and attempts by distance bucket."""
    if putting_df.empty:
        return pd.DataFrame(
            columns=['Distance Bucket', 'Attempts', 'SG', 'Makes', 'Make %']
        )

    bins = [0, 4, 7, 11, 21, 31, 1000]
    labels = ['0–3', '4–6', '7–10', '10–20', '20–30', '30+']

    df = putting_df.copy()
    df['Distance Bucket'] = pd.cut(
        df['Starting Distance'],
        bins=bins,
        labels=labels,
        right=False,
    )

    grouped = df.groupby('Distance Bucket', observed=False).agg(
        Attempts=('Made', 'count'),
        SG=('Strokes Gained', 'sum'),
        Makes=('Made', 'sum'),
    ).reset_index()

    grouped['Make %'] = grouped.apply(
        lambda row: f"{safe_divide(row['Makes'], row['Attempts']) * 100:.1f}%"
        if row['Attempts'] > 0 else "-",
        axis=1,
    )
    grouped['SG'] = grouped['SG'].apply(lambda x: f"{x:+.2f}")

    return grouped


# ============================================================
# PUTT OUTCOME CHART DATA (Section 2 — dual-axis chart)
# ============================================================

def _build_outcome_chart_data(putting_df):
    """
    Stacked bar (1-putt / 2-putt / 3+ %) plus SG line, grouped by
    first-putt starting distance.

    Note: Outcome distribution uses first-putt distance, but SG is calculated
    from ALL putts at each distance (putt-level, not hole-level) to match
    the stat cards above.
    """
    if putting_df.empty:
        return pd.DataFrame()

    first_putts = putting_df[putting_df['Putt Number'] == 1].copy()
    if first_putts.empty:
        return pd.DataFrame()

    bins = [0, 4, 7, 11, 21, 31, 1000]
    labels = ['0–3', '4–6', '7–10', '10–20', '20–30', '30+']

    first_putts['Distance Bucket'] = pd.cut(
        first_putts['Starting Distance'],
        bins=bins,
        labels=labels,
        right=False,
    )

    # Classify hole outcome by total putts on the hole
    first_putts['Outcome'] = first_putts['Putts On Hole'].apply(
        lambda x: '1-Putt' if x == 1 else ('2-Putt' if x == 2 else '3+ Putt')
    )

    # Calculate SG using ALL putts (putt-level), not hole-level
    # This matches the stat cards calculation method
    all_putts = putting_df.copy()
    all_putts['Distance Bucket'] = pd.cut(
        all_putts['Starting Distance'],
        bins=bins,
        labels=labels,
        right=False,
    )

    # Sum SG by distance bucket for all putts
    sg_by_bucket = all_putts.groupby('Distance Bucket', observed=False)['Strokes Gained'].sum().to_dict()

    # Aggregate by bucket
    rows = []
    for bucket in labels:
        bucket_df = first_putts[first_putts['Distance Bucket'] == bucket]
        total_holes = len(bucket_df)
        if total_holes == 0:
            rows.append({
                'Distance Bucket': bucket,
                'pct_1putt': 0, 'pct_2putt': 0, 'pct_3plus': 0,
                'sg': 0.0, 'holes': 0,
            })
            continue

        rows.append({
            'Distance Bucket': bucket,
            'pct_1putt': (bucket_df['Outcome'] == '1-Putt').sum() / total_holes * 100,
            'pct_2putt': (bucket_df['Outcome'] == '2-Putt').sum() / total_holes * 100,
            'pct_3plus': (bucket_df['Outcome'] == '3+ Putt').sum() / total_holes * 100,
            'sg': sg_by_bucket.get(bucket, 0.0),  # Use putt-level SG
            'holes': total_holes,
        })

    return pd.DataFrame(rows)


# ============================================================
# LAG METRICS (Section 3 — stat cards)
# ============================================================

def _build_lag_metrics(putting_df):
    """Stat cards for putts starting >= 20 ft."""
    lag = putting_df[putting_df['Starting Distance'] >= 20]
    if lag.empty:
        return {"avg_leave": 0.0, "pct_inside_3": 0.0, "pct_over_5": 0.0}

    return {
        "avg_leave": lag['Ending Distance'].mean(),
        "pct_inside_3": safe_divide(
            (lag['Ending Distance'] <= 3).sum(), len(lag)
        ) * 100,
        "pct_over_5": safe_divide(
            (lag['Ending Distance'] > 5).sum(), len(lag)
        ) * 100,
    }


# ============================================================
# LAG MISS DETAIL (collapsible list under hero cards)
# ============================================================

def _build_lag_miss_detail(putting_df):
    """First putts >= 20 ft that leave > 5 ft."""
    first_putts = putting_df[putting_df['Putt Number'] == 1]
    lag_misses = first_putts[
        (first_putts['Starting Distance'] >= 20) &
        (first_putts['Ending Distance'] > 5)
    ].copy()

    if lag_misses.empty:
        return pd.DataFrame(columns=[
            'Player', 'Course', 'Hole',
            'Start Dist (ft)', 'Leave Dist (ft)', 'SG',
        ])

    detail = lag_misses[[
        'Player', 'Date', 'Course', 'Hole',
        'Starting Distance', 'Ending Distance', 'Strokes Gained',
    ]].copy()
    detail = detail.sort_values(
        ['Date', 'Course', 'Hole'], ascending=[False, True, True]
    )
    detail = detail.rename(columns={
        'Starting Distance': 'Start Dist (ft)',
        'Ending Distance': 'Leave Dist (ft)',
        'Strokes Gained': 'SG',
    })
    detail = detail.drop(columns=['Date'])
    return detail


# ============================================================
# THREE-PUTT START DISTRIBUTION (Section 3 — donut a)
# ============================================================

def _build_three_putt_starts(putting_df):
    """First-putt starting distance on holes with 3+ putts."""
    first_putts = putting_df[putting_df['Putt Number'] == 1]
    three_putt_firsts = first_putts[first_putts['Putts On Hole'] >= 3].copy()

    if three_putt_firsts.empty:
        return pd.DataFrame(columns=['Bucket', 'Count'])

    bins = [0, 20, 30, 40, 1000]
    labels = ['<20 ft', '20–30 ft', '30–40 ft', '40+ ft']

    three_putt_firsts['Bucket'] = pd.cut(
        three_putt_firsts['Starting Distance'],
        bins=bins,
        labels=labels,
        right=False,
    )

    return (
        three_putt_firsts
        .groupby('Bucket', observed=False)
        .size()
        .reset_index(name='Count')
    )


# ============================================================
# LEAVE DISTANCE DISTRIBUTION (Section 3 — donut b)
# ============================================================

def _build_leave_distribution(putting_df):
    """Ending-distance distribution for putts starting > 20 ft."""
    lag = putting_df[putting_df['Starting Distance'] > 20].copy()
    if lag.empty:
        return pd.DataFrame(columns=['Bucket', 'Count'])

    bins = [0, 4, 7, 11, 1000]
    labels = ['0–3 ft', '4–6 ft', '7–10 ft', '10+ ft']

    lag['Bucket'] = pd.cut(
        lag['Ending Distance'],
        bins=bins,
        labels=labels,
        right=False,
    )

    return (
        lag.groupby('Bucket', observed=False)
        .size()
        .reset_index(name='Count')
    )


# ============================================================
# SG TREND BY ROUND (Section 4)
# ============================================================

def _build_trend_df(putting_df):
    """SG Putting per round for the trend chart."""
    if putting_df.empty:
        return pd.DataFrame(columns=['Round ID', 'Date', 'Course', 'SG', 'Label'])

    grouped = putting_df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        SG=('Strokes Gained', 'sum'),
    ).reset_index()

    grouped['Date'] = pd.to_datetime(grouped['Date'])
    grouped = grouped.sort_values('Date')
    grouped['Label'] = grouped.apply(
        lambda r: round_label(r['Date'], r['Course']), axis=1
    )

    return grouped


# ============================================================
# SHOT DETAIL TABLE (Section 4 — collapsible)
# ============================================================

def _build_shot_detail(putting_df):
    """Every putt for the detail expander."""
    if putting_df.empty:
        return pd.DataFrame(columns=[
            'Player', 'Course', 'Hole', 'Shot #',
            'Starting Distance', 'Ending Distance', 'SG',
        ])

    detail = putting_df[[
        'Player', 'Date', 'Course', 'Hole', 'Shot',
        'Starting Distance', 'Ending Distance', 'Strokes Gained',
    ]].copy()
    detail = detail.rename(columns={
        'Shot': 'Shot #',
        'Strokes Gained': 'SG',
    })
    detail = detail.sort_values(
        ['Date', 'Course', 'Hole', 'Shot #'],
        ascending=[False, True, True, True],
    )
    detail = detail.drop(columns=['Date'])
    return detail


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def build_putting_results(filtered_df, num_rounds):
    """
    Return a rich dict consumed by putting_tab, overview_engine,
    and coachs_corner.

    Downstream keys preserved:
        - total_sg_putting   (used by overview_engine, coachs_corner)
        - df                 (enriched putting DataFrame)
    """
    putting_df = _enrich_putting_df(filtered_df)

    empty_hero = {
        "sg_total": 0.0, "sg_per_round": 0.0,
        "sg_4_6": 0.0, "sg_4_6_made": 0, "sg_4_6_attempts": 0,
        "sg_7_10": 0.0, "sg_7_10_made": 0, "sg_7_10_attempts": 0,
        "lag_miss_pct": 0.0,
        "make_0_3_pct": 0.0, "make_0_3_made": 0, "make_0_3_attempts": 0,
    }
    empty_lag = {"avg_leave": 0.0, "pct_inside_3": 0.0, "pct_over_5": 0.0}

    if putting_df.empty:
        return {
            "empty": True,
            "df": putting_df,
            "total_sg_putting": 0.0,
            "hero_metrics": empty_hero,
            "bucket_table": pd.DataFrame(),
            "outcome_chart_data": pd.DataFrame(),
            "lag_metrics": empty_lag,
            "lag_miss_detail": pd.DataFrame(),
            "three_putt_starts": pd.DataFrame(),
            "leave_distribution": pd.DataFrame(),
            "trend_df": pd.DataFrame(),
            "shot_detail": pd.DataFrame(),
        }

    total_sg = putting_df['Strokes Gained'].sum()

    return {
        "empty": False,
        "df": putting_df,
        "total_sg_putting": total_sg,
        "hero_metrics": _build_hero_metrics(putting_df, num_rounds),
        "bucket_table": _build_bucket_table(putting_df),
        "outcome_chart_data": _build_outcome_chart_data(putting_df),
        "lag_metrics": _build_lag_metrics(putting_df),
        "lag_miss_detail": _build_lag_miss_detail(putting_df),
        "three_putt_starts": _build_three_putt_starts(putting_df),
        "leave_distribution": _build_leave_distribution(putting_df),
        "trend_df": _build_trend_df(putting_df),
        "shot_detail": _build_shot_detail(putting_df),
    }
