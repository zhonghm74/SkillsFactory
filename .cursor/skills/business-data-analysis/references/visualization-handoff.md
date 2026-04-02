# Visualization Handoff to `data-visualization` Skill

Use this handoff format when business analysis outputs need charts.

## Inputs to pass

1. **Business question**
   - What decision should the chart support?
2. **Data summary**
   - Grain, period, dimensions, measures.
3. **Insight intent**
   - Trend, comparison, composition, correlation, or anomaly focus.
4. **Integrity constraints**
   - Axis rules, known caveats, excluded records.
5. **Audience**
   - Executive / analyst / public.

## Chart request template

```markdown
Visualization request:
- Objective: <decision question>
- Dataset summary: <tables/fields/timeframe>
- Priority insights:
  1) <insight 1>
  2) <insight 2>
- Required chart types (if any): <bar/line/scatter/stacked>
- Constraints:
  - bar/column must start at zero unless explicitly justified
  - color usage must be accessibility-safe
- Deliverables:
  - chart spec
  - annotation notes
  - accessibility checks
```

## Required outputs from `data-visualization`

- Chart recommendation/spec
- Integrity checks (axis/scaling)
- Accessibility checks (contrast + color independence)
- Narrative annotations

## Integration back into report

Insert chart outputs into report sections:
- Supporting Arguments
- Evidence Summary
- Appendix (if dense technical visual details are needed)
