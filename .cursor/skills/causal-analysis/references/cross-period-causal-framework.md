# Cross-Period Causal Framework

## Goal
Estimate incremental impact when strategy changes across periods (for example, Period A policy vs Period B policy), while reducing selection bias and confounding.

## Five-stage pipeline

1. **Causal estimand definition**
   - Define treatment `T`, outcome `Y`, covariates `X`.
   - Choose estimand: ATE / ATT / CATE.
2. **Distribution alignment**
   - Fit propensity model `P(T=1|X)`.
   - Build stabilized IPW weights.
   - Check overlap and standardized mean differences (SMD).
3. **Orthogonalization**
   - Residualize high-correlation features against confounders.
   - Compare key conclusions before/after residualization.
4. **HTE/Uplift estimation**
   - Use X-learner style workflow when treatment assignment is imbalanced.
   - Use causal-forest style workflow when strong nonlinear interactions are expected.
5. **Ranking-based evaluation**
   - Build uplift decile table.
   - Report AUUC/Qini with caveats.
   - Add balanced checks so model is not rewarded for selecting baseline high-converters only.

## Practical cautions

- Do not treat period indicator as causal by default.
- Do not claim unsupported effects in poor-overlap regions.
- Do not use plain AUC/F1 to evaluate uplift ranking quality.
