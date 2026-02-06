# Short Game Tab Overhaul — Implementation Plan

## Overview

Overhaul the Short Game tab with 5 new sections: redesigned hero cards, an SG/Shot
heat map with collapsible detail table, a leave-distance distribution chart, the
existing SG trend line (kept as-is), and a collapsible all-shots table. The engine
(`engines/short_game.py`) will be updated to compute all new metrics; the UI
(`app.py: short_game_tab`) will be rewritten to render the new layout.

---

## Files Changed

| File | Action | Scope |
|------|--------|-------|
| `engines/short_game.py` | **Rewrite** | New hero metrics, heat map data, leave-distance buckets, shot detail table |
| `app.py` (lines 1704–1860) | **Rewrite** | `short_game_tab()` function — new sections 1–5 |
| `app.py` (CSS block, ~line 69) | **Add** | New CSS classes for SG hero cards with conditional coloring |
| `engines/helpers.py` | **Add** | `sg_distance_bucket()` helper for short game distance buckets |

### Files NOT Changed (backward compatibility preserved)

| File | Why |
|------|-----|
| `engines/overview.py` | Reads `short_game_results.get("total_sg", 0)` — key preserved |
| `engines/coachs_corner.py` | Reads `short_game_results.get("total_sg", 0)` — key preserved |
| `app.py` (call site, line 2218) | Signature `build_short_game_results(filtered_df, num_rounds)` unchanged |
| `data/load_data.py` | No changes to data loading or shot-type classification |

---

## Step 1 — `engines/helpers.py`: Add short-game distance bucket helper

Add a new function alongside the existing `bucket_distance()`:

```python
def sg_distance_bucket(dist):
    """Short-game specific distance buckets (0–50 yards)."""
    if dist < 10:
        return "<10"
    elif dist < 20:
        return "10–20"
    elif dist < 30:
        return "20–30"
    elif dist < 40:
        return "30–40"
    return "40–50"
```

**Why**: The current `sg_bucket()` is defined inline inside `build_short_game_results`.
Extracting it to `helpers.py` makes it reusable, testable, and avoids duplication
between the heat map builder and the distance-lie table builder.

**Bucket boundary logic** (deterministic, no ambiguity):
- `dist < 10` → `"<10"`
- `10 <= dist < 20` → `"10–20"`
- `20 <= dist < 30` → `"20–30"`
- `30 <= dist < 40` → `"30–40"`
- `40 <= dist` → `"40–50"` (shots are already filtered to < 50 by Shot Type)

---

## Step 2 — `engines/short_game.py`: Rewrite engine

Replace the current `build_short_game_results` function. The return dict will contain
all keys needed by the new UI, while preserving backward-compatible keys consumed by
`overview.py` and `coachs_corner.py`.

### 2a. Input / Filter (unchanged)

```python
df = filtered_df[filtered_df['Shot Type'] == 'Short Game'].copy()
```

Ensure numeric types:
```python
df['Ending Distance'] = pd.to_numeric(df['Ending Distance'], errors='coerce')
df['Starting Distance'] = pd.to_numeric(df['Starting Distance'], errors='coerce')
```

### 2b. Hero Metrics (Section 1)

Compute **5 hero values**:

| Metric | Key | Computation |
|--------|-----|-------------|
| SG Short Game (total) | `sg_total` | `df['Strokes Gained'].sum()` |
| SG Short Game (per round) | `sg_per_round` | `sg_total / num_rounds` |
| SG 25–50 | `sg_25_50` | `df[df['Starting Distance'] >= 25]['Strokes Gained'].sum()` |
| SG ARG (< 25) | `sg_arg` | `df[df['Starting Distance'] < 25]['Strokes Gained'].sum()` |
| % Inside 8 ft (FW & Rough) | `pct_inside_8_fr` | Of shots with `Starting Location` in `['Fairway', 'Rough']`, the percentage where `Ending Distance <= 8` AND `Ending Location == 'Green'` |
| % Inside 8 ft (Sand) | `pct_inside_8_sand` | Of shots with `Starting Location == 'Sand'`, the percentage where `Ending Distance <= 8` AND `Ending Location == 'Green'` |

**Implementation detail — "finish within 8 feet on the green":**

The spec says "% of short game shots that finish within 8 feet **on the green**".
This means we must check **both** `Ending Distance <= 8` **and** `Ending Location == 'Green'`.
This is stricter than the current implementation which only checks `Ending Distance <= 8`.

```python
fr_shots = df[df['Starting Location'].isin(['Fairway', 'Rough'])]
fr_on_green_inside_8 = fr_shots[
    (fr_shots['Ending Distance'] <= 8) & (fr_shots['Ending Location'] == 'Green')
]
pct_inside_8_fr = (len(fr_on_green_inside_8) / len(fr_shots) * 100) if len(fr_shots) > 0 else 0.0

sand_shots = df[df['Starting Location'] == 'Sand']
sand_on_green_inside_8 = sand_shots[
    (sand_shots['Ending Distance'] <= 8) & (sand_shots['Ending Location'] == 'Green')
]
pct_inside_8_sand = (len(sand_on_green_inside_8) / len(sand_shots) * 100) if len(sand_shots) > 0 else 0.0
```

**Return structure for hero metrics:**
```python
"hero_metrics": {
    "sg_total": float,       # total SG short game
    "sg_per_round": float,   # SG per round (sub-text)
    "sg_25_50": float,       # SG for 25-50 yard shots
    "sg_arg": float,          # SG for <25 yard shots (Around the Green)
    "pct_inside_8_fr": float, # % inside 8ft on green (FW + Rough)
    "pct_inside_8_sand": float # % inside 8ft on green (Sand)
}
```

### 2c. Heat Map Data (Section 2)

Build a pivot table: rows = Starting Location, columns = Distance Bucket, values = SG/Shot.
Also build a parallel pivot for shot counts (used for cell labels and blank-cell logic).

```python
from engines.helpers import sg_distance_bucket

df['Dist Bucket'] = df['Starting Distance'].apply(sg_distance_bucket)

BUCKET_ORDER = ["<10", "10–20", "20–30", "30–40", "40–50"]
LIE_ORDER = ["Fairway", "Rough", "Sand"]

# Filter to the three lie types we care about
heat_df = df[df['Starting Location'].isin(LIE_ORDER)]

# SG per shot pivot
sg_pivot = heat_df.pivot_table(
    index='Starting Location',
    columns='Dist Bucket',
    values='Strokes Gained',
    aggfunc='mean'
)

# Shot count pivot
count_pivot = heat_df.pivot_table(
    index='Starting Location',
    columns='Dist Bucket',
    values='Strokes Gained',
    aggfunc='count'
)

# Reindex to enforce consistent ordering; missing cells become NaN
sg_pivot = sg_pivot.reindex(index=LIE_ORDER, columns=BUCKET_ORDER)
count_pivot = count_pivot.reindex(index=LIE_ORDER, columns=BUCKET_ORDER)
```

**Return keys:**
```python
"heatmap_sg_pivot": DataFrame,    # SG/Shot values (NaN where 0 shots)
"heatmap_count_pivot": DataFrame  # shot counts (NaN where 0 shots)
```

### 2d. Distance × Lie Table (Section 2 — collapsible, existing logic preserved)

Keep the existing `lie_table` aggregation, but use `sg_distance_bucket` from helpers
instead of the inline `sg_bucket` function. This table is placed inside
`st.expander()` below the heat map.

**Return key (unchanged):**
```python
"distance_lie_table": DataFrame
```

### 2e. Leave Distance Distribution (Section 3)

Bucket all short game shots by `Ending Distance` (leave distance):

```python
def leave_bucket(dist):
    if dist <= 3:
        return "0–3"
    elif dist <= 6:
        return "4–6"
    elif dist <= 10:
        return "7–10"
    elif dist <= 20:
        return "10–20"
    return "20+"

df['Leave Bucket'] = df['Ending Distance'].apply(leave_bucket)

LEAVE_ORDER = ["0–3", "4–6", "7–10", "10–20", "20+"]

leave_dist = (
    df.groupby('Leave Bucket')
    .size()
    .reindex(LEAVE_ORDER, fill_value=0)
    .reset_index(name='Shots')
)
leave_dist.columns = ['Leave Bucket', 'Shots']
```

**Return key:**
```python
"leave_distribution": DataFrame  # columns: Leave Bucket, Shots
```

### 2f. Trend Data (Section 4 — unchanged)

Keep the existing round-trend computation exactly as-is. No changes.

**Return key (unchanged):**
```python
"trend_df": DataFrame
```

### 2g. Shot Detail Table (Section 5)

Build a table of every short game shot with the requested columns:

```python
detail_cols = [
    'Player', 'Date', 'Course', 'Hole', 'Shot',
    'Starting Distance', 'Starting Location',
    'Ending Distance', 'Ending Location', 'Penalty', 'Strokes Gained'
]
shot_detail = df[detail_cols].copy()
shot_detail = shot_detail.rename(columns={
    'Shot': 'Shot #',
    'Starting Distance': 'Start Dist',
    'Starting Location': 'Start Lie',
    'Ending Distance': 'End Dist',
    'Ending Location': 'End Lie',
    'Strokes Gained': 'SG'
})
shot_detail = shot_detail.sort_values(['Date', 'Course', 'Hole', 'Shot #'])
```

**Return key:**
```python
"shot_detail": DataFrame
```

### 2h. Complete Return Dict

```python
{
    "empty": bool,
    "df": DataFrame,              # full short game df (internal use)
    "total_sg": float,            # PRESERVED — used by overview.py, coachs_corner.py
    "sg_per_round": float,        # PRESERVED — used by narrative
    "hero_metrics": { ... },      # see 2b
    "heatmap_sg_pivot": DataFrame,    # see 2c
    "heatmap_count_pivot": DataFrame, # see 2c
    "distance_lie_table": DataFrame,  # see 2d (preserved)
    "leave_distribution": DataFrame,  # see 2e
    "trend_df": DataFrame,            # see 2f (preserved)
    "shot_detail": DataFrame          # see 2g
}
```

### 2i. Update `short_game_narrative()`

Update the narrative function to reference the new hero metric keys. This function is
currently unused in `app.py` (no call site found), but update for consistency:

```python
def short_game_narrative(results):
    hero = results.get("hero_metrics", {})
    sg = hero.get("sg_per_round", 0)
    # ... rest of logic using new keys
```

---

## Step 3 — `app.py` CSS: Add short-game hero card classes

Add two new CSS classes near the existing `.tiger-card-*` block (~line 78). These
mirror the Tiger 5 card styling but use green/red conditional coloring for the value:

```css
/* Short Game hero cards — positive (green) */
.sg-hero-positive {
    background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
    border-radius: 12px;
    padding: 1.25rem 1rem;
    text-align: center;
    border: 2px solid #2d6a4f;
    margin-bottom: 1rem;
}
.sg-hero-positive .card-label {
    font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600;
    color: #2d6a4f; text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}
.sg-hero-positive .card-value {
    font-family: 'Playfair Display', serif; font-size: 2.25rem; font-weight: 700;
    color: #2d6a4f; line-height: 1; margin-bottom: 0.25rem;
}
.sg-hero-positive .card-unit {
    font-family: 'Inter', sans-serif; font-size: 0.65rem;
    color: rgba(45,106,79,0.7); text-transform: uppercase; letter-spacing: 0.05em;
}

/* Short Game hero cards — negative (red) */
.sg-hero-negative {
    background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
    border-radius: 12px;
    padding: 1.25rem 1rem;
    text-align: center;
    border: 2px solid #E03C31;
    margin-bottom: 1rem;
}
.sg-hero-negative .card-label {
    font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600;
    color: #E03C31; text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}
.sg-hero-negative .card-value {
    font-family: 'Playfair Display', serif; font-size: 2.25rem; font-weight: 700;
    color: #E03C31; line-height: 1; margin-bottom: 0.25rem;
}
.sg-hero-negative .card-unit {
    font-family: 'Inter', sans-serif; font-size: 0.65rem;
    color: rgba(224,60,49,0.7); text-transform: uppercase; letter-spacing: 0.05em;
}
```

**Card class selection logic (in Python):**
- SG cards (1, 2, 3): `"sg-hero-positive"` if value >= 0, else `"sg-hero-negative"`
- % Inside 8ft cards (4, 5): `"sg-hero-positive"` if value >= 60, else `"sg-hero-negative"`

---

## Step 4 — `app.py`: Rewrite `short_game_tab()`

Replace lines 1704–1860 with the new function. Signature stays the same:
```python
def short_game_tab(sg, num_rounds):
```

### Section 1: Hero Cards (5 columns)

```
| SG Short Game   | SG 25–50       | SG ARG (<25)   | % Inside 8ft    | % Inside 8ft    |
| +0.45           | +0.22          | +0.23          | 62%             | 48%             |
| 0.15 per round  | Total          | Total          | Fairway & Rough | Bunker           |
```

Each card uses the Tiger 5 card structure:
```html
<div class="{card_class}">
    <div class="card-label">{label}</div>
    <div class="card-value">{value}</div>
    <div class="card-unit">{sub_text}</div>
</div>
```

**Card details:**

| # | Label | Value | Sub-text | Threshold for green/red |
|---|-------|-------|----------|------------------------|
| 1 | SG Short Game | `{sg_total:+.2f}` | `{sg_per_round:+.2f} per round` | `>= 0` → green |
| 2 | SG 25–50 | `{sg_25_50:+.2f}` | `Total` | `>= 0` → green |
| 3 | SG ARG | `{sg_arg:+.2f}` | `Total` | `>= 0` → green |
| 4 | % Inside 8 ft | `{pct_inside_8_fr:.0f}%` | `Fairway & Rough` | `>= 60` → green |
| 5 | % Inside 8 ft | `{pct_inside_8_sand:.0f}%` | `Bunker` | `>= 60` → green |

### Section 2: Heat Map + Collapsible Table

**Heat Map** — Rendered with `plotly.graph_objects.Heatmap`:

```python
import plotly.graph_objects as go
import numpy as np

sg_pivot = sg["heatmap_sg_pivot"]
count_pivot = sg["heatmap_count_pivot"]

# Build custom text matrix: show shot count, blank if 0/NaN
text_matrix = count_pivot.fillna(0).astype(int).astype(str)
text_matrix = text_matrix.replace('0', '')
# Prefix non-empty cells with "n=" for clarity
text_matrix = text_matrix.apply(lambda col: col.apply(lambda v: f"n={v}" if v else ""))

fig_heat = go.Figure(data=go.Heatmap(
    z=sg_pivot.values,
    x=sg_pivot.columns.tolist(),  # distance buckets
    y=sg_pivot.index.tolist(),    # lie types
    text=text_matrix.values,
    texttemplate="%{text}",
    colorscale=[
        [0.0, '#E03C31'],   # red (negative SG)
        [0.5, '#f5f5f5'],   # white (neutral)
        [1.0, '#2d6a4f']    # green (positive SG)
    ],
    zmid=0,                       # center diverging scale at 0
    colorbar=dict(title="SG/Shot"),
    hovertemplate=(
        "Lie: %{y}<br>"
        "Distance: %{x}<br>"
        "SG/Shot: %{z:.3f}<br>"
        "%{text}<extra></extra>"
    )
))

fig_heat.update_layout(
    **CHART_LAYOUT,
    xaxis_title="Distance (yards)",
    yaxis_title="Starting Lie",
    height=300,
    margin=dict(t=40, b=60, l=100, r=40)
)
```

**Key behavior**: Cells with 0 shots → `NaN` in z-values → rendered as blank/white
(Plotly Heatmap skips NaN cells by default).

**Collapsible detail table** — Directly beneath the heat map:

```python
with st.expander("View Detailed Performance by Distance & Lie"):
    st.dataframe(sg["distance_lie_table"], use_container_width=True, hide_index=True)
```

### Section 3: Leave Distance Distribution

Bar chart using `plotly.graph_objects.Bar`:

```python
leave = sg["leave_distribution"]

fig_leave = go.Figure(data=go.Bar(
    x=leave['Leave Bucket'],
    y=leave['Shots'],
    marker_color=ODU_GOLD,
    text=leave['Shots'],
    textposition='outside'
))

fig_leave.update_layout(
    **CHART_LAYOUT,
    xaxis_title="Leave Distance (ft)",
    yaxis_title="Number of Shots",
    height=350,
    margin=dict(t=40, b=60, l=60, r=40),
    showlegend=False
)
```

### Section 4: SG Short Game Trend Line (preserved)

Keep the existing dual-axis bar + line chart implementation exactly as-is
(lines 1787–1860 in current code). This includes:
- Moving average checkbox + window selector
- SG bar trace (primary y-axis)
- % Inside 8 ft line trace (secondary y-axis)
- All existing layout/styling

No changes to this section.

### Section 5: Collapsible Shot Detail Table

```python
with st.expander("View All Short Game Shots"):
    st.dataframe(sg["shot_detail"], use_container_width=True, hide_index=True)
```

---

## Execution Order

Tasks must be done in this order due to dependencies:

```
Step 1: helpers.py (sg_distance_bucket)
   ↓
Step 2: engines/short_game.py (engine rewrite — depends on Step 1)
   ↓
Step 3: app.py CSS (add new card classes — no dependency on Step 2, but group with Step 4)
   ↓
Step 4: app.py short_game_tab() (UI rewrite — depends on Steps 2 + 3)
   ↓
Step 5: Smoke test (run streamlit app, verify no import/runtime errors)
```

---

## Backward Compatibility Checklist

These keys in the return dict are consumed by other engines and **must be preserved**:

| Key | Consumer | Status |
|-----|----------|--------|
| `total_sg` | `overview.py:27`, `coachs_corner.py:358` | Preserved |
| `empty` | `app.py:1706` | Preserved |
| `sg_per_round` | `short_game_narrative()` | Preserved (moved into hero_metrics too) |
| `df` | Internal / tiger5 | Preserved |

Function signature is unchanged:
```python
build_short_game_results(filtered_df, num_rounds) → dict
```

Tab function signature is unchanged:
```python
short_game_tab(sg, num_rounds) → None
```

---

## Edge Cases & Defensive Logic

| Scenario | Handling |
|----------|----------|
| No short game shots | Return `"empty": True` with zeroed metrics; UI shows `st.warning()` |
| No shots in a heat map cell | `NaN` in pivot → blank cell (no color, no text) |
| No FW/Rough shots | `pct_inside_8_fr = 0.0` (safe divide) |
| No Sand shots | `pct_inside_8_sand = 0.0` (safe divide) |
| No shots 25–50 or < 25 | `sg_25_50 = 0.0` or `sg_arg = 0.0` (sum of empty series) |
| `num_rounds = 0` | `sg_per_round = 0.0` (guarded divide) |
| NaN in Ending Distance | `errors='coerce'` already applied; NaN excluded from aggregations |
| Leave bucket with 0 shots | `reindex(..., fill_value=0)` ensures bucket appears with 0 |

---

## Testing Strategy

Since the codebase has no existing test framework, validate by:

1. **Import check**: `python -c "from engines.short_game import build_short_game_results"`
2. **Helper check**: `python -c "from engines.helpers import sg_distance_bucket; assert sg_distance_bucket(5) == '<10'"`
3. **Streamlit run**: `streamlit run app.py` — verify all 5 sections render without error
4. **Empty state**: Filter to a player/date range with no short game shots — verify warning shown
5. **Visual check**: Confirm heat map colors diverge correctly (green = positive SG, red = negative)
