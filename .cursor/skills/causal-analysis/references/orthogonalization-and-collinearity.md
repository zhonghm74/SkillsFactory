# Orthogonalization and Collinearity Handling

## Why this matters

In uplift/HTE settings, multicollinearity can create fake "important features":
- real driver: education,
- proxy feature: age,
- model importance may over-credit proxy variables.

## FWL intuition

For a target feature `x_j`:
1. Regress `x_j` on other controls `X_-j`, keep residual `r_xj`.
2. Regress outcome `Y` on controls `X_-j`, keep residual `r_y`.
3. Regress `r_y` on `r_xj`.

The slope isolates variation in `x_j` unexplained by other controls.

## Practical residualization in this skill

- Residualize selected columns against confounders.
- Optionally residualize outcome for sensitivity checks.
- Compare effect conclusions before/after residualization.

## Guardrails

- Do not remove features solely by correlation threshold.
- Document confounder list and rationale.
- Mark unstable signs/magnitudes across robustness checks.
