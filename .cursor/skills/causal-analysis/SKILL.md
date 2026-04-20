---
name: causal-analysis
description: Estimate cross-period causal effects and heterogeneous treatment effects (HTE/Uplift) under covariate shift and multicollinearity. Use for policy comparison (e.g., Feb vs Mar strategy), individual uplift ranking, robust attribution (SHAP interaction), and decision-ready causal recommendations. Avoid for pure prediction-only tasks.
license: MIT
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
metadata:
  version: 0.1.0
  domains: [causal-inference, uplift-modeling, hte, policy-evaluation, attribution]
  outputs: [causal-plan, weighted-data, residualized-data, hte-summary, uplift-eval, causal-report, chart-specs]
---

# Causal Analysis

Use this skill when business questions are counterfactual:
- "Which strategy works better for which users?"
- "If we switch policy A to policy B, how much incremental conversion do we gain?"
- "How to avoid fake important features under multicollinearity?"

This skill follows a five-stage framework:
1) Distribution alignment (IPW),
2) Orthogonalization (FWL / DML mindset),
3) HTE estimation (X-Learner / Causal Forest),
4) Causal attribution (SHAP interaction),
5) Uplift evaluation (Qini / AUUC / PUC-like balanced checks).

## Triggers

- `compare two campaign periods with causal method`
- `estimate uplift by user segment`
- `find true causal drivers under correlated features`
- `build HTE model and explain why`
- `evaluate policy switch impact with qini/auuc`

## Scope Boundary

- In-scope:
  - cross-period causal effect estimation,
  - observational adjustment for selection bias,
  - heterogeneous treatment effect estimation and ranking,
  - robust attribution under collinearity,
  - causal evaluation and recommendation packaging.
- Out-of-scope:
  - pure ETL/data cleaning requests,
  - prediction-only model tuning without causal estimand,
  - dashboard visual styling-only work.

## Process

### Phase 0: Causal Question & Assumptions

1. Define treatment (`T`: old vs new strategy), outcome (`Y`), and covariates (`X`).
2. State estimand explicitly (ATE, CATE, ATT, uplift ranking objective).
3. Record assumptions:
   - ignorability (conditional exchangeability),
   - overlap/positivity,
   - SUTVA risk and expected spillover.

### Phase 1: Covariate Shift Alignment (IPW)

1. Estimate propensity score `e(x)=P(T=1|X)`.
2. Compute stabilized inverse probability weights.
3. Diagnose overlap and balance (SMD before/after weighting).
4. If overlap is poor, trim/report unsupported regions rather than over-claiming.

### Phase 2: Orthogonalization for Collinearity Control

1. Residualize selected features against confounders (FWL-style).
2. Residualize outcome and/or treatment channels when needed.
3. Use residualized variables for effect modeling and sensitivity checks.
4. Report which conclusions are stable before/after orthogonalization.

### Phase 3: HTE Estimation

1. Choose learner family by data condition:
   - treatment imbalance -> prefer X-Learner flow,
   - strong interaction and nonlinearity -> causal-forest style flow.
2. Produce CATE/uplift score for each unit.
3. Summarize segment-level uplift differences and negative-uplift pockets.

### Phase 4: Attribution (CATE-focused)

1. Compute/collect SHAP values on effect model output (not just baseline conversion model).
2. Prioritize SHAP interaction analysis for correlated features.
3. Separate:
   - main effect (independent causal contribution),
   - interaction effect (shared/entangled contribution).
4. Explicitly mark potential proxy features.

### Phase 5: Uplift Evaluation & Decision Packaging

1. Evaluate ranking quality using decile uplift table.
2. Report AUUC and Qini-like area, and balanced rate-based checks (PUC-style).
3. Package recommendations:
   - where to increase treatment,
   - where to hold out/avoid treatment,
   - expected incremental gain and risk notes.
4. Prepare chart specs and invoke `data-visualization` for final storytelling visuals.

## Required Script Calls

```bash
python scripts/estimate_ipw_weights.py scored_input.csv --treatment-col treatment --treated-value 1 --output out/weighted.csv --diagnostics out/ipw_balance.json
python scripts/residualize_features.py out/weighted.csv --confounders age,education,income --residualize-cols education,age --outcome-col conversion --output out/residualized.csv --diagnostics out/residualization.json
python scripts/build_uplift_eval.py model_scored.csv --treatment-col treatment --treated-value 1 --outcome-col conversion --score-col uplift_score --decile-output out/uplift_deciles.csv --metrics-output out/uplift_metrics.json
python scripts/validate_causal_report.py out/causal_report.md
```

## Output Contract

Produce these artifacts unless user asks otherwise:

1. `causal_plan` (estimand, assumptions, identification strategy)
2. `weighted_data` + `ipw_balance` diagnostics
3. `residualized_data` + residual diagnostics
4. `hte_summary` (segment-level uplift findings)
5. `uplift_eval` (deciles + AUUC + Qini + balanced checks)
6. `causal_report` (decision-ready narrative with caveats)
7. `chart_specs` for `data-visualization` handoff

## Anti-Patterns

| Avoid | Why | Instead |
|---|---|---|
| Directly compare period A vs B conversion means | confounded by targeting/population drift | estimate propensity and apply IPW first |
| Drop correlated features by correlation threshold only | may remove true causal driver | use orthogonalization + causal reasoning |
| Use Gini/PFI as final causal importance | unstable under collinearity/proxy effects | use CATE SHAP + interaction decomposition |
| Evaluate uplift model with AUC/F1 only | not aligned to incremental impact ranking | use decile uplift, AUUC, Qini, balanced checks |

## Verification Checklist

- [ ] Causal estimand and assumptions are explicit.
- [ ] IPW balance diagnostics (SMD before/after) are reported.
- [ ] Orthogonalization/residualization outputs are documented.
- [ ] HTE results identify positive and negative uplift segments.
- [ ] Attribution separates main vs interaction effects.
- [ ] Evaluation includes AUUC/Qini and decile uplift table.
- [ ] Final recommendation includes owner, timeline, and guardrails.

## References

- `references/cross-period-causal-framework.md`
- `references/orthogonalization-and-collinearity.md`
- `references/uplift-evaluation-metrics.md`
- Source article: `uploads/___________.md` (跨期样本差异化特征分析)
