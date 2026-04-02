---
name: business-data-analysis
description: Build KPI/driver trees, run anomaly root-cause diagnostics, verify business hypotheses, and produce executive reports using the Minto Pyramid. Use when asked to diagnose metric shifts, map business indicators, validate customer/operations/policy assumptions, or deliver decision-ready analysis. Do not use for pure ETL/data cleaning, model training, or visualization-only styling.
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
  domains: [business-analysis, kpi, rca, causality, reporting]
  outputs: [driver-tree, rca-summary, hypothesis-summary, executive-report]
---

# Business Data Analysis

Turn business telemetry into decision-ready recommendations with explicit causal checks.

## Triggers

- `analyze this business metric drop`
- `build a KPI/driver tree for {goal}`
- `run root cause analysis for {kpi anomaly}`
- `validate this business hypothesis`
- `write an executive analysis report`

## Scope Boundary

- In-scope: indicator decomposition, anomaly diagnostics, hypothesis verification, executive reporting.
- Out-of-scope: pure data cleaning/ETL, model training, chart beautification-only requests.

## Process

### Phase 1: Indicator Mapping

1. Define top-level objective metric.
2. Decompose into drivers and sub-drivers.
3. Assign owners, thresholds, and action corridors.
4. Mark known conflicts (for example, speed vs quality).

### Phase 2: Anomaly Diagnostics

1. Execute 7-step RCA sequence from references.
2. Distinguish data quality issues from behavior shifts.
3. Isolate affected segments and decompose ratios.
4. Produce suspected-cause shortlist with confidence notes.

### Phase 3: Hypothesis Verification

1. Formulate falsifiable hypothesis.
2. Select verification path:
   - customer structure (cohorts)
   - operations (event/dependency checks)
   - policy (counterfactual methods)
3. Run predict-then-verify loop; update confidence.

### Phase 4: Executive Reporting (Minto)

1. Lead with BLUF assertion.
2. Group support arguments in MECE structure.
3. Attach evidence and caveats.
4. End with recommended action, owner, and timeline.

## Required Script Calls

```bash
python scripts/build_driver_tree.py input.json --output out/driver_tree.json
python scripts/run_rca_checklist.py incident.json --output out/rca.md
python scripts/validate_report.py out/executive_report.md
```

## Scripts

Deterministic checks and artifact builders used by this skill:

- `scripts/build_driver_tree.py`: Builds structured driver tree JSON from objective + drivers input.
- `scripts/run_rca_checklist.py`: Produces a 7-step RCA checklist markdown draft.
- `scripts/validate_report.py`: Validates Minto-style executive report structure and action fields.

### Script Exit Codes

- `0`: success
- `1`: general failure
- `3`: file not found
- `10`: validation failure

## Output Contract

Produce all artifacts unless user asks otherwise:

1. `driver_tree` (structured JSON)
2. `rca_summary` (markdown)
3. `hypothesis_summary` (markdown)
4. `executive_report` (BLUF + Minto structure)
5. `next_actions` (owner, timeline, success metric)

## Anti-Patterns

| Avoid | Why | Instead |
|---|---|---|
| Jumping to conclusions before RCA sequence | Causes false causality | Complete all 7 RCA steps first |
| Collecting all data before hypothesis framing | Analysis paralysis | Use falsifiable hypothesis-first loop |
| Reporting data chronologically without BLUF | Slows executive decisions | Use assertion-first Minto structure |

## Verification Checklist

- [ ] Driver tree links top objective to measurable sub-drivers.
- [ ] RCA includes all 7 diagnostic steps.
- [ ] Hypothesis is falsifiable and test path is explicit.
- [ ] Report is answer-first and MECE.
- [ ] Final recommendation includes owner and execution timeline.

## Extension Points

1. Add causal method selector for DiD/synthetic-control workflows.
2. Add attribution model recommendation helper for channel analysis.
3. Add bias audit script for confirmation/selection/survivorship checks.

## References

- [Indicator / Driver Tree](references/indicator-driver-tree.md)
- [Anomaly RCA Playbook](references/anomaly-rca-playbook.md)
- [Hypothesis Verification Loops](references/hypothesis-verification-loops.md)
- [Minto Pyramid Reporting](references/minto-pyramid-reporting.md)
