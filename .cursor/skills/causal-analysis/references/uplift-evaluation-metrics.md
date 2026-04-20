# Uplift Evaluation Metrics

## Why AUC/F1 is not enough

Uplift models rank users by expected incremental effect, not baseline conversion.
So traditional classification metrics can be misleading.

## Core Metrics

### 1) Decile uplift table

Steps:
1. Sort users by predicted uplift score descending.
2. Split into equal-size buckets (e.g., 10 deciles).
3. In each bucket, compute treated vs control conversion rates.
4. Uplift(decile) = rate_treated - rate_control.

Use this to identify:
- where intervention should be concentrated,
- where intervention is neutral,
- where intervention may hurt (negative uplift).

### 2) AUUC (Area Under Uplift Curve)

- Build cumulative incremental gain curve over ranked users.
- AUUC summarizes total ranking quality as area.
- Higher AUUC indicates better prioritization of persuadable users.

### 3) Qini / Qini-like area

- Similar to AUUC but benchmarked against random targeting baseline.
- Helps quantify incremental value over random policy.

### 4) Balanced / PUC-style check

To reduce bias from selecting already-high converters:
- compare treated-control differences using rate-normalized views,
- inspect both positive and negative outcome contribution,
- avoid over-crediting models that only find baseline-easy users.

## Reporting Template

Include:
- top-decile uplift (%),
- cumulative uplift by top-k population (10%, 20%, 30%),
- AUUC value,
- Qini value,
- negative uplift segment share (% users with predicted uplift < 0),
- deployment guardrails (where to suppress treatment).
