#!/usr/bin/env python3
"""Render a 7-step RCA markdown summary from incident JSON."""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

STEPS = [
    "Reproduction",
    "Data Verification",
    "Helicopter View",
    "Contextual Synthesis",
    "Slicing & Dicing",
    "Metric Decomposition",
    "Synthesis & Conclusion",
]


@dataclass
class Result:
    success: bool
    message: str
    errors: List[str] = field(default_factory=list)


def generate_rca(incident: Path, output: Path) -> Result:
    if not incident.exists():
        return Result(False, f"Incident input not found: {incident}", errors=["file_not_found"])

    try:
        data = json.loads(incident.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return Result(False, f"Invalid incident JSON: {exc}", errors=["invalid_json"])

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

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return Result(True, f"RCA summary written: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RCA checklist output")
    parser.add_argument("incident", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    result = generate_rca(args.incident, args.output)
    stream = sys.stdout if result.success else sys.stderr
    print(result.message, file=stream)

    if result.success:
        sys.exit(0)
    if "file_not_found" in result.errors:
        sys.exit(3)
    if "invalid_json" in result.errors:
        sys.exit(10)
    sys.exit(1)


if __name__ == "__main__":
    main()
