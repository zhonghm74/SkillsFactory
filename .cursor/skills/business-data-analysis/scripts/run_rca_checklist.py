#!/usr/bin/env python3
"""Render a 7-step RCA markdown summary from incident JSON."""

import argparse
import json
import sys
from pathlib import Path

STEPS = [
    "Reproduction",
    "Data Verification",
    "Helicopter View",
    "Contextual Synthesis",
    "Slicing & Dicing",
    "Metric Decomposition",
    "Synthesis & Conclusion",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RCA checklist output")
    parser.add_argument("incident", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.incident.exists():
        print(f"Incident input not found: {args.incident}", file=sys.stderr)
        sys.exit(3)

    try:
        data = json.loads(args.incident.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid incident JSON: {exc}", file=sys.stderr)
        sys.exit(10)

    metric = data.get("metric", "unknown_metric")
    anomaly = data.get("anomaly", "unspecified anomaly")

    lines = [
        f"# RCA Summary: {metric}",
        "",
        f"Anomaly: {anomaly}",
        "",
        "## 7-Step Checklist",
    ]
    for idx, step in enumerate(STEPS, start=1):
        lines.append(f"{idx}. [ ] {step}: TODO findings")

    lines.extend([
        "",
        "## Preliminary Suspects",
        "- TODO",
        "",
        "## Validation Plan",
        "- TODO",
    ])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"RCA summary written: {args.output}")
    sys.exit(0)


if __name__ == "__main__":
    main()
