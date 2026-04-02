---
name: data-visualization
description: Design and critique truthful, accessible data visualizations and data stories. Use when asked to choose chart types, improve chart clarity, reduce chart junk, enforce axis integrity, apply WCAG contrast/color-blind-safe rules, or turn analysis into an executive narrative with actionable recommendations. Do not use for pure data cleaning/ETL, model training/tuning, or non-visual document editing tasks.
license: MIT
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
metadata:
  version: 1.0.0
  domains: [analytics, data-visualization, storytelling, accessibility]
  outputs: [chart-recommendation, chart-critique, revised-spec, narrative-brief]
---

# Data Visualization Skill

Create clear, ethical, and decision-ready visualizations from raw analysis.

## Triggers

- `design a chart for {analysis goal}` - Select chart form based on analytical objective.
- `review this visualization` - Audit clarity, integrity, and accessibility.
- `turn these metrics into a data story` - Build narrative from insight to action.
- `improve this dashboard chart` - Remove clutter and strengthen hierarchy.
- `validate chart accessibility` - Apply WCAG and color-blind-safe checks.

## Quick Reference

| Input | Output | Focus |
|---|---|---|
| Business question + dataset summary | Chart type recommendation + rationale | Form/function fit |
| Existing chart or spec | Critique + corrected chart spec | Integrity + clarity |
| KPI trend and context | Narrative outline + chart sequence | Storytelling |
| Dashboard screenshot/spec | Visual hierarchy improvements | Attention guidance |

## Process

### Phase 1: Clarify Analytical Intent

1. Identify the primary analytical objective:
   - Compare categories
   - Track change over time
   - Show part-to-whole
   - Reveal correlation/distribution
   - Retrieve exact values
2. Define audience and decision context:
   - Who will use this (executive, analyst, public)?
   - What action should follow from insight?
3. Establish the **Big Idea** (one sentence):
   - "The single thing this audience must understand is ..."

**Verification:** Objective, audience, and one-sentence Big Idea are explicit.

### Phase 2: Design for Truth and Cognitive Clarity

1. Apply minimalist data-ink rules:
   - Remove non-data-ink (3D effects, heavy gridlines, decorative backgrounds).
   - Keep only marks and labels that improve comprehension.
2. Build visual hierarchy deliberately:
   - Use muted baseline colors for context.
   - Use one accent color for key insight.
   - Prefer direct labels over legends when possible.
3. Enforce axis integrity:
   - Bar/column charts: y-axis starts at zero.
   - Any non-zero baseline must be justified and explicitly disclosed.
4. Choose chart type by objective (see references):
   - Categorical comparison -> horizontal bar chart
   - Continuous temporal trend -> line chart
   - Discrete period comparison -> column chart
   - Correlation/outliers -> scatter plot
   - Part-to-whole -> 100% stacked bar (pie only under strict limits)

**Verification:** Chart choice and axis decision are explained with explicit rationale.

### Phase 3: Accessibility and Storytelling Delivery

1. Run accessibility checks:
   - Text contrast: 4.5:1 (regular), 3:1 (large text)
   - Graphical objects/non-text contrast: >= 3:1
   - Do not rely on color alone; use shape/line style/text labels.
2. Add narrative context:
   - Title states conclusion (not just topic).
   - Add concise annotations at key events/outliers.
   - Convert insight to implication/action.
3. Apply progressive disclosure:
   - Headline insight first
   - Supporting evidence second
   - Deep methodology in appendix

4. Run deterministic validation scripts before final output:
   - `python scripts/validate_axis_integrity.py --spec chart_spec.json`
   - `python scripts/validate_accessibility.py --spec chart_spec.json`
   - For Chinese/CJK labels, run font rendering validation first:
     - `python scripts/validate_cjk_font_rendering.py --text "中文渲染检查：增长与客户结构"`
   - If validation fails, fix and rerun until both pass.

**Verification:** Output includes (a) insight headline, (b) evidence, (c) action/implication, and (d) passing script validation.

## Output Format

Return results in this structure:

1. **Recommended Visualization**
   - Chart type
   - Encoding choices (x, y, color, labels)
   - Why this is the right form
2. **Integrity Checks**
   - Axis baseline/scaling notes
   - Potential distortion risks
3. **Accessibility Checks**
   - Contrast compliance notes
   - Color-blind-safe encodings
4. **Narrative Layer**
   - Big Idea sentence
   - Executive title
   - 2-4 chart annotations
   - Recommended action

## Scripts

Use these scripts to enforce run-validate-fix-repeat checks.

| Script | Purpose | Typical Command |
|---|---|---|
| `scripts/validate_axis_integrity.py` | Validate bar/column baseline rules and detect high-risk truncation patterns | `python scripts/validate_axis_integrity.py --spec chart_spec.json` |
| `scripts/validate_accessibility.py` | Validate WCAG-related contrast targets and color-independent encoding metadata | `python scripts/validate_accessibility.py --spec chart_spec.json` |
| `scripts/validate_cjk_font_rendering.py` | Validate matplotlib can render Chinese/CJK labels without missing glyph fallback | `python scripts/validate_cjk_font_rendering.py --text "中文渲染检查：增长与客户结构"` |

### Script Exit Codes

- `0` = validation passed
- `1` = general runtime failure
- `2` = invalid arguments / malformed input
- `10` = validation failure (must fix before final output)

## Anti-Patterns

| Avoid | Why | Instead |
|---|---|---|
| Decorative chart junk (3D, shadows, busy backgrounds) | Increases cognitive load, hides signal | Maximize data-ink; simplify marks |
| Rainbow coloring for many categories | Destroys hierarchy and focus | Neutral palette + single accent |
| Truncated bar-chart baseline | Exaggerates differences | Start bars at zero |
| Legend-only labeling | Eye darting and slow decoding | Direct labels near marks |
| Pie chart with many similar slices | Poor angle/area comparison | Horizontal bar or 100% stacked bar |
| Descriptive-but-empty titles | Misses decision context | Insight-led, action-oriented title |
| Color-only encoding | Excludes color-blind users | Add shapes, patterns, text labels |

## Verification Checklist

- [ ] Chart type matches analytical objective.
- [ ] Bar/column charts use zero baseline (or documented exception).
- [ ] Non-data-ink removed; visual hierarchy is intentional.
- [ ] Accent color used only for key insight.
- [ ] Accessibility checks documented (contrast + color-independence).
- [ ] Title states insight; annotations explain key events.
- [ ] Output ends with actionable implication.
- [ ] `python scripts/validate_axis_integrity.py --spec chart_spec.json` passes.
- [ ] `python scripts/validate_accessibility.py --spec chart_spec.json` passes.
- [ ] For Chinese/CJK charts, `python scripts/validate_cjk_font_rendering.py --text "中文渲染检查"` passes.

## References

- [Visualization Principles](references/visualization-principles.md) - Data-ink, hierarchy, axes, chart selection.
- [Accessibility Checklist](references/accessibility-checklist.md) - WCAG and color-blind-safe guidance.
- [Storytelling Framework](references/storytelling-framework.md) - Big Idea, so-what, narrative arc.
- [Chart Selection Matrix](assets/templates/chart-selection-matrix.md) - Objective-to-chart quick selector.

## Extension Points

1. Add domain presets (finance, product analytics, operations, public policy).
2. Add Python/R plotting snippets mapped to each chart pattern.
3. Add accessibility auto-check scripts for contrast and alt-text completeness.
4. Add dashboard review rubric for executive, analyst, and public audiences.
