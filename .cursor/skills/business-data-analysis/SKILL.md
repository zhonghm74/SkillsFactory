---
name: business-data-analysis
description: Build KPI/driver trees, run anomaly root-cause diagnostics, verify business hypotheses, and produce executive reports using the Minto Pyramid. Use when asked to diagnose metric shifts, map business indicators, validate customer/operations/policy assumptions, or deliver decision-ready analysis. For charting and visual storytelling output, explicitly invoke the data-visualization skill with prepared chart specs. Do not use for pure ETL/data cleaning, model training, or visualization-only styling.
license: MIT
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
metadata:
  version: 0.2.0
  domains: [business-analysis, kpi, rca, causality, reporting]
  outputs: [driver-tree, rca-summary, hypothesis-summary, executive-report, chart-specs, visualization-brief]
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
- Visualization policy: this skill prepares chart specifications and business narrative context; the
  `data-visualization` skill is responsible for chart design quality, accessibility checks, and
  annotation/story polish.

## Process

### Phase 1: Indicator Mapping + Anomaly Diagnostics

1. Define top-level objective metric.
2. Decompose into drivers and sub-drivers.
3. Assign owners, thresholds, and action corridors.
4. Mark known conflicts (for example, speed vs quality).

5. Execute 7-step RCA sequence from references.
6. Distinguish data quality issues from behavior shifts.
7. Isolate affected segments and decompose ratios.
8. Produce suspected-cause shortlist with confidence notes.

### Phase 2: Hypothesis Verification

1. Formulate falsifiable hypothesis.
2. Select verification path:
   - customer structure (cohorts)
   - operations (event/dependency checks)
   - policy (counterfactual methods)
3. Run predict-then-verify loop; update confidence.

### Phase 3: Executive Reporting + Visualization (Minto + `data-visualization`)

1. Lead with BLUF assertion.
2. Group support arguments in MECE structure.
3. Attach evidence and caveats.
4. Prepare `chart_specs` from validated findings:
   - trend charts for metric evolution
   - comparison bars for cohort/channel differences
   - decomposition chart for numerator/denominator or funnel stages
5. Invoke `data-visualization` skill for each chart spec:
   - request chart type selection rationale
   - require axis-integrity and accessibility checks
   - require insight-led title + annotations
6. Merge returned visuals into report appendix and executive narrative.
7. End with recommended action, owner, and timeline.

## Required Script Calls

```bash
python scripts/build_driver_tree.py input.json --output out/driver_tree.json
python scripts/run_rca_checklist.py incident.json --output out/rca.md
python scripts/validate_report.py out/executive_report.md
```

## Cross-Skill Invocation Contract (`data-visualization`)

Use this payload when handing off:

```yaml
business_context:
  objective: "<business objective>"
  key_question: "<decision question>"
chart_spec:
  chart_type_candidate: "<bar|line|scatter|100%-stacked>"
  x: "<dimension>"
  y: "<metric>"
  segment: "<optional segment>"
  baseline_policy: "bar/column must start at zero unless explicitly justified"
  insight_claim: "<single sentence insight to emphasize>"
```

Expected return from `data-visualization`:
- recommended chart form + rationale
- integrity checks (axis/baseline/disclosure)
- accessibility checks (contrast/color-independent encoding)
- narrative layer (title + annotations + action implication)

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
5. `chart_specs` (structured specs for data-visualization handoff)
6. `visualization_brief` (chart list + intended business insight per chart)
7. `next_actions` (owner, timeline, success metric)

## Anti-Patterns

| Avoid | Why | Instead |
|---|---|---|
| Jumping to conclusions before RCA sequence | Causes false causality | Complete all 7 RCA steps first |
| Collecting all data before hypothesis framing | Analysis paralysis | Use falsifiable hypothesis-first loop |
| Reporting data chronologically without BLUF | Slows executive decisions | Use assertion-first Minto structure |
| Drawing charts directly here without visualization handoff | Inconsistent visual quality and accessibility | Hand off chart specs to `data-visualization` skill |

## Verification Checklist

- [ ] Driver tree links top objective to measurable sub-drivers.
- [ ] RCA includes all 7 diagnostic steps.
- [ ] Hypothesis is falsifiable and test path is explicit.
- [ ] Report is answer-first and MECE.
- [ ] Chart specs are prepared for `data-visualization` and linked to core findings.
- [ ] Final recommendation includes owner and execution timeline.

## Extension Points

1. Add causal method selector for DiD/synthetic-control workflows.
2. Add attribution model recommendation helper for channel analysis.
3. Add bias audit script for confirmation/selection/survivorship checks.
4. Add automated bridge script to convert analysis outputs into `data-visualization` payloads.

## References

- [Indicator / Driver Tree](references/indicator-driver-tree.md)
- [Anomaly RCA Playbook](references/anomaly-rca-playbook.md)
- [Hypothesis Verification Loops](references/hypothesis-verification-loops.md)
- [Minto Pyramid Reporting](references/minto-pyramid-reporting.md)
