# Visualization Principles

## Table of Contents

- [Minimalism and Data-Ink](#minimalism-and-data-ink)
- [Visual Hierarchy and Color](#visual-hierarchy-and-color)
- [Axis Integrity](#axis-integrity)
- [Chart-Type Guidance](#chart-type-guidance)
- [Pie-Chart Constraints](#pie-chart-constraints)

## Minimalism and Data-Ink

- Keep data representation primary; remove non-data-ink.
- Remove or soften heavy gridlines unless they support reading values.
- Avoid decorative effects (3D, shadows, ornamental backgrounds).
- Prefer direct labels over redundant axes/legends when feasible.

## Visual Hierarchy and Color

- Use pre-attentive cues intentionally: size, contrast, position, and color.
- Set a neutral baseline palette for context.
- Reserve one accent color for the key message.
- If everything is highlighted, nothing is highlighted.

## Axis Integrity

- Bar/column charts encode value by length; baseline must start at zero.
- Any baseline truncation must be explicit, justified, and risk-assessed.
- For line charts, truncation can improve detail but may exaggerate perception;
  default to zero first, then justify deviations with context.

## Chart-Type Guidance

| Objective | Preferred Chart | Why |
|---|---|---|
| Compare categories | Horizontal bar | Best for magnitude comparison and long labels |
| Continuous time trend | Line | Emphasizes slope/pattern over time |
| Discrete period comparison | Column | Compares separated periods clearly |
| Correlation/distribution | Scatter | Reveals clusters/outliers/relationships |
| Part-to-whole | 100% stacked bar / treemap | Better precision than many-slice pie |
| Exact lookup | Data table | Best for precise values |

## Pie-Chart Constraints

Only consider pie charts when all conditions hold:

1. Slices are mutually exclusive and sum to 100%.
2. Category count is very small (ideally <=3, never >5).
3. Differences are large and obvious.

Otherwise prefer bar-based alternatives.
