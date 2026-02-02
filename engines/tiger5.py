import pandas as pd

# ============================================================
# TIGER 5 ENGINE — CENTRALIZED & REUSABLE
# ============================================================

def _t5_three_putts(hole_summary):
    """3 Putts: any hole with ≥3 putts."""
    attempts = (hole_summary['num_putts'] >= 1).sum()
    fails = (hole_summary['num_putts'] >= 3).sum()

    detail = hole_summary[hole_summary['num_putts'] >= 3][
        ['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']
    ].copy()

    return attempts, fails, detail


def _t5_double_bogey(hole_summary):
    """Double Bogey: score ≥ par + 2."""
    attempts = len(hole_summary)
    mask = hole_summary['Hole Score'] >= hole_summary['Par'] + 2
    fails = mask.sum()

    detail = hole_summary[mask][
        ['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']
    ].copy()

    return attempts, fails, detail


def _t5_par5_bogey(hole_summary):
    """Par 5 Bogey: par 5 holes with score ≥ 6."""
    par5 = hole_summary[hole_summary['Par'] == 5]
    attempts = len(par5)

    mask = par5['Hole Score'] >= 6
    fails = mask.sum()

    detail = par5[mask][
        ['Player', 'Round ID', 'Date', 'Course', 'Hole', 'Par', 'Hole Score']
    ].copy()

    return attempts, fails, detail


def _t5_missed_green_short_game(df, hole_summary):
    """Missed Green: any short game shot not ending on the green."""
    sg_shots = df[df['Shot Type'] == 'Short Game'].copy()
    if sg_shots.empty:
        return 0, 0, sg_shots

    sg_shots['missed_green'] = sg_shots['Ending Location'] != 'Green'

    by_hole = sg_shots.groupby(
        ['Player', 'Round ID', 'Date', 'Course', 'Hole']
    ).agg(any_missed=('missed_green', 'any')).reset_index()

    attempts = len(by_hole)
    fails = by_hole['any_missed'].sum()

    detail = by_hole[by_hole['any_missed']][
        ['Player', 'Round ID', 'Date', 'Course', 'Hole']
    ].copy()

    if not detail.empty:
        detail = detail.merge(
            hole_summary[['Player', 'Round ID', 'Hole', 'Par', 'Hole Score']],
            on=['Player', 'Round ID', 'Hole'],
            how='left'
        )

    return attempts, fails, detail


def _t5_approach_125_bogey(df, hole_summary):
    """125yd Bogey: scoring shot inside 125yd that results in bogey or worse."""
    cond = (
        (df['Starting Distance'] <= 125) &
        (df['Starting Location'] != 'Recovery') &
        (
            ((df['Shot'] == 3) & (df['Par'] == 5)) |
            ((df['Shot'] == 2) & (df['Par'] == 4)) |
            ((df['Shot'] == 1) & (df['Par'] == 3))
        )
    )

    candidates = df[cond][['Player', 'Round ID', 'Date', 'Course', 'Hole']].drop_duplicates()

    if candidates.empty:
        return 0, 0, candidates

    with_score = candidates.merge(
        hole_summary[['Player', 'Round ID', 'Hole', 'Hole Score', 'Par']],
        on=['Player', 'Round ID', 'Hole'],
        how='left'
    )

    attempts = len(with_score)
    mask = with_score['Hole Score'] > with_score['Par']
    fails = mask.sum()

    detail = with_score[mask].copy()

    return attempts, fails, detail


# ============================================================
# MASTER TIGER 5 CALCULATOR (RENAMED FOR APP.PY)
# ============================================================

def build_tiger5_results(df, hole_summary):
    """
    Returns:
        - results: dict of each Tiger 5 category with attempts, fails, detail_holes
        - total_fails: total Tiger 5 fails
        - grit_score: success rate %
    """
    results = {}

    # 3 Putts
    a_3p, f_3p, d_3p = _t5_three_putts(hole_summary)
    results['3 Putts'] = {
        'attempts': a_3p,
        'fails': f_3p,
        'detail_holes': d_3p
    }

    # Double Bogey
    a_db, f_db, d_db = _t5_double_bogey(hole_summary)
    results['Double Bogey'] = {
        'attempts': a_db,
        'fails': f_db,
        'detail_holes': d_db
    }

    # Par 5 Bogey
    a_p5, f_p5, d_p5 = _t5_par5_bogey(hole_summary)
    results['Par 5 Bogey'] = {
        'attempts': a_p5,
        'fails': f_p5,
        'detail_holes': d_p5
    }

    # Missed Green
    a_mg, f_mg, d_mg = _t5_missed_green_short_game(df, hole_summary)
    results['Missed Green'] = {
        'attempts': a_mg,
        'fails': f_mg,
        'detail_holes': d_mg
    }

    # 125yd Bogey
    a_125, f_125, d_125 = _t5_approach_125_bogey(df, hole_summary)
    results['125yd Bogey'] = {
        'attempts': a_125,
        'fails': f_125,
        'detail_holes': d_125
    }

    # Totals
    total_attempts = sum(r['attempts'] for r in results.values())
    total_fails = sum(r['fails'] for r in results.values())

    grit_score = (
        ((total_attempts - total_fails) / total_attempts * 100)
        if total_attempts > 0 else 0
    )

    return results, total_fails, grit_score


# ============================================================
# TIGER 5 BY ROUND — FOR TREND CHARTS
# ============================================================

def tiger5_by_round(df, hole_summary):
    """Per-round Tiger 5 breakdown."""
    round_info = df.groupby('Round ID').agg(
        Date=('Date', 'first'),
        Course=('Course', 'first')
    ).reset_index()

    rows = []

    for _, r in round_info.iterrows():
        rid = r['Round ID']
        date_obj = pd.to_datetime(r['Date'])
        label = f"{date_obj.strftime('%m/%d/%Y')} {r['Course']}"

        round_df = df[df['Round ID'] == rid]
        round_holes = hole_summary[hole_summary['Round ID'] == rid]

        a_3p, f_3p, _ = _t5_three_putts(round_holes)
        a_db, f_db, _ = _t5_double_bogey(round_holes)
        a_p5, f_p5, _ = _t5_par5_bogey(round_holes)
        a_mg, f_mg, _ = _t5_missed_green_short_game(round_df, round_holes)
        a_125, f_125, _ = _t5_approach_125_bogey(round_df, round_holes)

        total_score = round_holes['Hole Score'].sum()

        rows.append({
            'Round ID': rid,
            'Label': label,
            'Date': date_obj,
            '3 Putts': f_3p,
            'Double Bogey': f_db,
            'Par 5 Bogey': f_p5,
            'Missed Green': f_mg,
            '125yd Bogey': f_125,
            'Total Score': total_score
        })

    t5_df = pd.DataFrame(rows)

    if not t5_df.empty:
        t5_df = t5_df.sort_values('Date')
        t5_df['Total Fails'] = (
            t5_df['3 Putts'] +
            t5_df['Double Bogey'] +
            t5_df['Par 5 Bogey'] +
            t5_df['Missed Green'] +
            t5_df['125yd Bogey']
        )

    return t5_df
