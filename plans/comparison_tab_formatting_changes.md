# Comparison Tab Formatting Changes Plan

## Overview
This plan outlines formatting changes to the Comparison tab based on user requirements.

---

## Change 1: Group Summary Text Box Restructuring

**File**: [`tabs/comparison.py`](tabs/comparison.py:51) - `render_group_summary()` function

**Current Behavior**:
- Single-line summary displayed vertically (group 1 then group 2)
- Shows: `{g1_label}: {num_rounds} rounds | Avg: {scoring_avg} | SG: {total_sg} ({sg_per_round}/r) | Low: {low_score} | High: {high_score}`

**Required Changes**:
1. **Two-column layout**: Split into left column (group 1) and right column (group 2)
2. **Rename "Avg" to "Total score avg"**: Change label text
3. **Change "/r" to "/Rd"**: Update strokes gained per round notation

**Implementation**:
```python
# Left column (Group 1)
<div style="column">
  <span style="color:{COMPARISON_GROUP_1};font-weight:600;">{g1_label}</span>
  {group1['num_rounds']} rounds | Total score avg: {group1['scoring_avg']:.1f} | 
  SG: {group1['total_sg']:+.1f} ({group1['sg_per_round']:+.2f}/Rd) |
  Low: {group1['low_score']} | High: {group1['high_score']}
</div>

# Right column (Group 2) - same structure with Group 2 colors and data
```

---

## Change 2: Hole Outcome Distribution - Per Round Instead of Total

**File**: [`tabs/comparison.py`](tabs/comparison.py:140) - `render_hole_outcomes()` function

**Current Behavior**:
- Shows total counts of hole outcomes (e.g., "Birdies: 45")
- Calculates percentages based on total holes

**Required Changes**:
- Display outcomes **per round** (divide count by number of rounds)
- Show values like "3.2/Rd" instead of total counts

**Implementation**:
```python
# Calculate per-round values
g1_birdies_per_round = group1['hole_outcomes'].get('Birdie', 0) / group1['num_rounds']
g1_bogeys_per_round = group1['hole_outcomes'].get('Bogey', 0) / group1['num_rounds']

# Update summary cards to show per-round values
f"Birdies: {g1_birdies_per_round:.1f}/Rd"
f"Bogeys: {g1_bogeys_per_round:.1f}/Rd"
```

**Also update chart title** from "Hole Outcomes (Count)" to "Hole Outcomes per Round"

---

## Change 3: Mental Characteristics - Card Layout with Labels

**File**: [`tabs/comparison.py`](tabs/comparison.py:309) - `render_mental_comparison()` function

**Current Behavior**:
- Uses `comparison_stat_row()` for Round Flow metrics
- Uses bullet points for Detailed Mental Metrics section

**Required Changes**:
1. **Card-based layout**: Use cards instead of bullet points for the detailed section
2. **Two-column layout**: Left column = Group 1 cards, Right column = Group 2 cards
3. **Add labels**: Each card needs a label (e.g., "Bounce Back", "Gas Pedal")
4. **Remove bullets**: Replace bullet list with card-based display

**Implementation**:
```python
# Two-column layout for detailed mental metrics
colA, colB = st.columns(2)

with colA:
    # Group 1 Cards
    comparison_stat_row(g1_label, format_pct(m1['bounce_back']['rate']),
                       "", "", "Bounce Back %")
    comparison_stat_row(g1_label, format_pct(m1['gas_pedal']['rate']),
                       "", "", "Gas Pedal %")
    comparison_stat_row(g1_label, format_pct(m1['drop_off']['rate']),
                       "", "", "Drop Off %")
    comparison_stat_row(g1_label, format_pct(m1['bogey_train_rate']['btr']),
                       "", "", "Bogey Train %")

with colB:
    # Group 2 Cards (same structure)
    comparison_stat_row(g2_label, format_pct(m2['bounce_back']['rate']),
                       "", "", "Bounce Back %")
    # ... etc
```

**Note**: May need to create a new component function `comparison_single_stat_card()` for single-group card display.

---

## Change 4: Basic Stats Cards - Add Labels

**File**: [`tabs/comparison.py`](tabs/comparison.py:380) - `render_basic_stats()` function

**Current Behavior**:
- Cards for Rounds and Scoring Avg have group labels but no metric labels

**Required Changes**:
- Add metric labels to the bottom cards (Rounds and Scoring Avg cards)

**Implementation**:
```python
# Rounds card - already has "Rounds" subtitle, verify it's visible
<div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};">Rounds</div>

# Scoring Avg card - add "Scoring Avg" label (already exists, verify)
<div style="font-family:{FONT_BODY};font-size:0.6rem;color:{SLATE};">Scoring Avg</div>
```

**Note**: The labels already exist in the code (lines 429 and 452). Need to verify they are styled consistently with other metric labels.

---

## Summary of Changes

| Change | Location | Impact |
|--------|----------|--------|
| 1a. Two-column group summary | `render_group_summary()` | High - restructures main summary |
| 1b. Rename "Avg" to "Total score avg" | `render_group_summary()` | Low - text change |
| 1c. Change "/r" to "/Rd" | `render_group_summary()` | Low - text change |
| 2. Per-round hole outcomes | `render_hole_outcomes()` | Medium - recalculates values |
| 3. Mental cards with labels | `render_mental_comparison()` | High - restructures section |
| 4. Add labels to basic stats | `render_basic_stats()` | Low - verify/fix styling |

---

## Files to Modify

1. [`tabs/comparison.py`](tabs/comparison.py) - Main implementation changes
2. [`ui/components.py`](ui/components.py) - May need new component function for single-group cards

---

## Testing Checklist

- [ ] Group summary displays in two columns
- [ ] "Total score avg" label is correct
- [ ] "/Rd" notation is used for strokes gained per round
- [ ] Hole outcomes show per-round values (e.g., "3.2/Rd")
- [ ] Mental characteristics section uses card layout with two columns
- [ ] Cards have clear labels
- [ ] Bullet points are removed from mental section
- [ ] Basic stats cards have visible metric labels
