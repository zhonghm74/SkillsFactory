# Accessibility Checklist for Data Visualization

## Contrast Requirements (WCAG-aligned)

| Element | Minimum Contrast |
|---|---|
| Regular text | 4.5:1 |
| Large text | 3:1 |
| Graphical objects/non-text | 3:1 |

Notes:
- Do not round up borderline ratios.
- Prefer comfortable high contrast (e.g., dark gray on off-white) over harsh extremes.

## Color-Blind-Safe Practices

- Never encode meaning by hue alone.
- Reinforce with shape, pattern, marker type, or line style.
- Avoid relying on red/green alone for positive/negative distinctions.

## Labeling and Assistive Context

- Prefer direct labels next to marks where possible.
- Keep axis/category text horizontal and readable.
- Provide alt text that states insight, not just chart geometry.

Good alt text example:
- "Monthly conversion rose from 3.1% to 4.0% after onboarding redesign, with strongest gains in mobile traffic."

## Accessibility QA Pass

- [ ] All core text meets required contrast.
- [ ] Data marks are distinguishable at 3:1 or higher.
- [ ] Color is not the only channel for meaning.
- [ ] Labels are readable without rotation where possible.
- [ ] Alt text captures the analytical takeaway.
