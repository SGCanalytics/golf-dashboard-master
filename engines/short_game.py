import pandas as pd

# ============================================================
# SHORT GAME ENGINE
# ============================================================

def build_short_game_results(filtered_df, num_rounds):
    """
    Compute all short game analytics for the Short Game tab.
    """

    df = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()
    num_sg = len(df)

    empty_hero = {"sg_total": 0.0, "inside_8_fr": 0, "inside_8_sand": 0, "avg_proximity": 0.0}

    if num_sg == 0:
        return {
            "empty": True,
            "df": df,
            "total_sg": 0.0,
            "sg_per_round": 0.0,
            "hero_metrics": empty_hero,
            "distance_lie_table": pd.DataFrame(),
            "trend_df": pd.DataFrame()
        }

    # Ensure distances are numeric
    df['Ending Distance'] = pd.to_numeric(df['Ending Distance'], errors='coerce')
    df['Starting Distance'] = pd.to_numeric(df['Starting Distance'], errors='coerce')

    # --- Basic SG ---
    total_sg = df['Strokes Gained'].sum()
    sg_per_round = total_sg / num_rounds if num_rounds > 0 else 0

    # --- Hero metrics ---
    fr_shots = df[df['Starting Location'].isin(['Fairway', 'Rough'])]
    sand_shots = df[df['Starting Location'] == 'Sand']

    inside_8_fr = int((fr_shots['Ending Distance'] <= 8).sum()) if not fr_shots.empty else 0
    inside_8_sand = int((sand_shots['Ending Distance'] <= 8).sum()) if not sand_shots.empty else 0
    avg_proximity = df['Ending Distance'].mean() if not df['Ending Distance'].isna().all() else 0.0

    hero_metrics = {
        "sg_total": total_sg,
        "inside_8_fr": inside_8_fr,
        "inside_8_sand": inside_8_sand,
        "avg_proximity": avg_proximity
    }

    # --- Distance x Lie table ---
    def sg_bucket(d):
        if d < 10:
            return "<10"
        elif d < 20:
            return "10\u201320"
        elif d < 30:
            return "20\u201330"
        elif d < 40:
            return "30\u201340"
        return "40+"

    df['Dist Bucket'] = df['Starting Distance'].apply(sg_bucket)

    lie_table = df.groupby(['Dist Bucket', 'Starting Location']).agg(
        Shots=('Strokes Gained', 'count'),
        **{'Total SG': ('Strokes Gained', 'sum')},
        **{'SG/Shot': ('Strokes Gained', 'mean')},
        **{'Avg Proximity': ('Ending Distance', 'mean')},
        **{'Inside 8 ft': ('Ending Distance', lambda x: (x <= 8).sum())}
    ).reset_index()

    # --- Trend by round ---
    round_trend = df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first'),
        SG=('Strokes Gained', 'sum'),
        Total_Shots=('Strokes Gained', 'count'),
        Inside8_Count=('Ending Distance', lambda x: (x <= 8).sum())
    ).reset_index()
    round_trend['Date'] = pd.to_datetime(round_trend['Date'])
    round_trend = round_trend.sort_values('Date')
    round_trend['Inside8 %'] = round_trend.apply(
        lambda r: r['Inside8_Count'] / r['Total_Shots'] * 100 if r['Total_Shots'] > 0 else 0, axis=1
    )
    round_trend['Label'] = round_trend.apply(
        lambda r: f"{r['Date'].strftime('%m/%d')} {r['Course']}", axis=1
    )

    return {
        "empty": False,
        "df": df,
        "total_sg": total_sg,
        "sg_per_round": sg_per_round,
        "hero_metrics": hero_metrics,
        "distance_lie_table": lie_table,
        "trend_df": round_trend
    }


#################################
# AI Narrative
##############################
def short_game_narrative(results):
    sg = results.get("sg_per_round", 0)
    hero = results.get("hero_metrics", {})

    lines = ["Short Game Performance:"]

    if sg > 0.25:
        lines.append(f"- Strong short game, gaining {sg:.2f} strokes per round.")
    elif sg > 0:
        lines.append(f"- Slightly positive SG around the green at {sg:.2f}.")
    else:
        lines.append(f"- Losing strokes around the green ({sg:.2f}).")

    lines.append(f"- Inside 8 ft (FR/Rough): {hero.get('inside_8_fr', 0)} shots")
    lines.append(f"- Inside 8 ft (Sand): {hero.get('inside_8_sand', 0)} shots")
    lines.append(f"- Avg Proximity: {hero.get('avg_proximity', 0):.1f} ft")

    return "\n".join(lines)
