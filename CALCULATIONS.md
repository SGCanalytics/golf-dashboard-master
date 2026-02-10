
# Golf Dashboard Calculations Documentation

This document provides a comprehensive overview of all calculations defined across the golf dashboard engines.

---

## Table of Contents

1. [Strokes Gained Core Engine](#1-strokes-gained-core-engine)
2. [Hole Summary Engine](#2-hole-summary-engine)
3. [Tiger 5 Engine](#3-tiger-5-engine)
4. [Driving Engine](#4-driving-engine)
5. [Approach Engine](#5-approach-engine)
6. [Short Game Engine](#6-short-game-engine)
7. [Putting Engine](#7-putting-engine)
8. [Overview Engine](#8-overview-engine)
9. [Coach's Corner Engine](#9-coachs-corner-engine)
10. [Comparison Engine](#10-comparison-engine)
11. [Helper Functions](#11-helper-functions)

---

## 1. Strokes Gained Core Engine

**File:** [`engines/strokes_gained.py`](engines/strokes_gained.py)

### 1.1 Core SG Formula

```
SG = Expected Strokes(start_location, start_distance) - Expected Strokes(end_location, end_distance) - strokes_consumed
```

**Where:**
- `strokes_consumed = 1` for normal shots
- `strokes_consumed = 2` if penalty = 'Yes' (1 extra stroke)

### 1.2 Expected Strokes Lookup

The expected strokes are looked up from benchmark CSV files based on:
- **Location:** Tee, Fairway, Rough, Sand, Recovery, Green (Putt)
- **Distance:** Rounded to nearest integer, clamped to 0-600 yards/feet

**Benchmark Files:**
- `data/benchmarks/pga_tour.csv` - PGA Tour baseline
- `data/benchmarks/elite_college.csv` - Elite College (+3) baseline
- `data/benchmarks/competitive_scratch.csv` - Competitive Scratch (0) baseline

### 1.3 Special Cases

| Scenario | Expected Strokes |
|----------|-----------------|
| Distance ≤ 0 (holed out) | 0.0 |
| Unknown location | None (calculation skipped) |

---

## 2. Hole Summary Engine

**File:** [`engines/hole_summary.py`](engines/hole_summary.py)

### 2.1 Hole Score Calculation

```
Hole Score = num_shots + num_penalties
```

### 2.2 Score Name Classification

| Score vs Par | Label |
|--------------|-------|
| ≤ -2 | Eagle |
| -1 | Birdie |
| 0 | Par |
| 1 | Bogey |
| ≥ 2 | Double or Worse |

### 2.3 Aggregated Metrics

```
num_shots = count of Shot column per hole
num_penalties = count of Penalty = 'Yes' per hole
num_putts = count of Shot Type = 'Putt' per hole
total_sg = sum of Strokes Gained per hole
```

---

## 3. Tiger 5 Engine

**File:** [`engines/tiger5.py`](engines/tiger5.py)

### 3.1 Tiger 5 Categories

| Category | Definition | Attempts | Fails |
|----------|-----------|----------|-------|
| **3 Putts** | Any hole with ≥3 putts | Holes with ≥1 putt | Holes with ≥3 putts |
| **Double Bogey** | Score ≥ par + 2 | All holes | Score ≥ par + 2 |
| **Par 5 Bogey** | Par 5 holes with score ≥ 6 | Par 5 holes only | Score ≥ 6 on Par 5 |
| **Missed Green** | Short game shot not ending on green | Holes with short game shot | Any short game shot not on green |
| **125yd Bogey** | Scoring shot inside 125yd resulting in bogey+ | Shot on par 3 hole (Shot 1), par 4 (Shot 2), par 5 (Shot 3) from ≤125yd | Hole score > par |

### 3.2 Grit Score

```
Grit Score = ((total_attempts - total_fails) / total_attempts) × 100
```

**Where total_attempts = sum of attempts across all 5 categories**

### 3.3 Tiger 5 Root Cause Categories

Root causes are classified into:
- Driving
- Approach
- Short Game
- Short Putts (< 6 ft)
- Lag Putts (≥ 6 ft)

---

## 4. Driving Engine

**File:** [`engines/driving.py`](engines/driving.py)

### 4.1 Fairway Percentage

```
Fairway % = (fairway_ends + green_ends) / total_drives × 100
```

**Ending Locations Counted:**
- Fairway
- Rough
- Sand
- Recovery
- Green

### 4.2 Non-Playable Rate

```
Non-Playable = shots ending in Recovery OR Sand OR penalty = 'Yes'

Non-Playable % = non_playable_count / total_drives × 100
```

### 4.3 SG Playable Drives

```
Playable = shots ending in Fairway OR Rough (no penalty)

SG Playable = sum of SG for playable drives
SG Playable/Per Round = SG Playable / num_rounds
```

### 4.4 Driving Distance (P90)

```
P90 = 90th percentile of (Starting Distance - Ending Distance) for non-penalty drives
```

### 4.5 OB/Re-tee Detection

```
OB/Re-tee = holes where ≥2 shots start on Tee
```

### 4.6 Avoidable Loss

```
Avoidable Loss = shots where:
  - SG ≤ -0.25
  - Ending Location in (Fairway, Rough, Sand)
  - No penalty

Avoidable Loss % = avoidable_count / total_drives × 100
```

### 4.7 Trouble to Bogey Rate

```
Trouble to Bogey = drives ending in Recovery where hole score ≥ par + 1

Trouble to Bogey % = trouble_to_bogey_fails / trouble_to_bogey_attempts × 100
```

### 4.8 Double Penalty Rate

```
Double Penalty = penalty holes (excluding OB) where score ≥ par + 2

Double Penalty % = double_penalty_fails / double_penalty_attempts × 100
```

### 4.9 Consistency Metrics

```
Positive SG % = (SG ≥ 0) count / total_drives × 100
Poor Drive % = (SG ≤ -0.15) count / total_drives × 100
SG Std Dev = standard deviation of SG across all drives
```

---

## 5. Approach Engine

**File:** [`engines/approach.py`](engines/approach.py)

### 5.1 Distance Buckets

| Bucket | Distance Range |
|--------|---------------|
| 50–100 | 50 ≤ distance < 100 |
| 100–150 | 100 ≤ distance < 150 |
| 150–200 | 150 ≤ distance < 200 |
| >200 | distance ≥ 200 |

**Rough-specific buckets:**
| Bucket | Distance Range |
|--------|---------------|
| <150 | distance < 150 |
| >150 | distance ≥ 150 |

### 5.2 Bucket Metrics

For each distance bucket, the following are calculated:

```
Total SG = sum of Strokes Gained for bucket
SG/Shot = Total SG / shot_count
Proximity = mean of Ending Distance
Green Hit % = (shots ending on Green) / shot_count × 100
Shots = count of shots in bucket
```

### 5.3 Positive/Poor Shot Rates

```
Positive Shot Rate = (SG ≥ 0) count / total_approach_shots × 100
Poor Shot Rate = (SG ≤ -0.15) count / total_approach_shots × 100
```

### 5.4 Fairway vs Rough SG

```
SG Fairway = sum of SG for shots with Starting Location = 'Fairway'
SG Rough = sum of SG for shots with Starting Location = 'Rough'
```

---

## 6. Short Game Engine

**File:** [`engines/short_game.py`](engines/short_game.py)

### 6.1 Distance Buckets

| Bucket | Distance Range |
|--------|---------------|
| <10 | 0 ≤ distance < 10 |
| 10–20 | 10 ≤ distance < 20 |
| 20–30 | 20 ≤ distance < 30 |
| 30–40 | 30 ≤ distance < 40 |
| 40–50 | 40 ≤ distance < 50 |

### 6.2 Leave Distance Buckets

| Bucket | Leave Distance |
|--------|---------------|
| 0–3 | 0 ≤ distance ≤ 3 ft |
| 4–6 | 3 < distance ≤ 6 ft |
| 7–10 | 6 < distance ≤ 10 ft |
| 10–20 | 10 < distance ≤ 20 ft |
| 20+ | distance > 20 ft |

### 6.3 Hero Metrics

```
SG Total = sum of all short game SG
SG/Per Round = SG Total / num_rounds

SG 25-50 = sum of SG for shots with Starting Distance ≥ 25 yards
SG Around Green = sum of SG for shots with Starting Distance < 25 yards

% Inside 8 ft (FW/Rough) = shots from Fairway/Rough ending on Green within 8 ft / total FW/Rough shots × 100
% Inside 8 ft (Sand) = shots from Sand ending on Green within 8 ft / total sand shots × 100
```

### 6.4 Heatmap Data

Mean SG and shot count pivoted by:
- **Rows:** Starting Location (Fairway, Rough, Sand)
- **Columns:** Distance Bucket (<10, 10–20, 20–30, 30–40, 40–50)

---

## 7. Putting Engine

**File:** [`engines/putting.py`](engines/putting.py)

### 7.1 Distance Buckets (for tables)

| Bucket | Distance Range |
|--------|---------------|
| 0–3 | 0 < distance ≤ 3 ft |
| 4–6 | 3 < distance ≤ 6 ft |
| 7–10 | 6 < distance ≤ 10 ft |
| 10–20 | 10 < distance ≤ 20 ft |
| 20–30 | 20 < distance ≤ 30 ft |
| 30+ | distance > 30 ft |

### 7.2 Hero Metrics

```
SG Total = sum of all putting SG
SG/Per Round = SG Total / num_rounds

SG 3-6 ft = sum of SG for putts with Starting Distance 3-6 ft
SG 7-10 ft = sum of SG for putts with Starting Distance 7-10 ft

Make % 0-3 ft = made_putts / attempts × 100 (for 0-3 ft putts)
Lag Miss % = (first putts ≥ 20 ft leaving > 5 ft) / first putts ≥ 20 ft × 100
```

### 7.3 Lag Metrics (putts ≥ 20 ft)

```
Avg Leave = mean of Ending Distance for lag putts
% Inside 3 ft = (leave ≤ 3 ft) / total_lag_putts × 100
% Over 5 ft = (leave > 5 ft) / total_lag_putts × 100
```

### 7.4 Three-Putt Analysis

**Three-Putt Start Distribution:** First-putt distance on holes with 3+ putts bucketed into:
- <20 ft, 20–30 ft, 30–40 ft, 40+ ft

### 7.5 Outcome Classification

For first putts, hole outcomes classified by total putts:
- 1-Putt: hole completed in 1 putt
- 2-Putt: hole completed in 2 putts
- 3+ Putt: hole required 3+ putts

---

## 8. Overview Engine

**File:** [`engines/overview.py`](engines/overview.py)

### 8.1 SG by Category

```
Total SG = sum of all Strokes Gained
SG/Per Round = Total SG / num_rounds

SG by Category:
  - Driving: from driving_results["driving_sg"]
  - Approach: from approach_results["total_sg"]
  - Short Game: from short_game_results["total_sg"]
  - Putting: from putting_results["total_sg_putting"]
```

### 8.2 Tee-to-Green SG

```
SG Tee-to-Green = Driving SG + Approach SG + Short Game SG
```

### 8.3 Scoring Average

```
Scoring Average = mean of Hole Score across all holes
```

### 8.4 SG Separators

| Separator | Definition |
|-----------|------------|
| SG Putting 3–6ft | Putts with 3 ≤ distance ≤ 6 ft |
| SG Putting 25+ft | Putts with distance ≥ 25 ft |
| SG Approach 100–150yd | Approaches with 100 ≤ distance ≤ 150 yd |
| SG Approach 150–200yd | Approaches with 150 ≤ distance ≤ 200 yd |
| SG Approach Rough <150yd | Approaches from Rough with distance < 150 yd |
| SG Playable Drives | Drives ending in Fairway, Rough, or Sand |
| SG Around Green | Short Game with starting distance ≤ 25 yd |

### 8.5 Hole Outcomes Distribution

Counts and percentages for each score name (Eagle, Birdie, Par, Bogey, Double or Worse)

---

## 9. Coach's Corner Engine

**File:** [`engines/coachs_corner.py`](engines/coachs_corner.py)

### 9.1 Mental Metrics

#### Bounce Back Rate

```
Opportunity = bogey or worse (score ≥ par + 1) on hole h (not hole 18)
Success = par or better (score ≤ par) on hole h+1

Bounce Back Rate = successes / opportunities × 100
```

#### Drop-Off Rate

```
Opportunity = bogey or worse (score ≥ par + 1) on hole h
Event = bogey or worse (score ≥ par + 1) on hole h+1

Drop-Off Rate = events / opportunities × 100
```

#### Gas Pedal Rate

```
Opportunity = birdie or better (score ≤ par - 1) on hole h
Success = birdie or better (score ≤ par - 1) on hole h+1

Gas Pedal Rate = successes / opportunities × 100
```

#### Bogey Train Rate (BTR)

```
Bogey Plus Hole = score ≥ par + 1
Bogey Train = 2+ consecutive bogey+ holes (within same round)

BTR = bogey_train_holes / bogey_plus_holes × 100
```

#### Pressure Finish Performance

Compare holes 16-18 vs baseline (all holes):

```
Finish Score to Par = sum(Hole Score - Par) for holes 16-18
Finish SG = sum(Strokes Gained) for holes 16-18
Finish SG/Hole = Finish SG / holes_16_18
SG vs Baseline = Finish SG/Hole - Baseline SG/Hole
```

#### Early Round Composure

Compare holes 1-3 vs baseline:

```
Early Score to Par = sum(Hole Score - Par) for holes 1-3
Early SG = sum(Strokes Gained) for holes 1-3
Early SG/Hole = Early SG / holes_1_3
SG vs Baseline = Early SG/Hole - Baseline SG/Hole
```

#### Mistake Penalty Index (MPI)

Compare holes with Tiger 5 fails vs clean holes:

```
MPI = fail_score_per_hole - clean_score_per_hole
```

### 9.2 Legacy Metrics

#### GIR Flags

```
GIR Flag = bucket where Green Hit % < 50%
```

#### Short Game Flags

```
% Inside 8 ft (FW/Rough) = (shots from FW/Rough ending on Green ≤ 8 ft) / total FW/Rough shots × 100
% Inside 8 ft (Sand) = (shots from Sand ending on Green ≤ 8 ft) / total sand shots × 100
```

#### Putting Flags

```
Make % 4-5 ft = made / attempts × 100 for putts 4-5 ft
SG 5-10 ft = sum of SG for putts 5-10 ft
Lag Miss % = (putts ≥ 30 ft leaving > 5 ft) / putts ≥ 30 ft × 100
3-Putts Inside 20 = count of 3-putt holes where first putt started ≤ 20 ft
```

#### Green/Yellow/Red Classification

```
Green = shots with SG > 0
Yellow = shots with -0.5 ≤ SG ≤ 0
Red = shots with SG < -0.5
```

#### Bogey Avoidance

```
Bogey Rate = (holes with score > par) / total_holes × 100
(Also computed separately for Par3, Par4, Par5)
```

#### Birdie Opportunities

```
Opportunity = first putt ≤ 20 ft
Conversion = opportunity hole with birdie or better

Conversion % = conversions / opportunities × 100
```

---

## 10. Comparison Engine

**File:** [`engines/comparison.py`](engines/comparison.py)

### 10.1 Round Quality Classification

| Category | Score vs Par |
|----------|-------------|
| Under Par | < 0 |
| Even - +3 | 0 to +3 |
| >+4 | ≥ +4 |

### 10.2 Time Period Splitting

```
Recent Rounds = last N rounds by date
Previous Rounds = N rounds before recent rounds
```

### 10.3 Group Processing Metrics

For each comparison group, calculates:

| Metric | Calculation |
|--------|-------------|
| Scoring Average | mean of Hole Score |
| Total SG | sum of Strokes Gained |
| SG/Per Round | Total SG / num_rounds |
| SG by Category | sum of SG per shot type / num_rounds |
| Approach by Bucket | sum of SG per distance bucket / num_rounds |
| Putting by Bucket | sum of SG per distance bucket / num_rounds |
| Short Game by Bucket | sum of SG per distance bucket / num_rounds |
| Hole Outcomes | counts of Eagle, Birdie, Par, Bogey, Double+ |
| Fairway % | (Fairway + Green) / drives × 100 |
| GIR % | Green / approaches × 100 |

### 10.4 Mental Metrics in Comparison

Same mental metrics as Coach's Corner, computed per group:
- Bounce Back Rate
- Drop-Off Rate
- Gas Pedal Rate
- Bogey Train Rate

---

## 11. Helper Functions

**File:** [`engines/helpers.py`](engines/helpers.py)

### 11.1 Distance Bucket Functions

```python
bucket_distance(dist):
    "<50" if dist < 50
    "50–100" if 50 ≤ dist < 100
    "100–150" if 100 ≤ dist < 150
    "150–200" if 150 ≤ dist < 200
    "200+" if dist ≥ 200

sg_distance_bucket(dist):
    "<10" if dist < 10
    "10–20" if 10 ≤ dist < 20
    "20–30" if 20 ≤ dist < 30
    "30–40" if 30 ≤ dist < 40
    "40–50" if dist ≥ 40
```

### 11.2 Safe Divide

```python
safe_divide(a, b):
    returns a / b if b != 0, else 0
```

---

## Appendix: Shot Type Categories

| Shot Type | Description |
|-----------|-------------|
| Driving | Tee shots on par 4 and par 5 holes only (tee shots on par 3 are classified as Approach) |
| Approach | Shots to the green from >25 yards |
| Short Game | Shots within 25 yards of green |
| Putting | Shots on the green |
| Recovery | Recovery shots from difficult lies |
| Other | Any shots not fitting above categories |

---

## Appendix: Ending Location Categories

| Location | Description |
|----------|-------------|
| Fairway | Drive or shot ending in fairway |
| Rough | Drive or shot ending in rough |
| Sand | Shot ending in sand trap |
| Recovery | Shot from difficult/embedded lie |
| Green | Any shot ending on green |
| Hole | Shot that went in (ending distance = 0) |

---

*Last Updated: February 2025*
*Generated from engine code analysis*
