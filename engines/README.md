# Engine Interface Standards

This document describes the standard patterns and conventions used across all analytics engines in the golf dashboard.

## Engine Function Naming Convention

### Public Functions (exported to app.py)
- Use `build_*` prefix for main engine functions
- Examples: `build_driving_results()`, `build_approach_results()`, `build_putting_results()`

### Private Helper Functions (internal to engine)
- Use `_` prefix for all internal helper functions
- Examples: `_compute_bucket_metrics()`, `_build_hero_metrics()`, `_enrich_putting_df()`

## Standard Return Structure

All main engine functions should return a dictionary with:

1. **Empty state indicator** (optional but recommended):
   ```python
   {
       "empty": bool,  # True if no data available
       ...
   }
   ```

2. **Primary metrics**:
   - Total strokes gained: `total_sg` or category-specific (e.g., `driving_sg`)
   - Per-round metrics: `sg_per_round` or `*_per_round`

3. **Detailed data**:
   - DataFrames for tables/charts
   - Breakdown metrics by subcategory
   - Hero card values

## Current Engine Functions

| Engine | Main Function | Return Keys Used By Tabs |
|--------|---------------|-------------------------|
| `driving.py` | `build_driving_results()` | `num_drives`, `driving_sg`, `fairway_pct`, `sg_by_result`, etc. |
| `approach.py` | `build_approach_results()` | `empty`, `total_sg`, `sg_per_round`, `fairway_tee_metrics`, etc. |
| `short_game.py` | `build_short_game_results()` | `empty`, `total_sg`, `sg_per_round`, `hero_metrics`, etc. |
| `putting.py` | `build_putting_results()` | `empty`, `total_sg_putting`, `hero_metrics`, `bucket_table`, etc. |
| `tiger5.py` | `build_tiger5_results()` | Returns tuple: `(results_dict, total_fails, grit_score)` |
| `scoring_performance.py` | `build_scoring_performance()` | Various scoring metrics |
| `coachs_corner.py` | `build_coachs_corner()` | `sg_summary`, `performance_drivers`, `practice_priorities`, etc. |

## Distance Bucketing Functions (helpers.py)

All distance bucketing functions are centralized in `engines/helpers.py`:

### Short Game Distance Buckets (0-50 yards)
```python
sg_distance_bucket(dist) -> str
```
Returns: `"<10"`, `"10–20"`, `"20–30"`, `"30–40"`, `"40–50"`

### Approach Distance Buckets (50-200+ yards)
```python
approach_distance_bucket(dist) -> str | None
```
Returns: `"50–100"`, `"100–150"`, `"150–200"`, `">200"`, or `None` if outside range

### Rough Distance Buckets
```python
rough_distance_bucket(dist) -> str
```
Returns: `"<150"` or `">150"`

### Zone Distance Buckets (Green/Yellow/Red Zones)
```python
zone_distance_bucket(dist) -> str | None
```
Returns:
- `"Green Zone"` (75-125 yards)
- `"Yellow Zone"` (125-175 yards)
- `"Red Zone"` (175-225 yards)
- `None` if outside 75-225 range

### Leave Distance Buckets (putting proximity)
```python
leave_distance_bucket(dist) -> str
```
Returns: `"0–3"`, `"4–6"`, `"7–10"`, `"10–20"`, `"20+"` (in feet)

## Bucket Constants

Canonical bucket label arrays for consistent ordering:

```python
from engines.helpers import (
    SHORT_GAME_BUCKETS,  # ["<10", "10–20", "20–30", "30–40", "40–50"]
    APPROACH_BUCKETS,    # ["50–100", "100–150", "150–200", ">200"]
    ROUGH_BUCKETS,       # ["<150", ">150"]
    ZONE_BUCKETS,        # ["Green Zone", "Yellow Zone", "Red Zone"]
    LEAVE_BUCKETS,       # ["0–3", "4–6", "7–10", "10–20", "20+"]
    LIE_ORDER,           # ["Fairway", "Rough", "Sand"]
    ZONE_RANGES,         # {"Green Zone": "75-125", ...}
)
```

## Utility Functions

### Safe Division
```python
safe_divide(a, b) -> float
```
Returns `a / b` if `b > 0`, otherwise returns `0`. Prevents division by zero errors.

## UI Components (ui/components.py)

### Standard Cards
- `premium_hero_card()` - Large hero metrics with colored border
- `premium_stat_card()` - Standard stat card
- `section_header()` - Section titles

### Sentiment Helpers
- `sg_sentiment(val, threshold=None)` - Determine sentiment from SG value
- `pct_sentiment_above(val, threshold_key)` - Positive when value >= threshold
- `pct_sentiment_below(val, threshold_key)` - Positive when value <= threshold

### Coach's Corner Cards
- `performance_driver_card(rank, driver)` - Performance drivers with severity
- `practice_priority_card(item, number, border_color)` - Practice priorities
- `strength_maintenance_card(item, number)` - Strength cards
- `compact_stat_card(label, value, subtitle, sentiment)` - Compact stats
- `player_path_category_card(entry, is_strength)` - PlayerPath categories

### Sentiment Helpers (Coach's Corner)
- `severity_color(severity)` - Get color for severity level
- `bounce_back_sentiment(pct)` - Bounce back percentage sentiment
- `drop_off_sentiment(pct)` - Drop off percentage sentiment
- `gas_pedal_sentiment(pct)` - Gas pedal percentage sentiment
- `bogey_train_sentiment(count)` - Bogey train count sentiment
- `grit_score_sentiment(score)` - Tiger 5 grit score sentiment
- `bogey_rate_sentiment(rate)` - Bogey rate sentiment
- `conversion_pct_sentiment(pct)` - Birdie conversion sentiment

## Best Practices

1. **Distance Conversion**: Distance fields (`Starting Distance`, `Ending Distance`) are automatically converted to numeric in `data/load_data.py`. Engines do not need to convert them again.

2. **Bucket Function Usage**: Always import and use centralized bucket functions from `helpers.py` rather than creating local implementations.

3. **Consistent Naming**: Follow the established naming conventions for public (`build_*`) and private (`_*`) functions.

4. **UI Components**: Use shared UI components from `ui/components.py` rather than creating inline HTML or custom local functions.

5. **Sentiment Logic**: Use centralized sentiment helper functions from `ui/components.py` for consistent color/sentiment decisions.

## Migration Notes

Recent refactoring consolidated:
- Distance bucketing functions → `helpers.py`
- Sentiment/color logic → `ui/components.py`
- Card components → `ui/components.py`
- Distance numeric conversion → `load_data.py`

When creating new engines or modifying existing ones, use these centralized utilities to maintain consistency.
