import pandas as pd
from engines.helpers import sg_distance_bucket
from ui.formatters import round_label

# ============================================================
# SHORT GAME ENGINE
# ============================================================

# Ordered constants used by heat map and distance-lie table
BUCKET_ORDER = ["<10", "10–20", "20–30", "30–40", "40–50"]
LIE_ORDER = ["Fairway", "Rough", "Sand"]

LEAVE_BUCKET_ORDER = ["0–3", "4–6", "7–10", "10–20", "20+"]


def _leave_bucket(dist):
    """Bucket ending distance into leave-distance ranges (feet)."""
    if dist <= 3:
        return "0–3"
    if dist <= 6:
        return "4–6"
    if dist <= 10:
        return "7–10"
    if dist <= 20:
        return "10–20"
    return "20+"


def _build_hero_metrics(df, num_rounds):
    """Compute the five hero-card values."""
    sg_total = df['Strokes Gained'].sum()
    sg_per_round = sg_total / num_rounds if num_rounds > 0 else 0.0

    shots_25_50 = df[df['Starting Distance'] >= 25]
    sg_25_50 = shots_25_50['Strokes Gained'].sum() if not shots_25_50.empty else 0.0

    shots_arg = df[df['Starting Distance'] < 25]
    sg_arg = shots_arg['Strokes Gained'].sum() if not shots_arg.empty else 0.0

    # % inside 8 ft on the green — Fairway & Rough
    fr_shots = df[df['Starting Location'].isin(['Fairway', 'Rough'])]
    if len(fr_shots) > 0:
        fr_inside_8 = fr_shots[
            (fr_shots['Ending Distance'] <= 8) & (fr_shots['Ending Location'] == 'Green')
        ]
        pct_inside_8_fr = len(fr_inside_8) / len(fr_shots) * 100
    else:
        pct_inside_8_fr = 0.0

    # % inside 8 ft on the green — Sand
    sand_shots = df[df['Starting Location'] == 'Sand']
    if len(sand_shots) > 0:
        sand_inside_8 = sand_shots[
            (sand_shots['Ending Distance'] <= 8) & (sand_shots['Ending Location'] == 'Green')
        ]
        pct_inside_8_sand = len(sand_inside_8) / len(sand_shots) * 100
    else:
        pct_inside_8_sand = 0.0

    return {
        "sg_total": sg_total,
        "sg_per_round": sg_per_round,
        "sg_25_50": sg_25_50,
        "sg_arg": sg_arg,
        "pct_inside_8_fr": pct_inside_8_fr,
        "pct_inside_8_sand": pct_inside_8_sand,
    }


def _build_heatmap_data(df):
    """Build SG/Shot and shot-count pivot tables for the heat map."""
    heat_df = df[df['Starting Location'].isin(LIE_ORDER)]

    sg_pivot = heat_df.pivot_table(
        index='Starting Location',
        columns='Dist Bucket',
        values='Strokes Gained',
        aggfunc='mean',
    )

    count_pivot = heat_df.pivot_table(
        index='Starting Location',
        columns='Dist Bucket',
        values='Strokes Gained',
        aggfunc='count',
    )

    # Enforce consistent row/column ordering; missing combos become NaN
    sg_pivot = sg_pivot.reindex(index=LIE_ORDER, columns=BUCKET_ORDER)
    count_pivot = count_pivot.reindex(index=LIE_ORDER, columns=BUCKET_ORDER)

    return sg_pivot, count_pivot


def _build_distance_lie_table(df):
    """Aggregate short game stats by distance bucket and starting lie."""
    lie_table = df.groupby(['Dist Bucket', 'Starting Location']).agg(
        Shots=('Strokes Gained', 'count'),
        **{'Total SG': ('Strokes Gained', 'sum')},
        **{'SG/Shot': ('Strokes Gained', 'mean')},
        **{'Avg Proximity': ('Ending Distance', 'mean')},
        **{'Inside 8 ft': ('Ending Distance', lambda x: (x <= 8).sum())},
    ).reset_index()

    return lie_table


def _build_leave_distribution(df):
    """Count shots in each leave-distance bucket."""
    df = df.copy()
    df['Leave Bucket'] = df['Ending Distance'].apply(_leave_bucket)

    leave_dist = (
        df.groupby('Leave Bucket')
        .size()
        .reindex(LEAVE_BUCKET_ORDER, fill_value=0)
        .reset_index(name='Shots')
    )
    leave_dist.columns = ['Leave Bucket', 'Shots']
    return leave_dist


def _build_trend(df):
    """Per-round SG and inside-8-ft trend data."""
    round_trend = df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        SG=('Strokes Gained', 'sum'),
        Total_Shots=('Strokes Gained', 'count'),
        Inside8_Count=('Ending Distance', lambda x: (x <= 8).sum()),
    ).reset_index()

    round_trend['Date'] = pd.to_datetime(round_trend['Date'])
    round_trend = round_trend.sort_values('Date')
    round_trend['Inside8 %'] = round_trend.apply(
        lambda r: r['Inside8_Count'] / r['Total_Shots'] * 100 if r['Total_Shots'] > 0 else 0,
        axis=1,
    )
    round_trend['Label'] = round_trend.apply(
        lambda r: round_label(r['Date'], r['Course']), axis=1
    )
    return round_trend


def _build_shot_detail(df):
    """Flat table of every short game shot for the detail expander."""
    detail_cols = [
        'Player', 'Date', 'Course', 'Hole', 'Shot',
        'Starting Distance', 'Starting Location',
        'Ending Distance', 'Ending Location', 'Penalty', 'Strokes Gained',
    ]
    shot_detail = df[detail_cols].copy()
    shot_detail = shot_detail.rename(columns={
        'Shot': 'Shot #',
        'Starting Distance': 'Start Dist',
        'Starting Location': 'Start Lie',
        'Ending Distance': 'End Dist',
        'Ending Location': 'End Lie',
        'Strokes Gained': 'SG',
    })
    shot_detail = shot_detail.sort_values(['Date', 'Course', 'Hole', 'Shot #'])
    return shot_detail


# ============================================================
# MASTER BUILDER
# ============================================================

def build_short_game_results(filtered_df, num_rounds):
    """
    Compute all short game analytics for the Short Game tab.

    Returns a dict consumed by short_game_tab() in app.py.
    Keys 'total_sg', 'sg_per_round', and 'empty' are also consumed
    by overview.py and coachs_corner.py — do not remove them.
    """
    df = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()

    empty_hero = {
        "sg_total": 0.0, "sg_per_round": 0.0,
        "sg_25_50": 0.0, "sg_arg": 0.0,
        "pct_inside_8_fr": 0.0, "pct_inside_8_sand": 0.0,
    }

    if len(df) == 0:
        return {
            "empty": True,
            "df": df,
            "total_sg": 0.0,
            "sg_per_round": 0.0,
            "hero_metrics": empty_hero,
            "heatmap_sg_pivot": pd.DataFrame(),
            "heatmap_count_pivot": pd.DataFrame(),
            "distance_lie_table": pd.DataFrame(),
            "leave_distribution": pd.DataFrame(),
            "trend_df": pd.DataFrame(),
            "shot_detail": pd.DataFrame(),
        }

    # Ensure distances are numeric
    df['Ending Distance'] = pd.to_numeric(df['Ending Distance'], errors='coerce')
    df['Starting Distance'] = pd.to_numeric(df['Starting Distance'], errors='coerce')

    # Distance bucket column — shared by heatmap and distance-lie table
    df['Dist Bucket'] = df['Starting Distance'].apply(sg_distance_bucket)

    # Build each section
    hero = _build_hero_metrics(df, num_rounds)
    sg_pivot, count_pivot = _build_heatmap_data(df)
    lie_table = _build_distance_lie_table(df)
    leave_dist = _build_leave_distribution(df)
    trend = _build_trend(df)
    shot_detail = _build_shot_detail(df)

    return {
        "empty": False,
        "df": df,
        "total_sg": hero["sg_total"],
        "sg_per_round": hero["sg_per_round"],
        "hero_metrics": hero,
        "heatmap_sg_pivot": sg_pivot,
        "heatmap_count_pivot": count_pivot,
        "distance_lie_table": lie_table,
        "leave_distribution": leave_dist,
        "trend_df": trend,
        "shot_detail": shot_detail,
    }


# ============================================================
# AI Narrative
# ============================================================

def short_game_narrative(results):
    hero = results.get("hero_metrics", {})
    sg = hero.get("sg_per_round", results.get("sg_per_round", 0))

    lines = ["Short Game Performance:"]

    if sg > 0.25:
        lines.append(f"- Strong short game, gaining {sg:.2f} strokes per round.")
    elif sg > 0:
        lines.append(f"- Slightly positive SG around the green at {sg:.2f}.")
    else:
        lines.append(f"- Losing strokes around the green ({sg:.2f}).")

    lines.append(f"- Inside 8 ft (FW/Rough): {hero.get('pct_inside_8_fr', 0):.0f}%")
    lines.append(f"- Inside 8 ft (Sand): {hero.get('pct_inside_8_sand', 0):.0f}%")

    return "\n".join(lines)
