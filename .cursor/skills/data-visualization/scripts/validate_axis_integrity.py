#!/usr/bin/env python3
"""
validate_axis_integrity.py - Validate chart-axis integrity and baseline disclosure.

Checks:
- Bar/column charts must use y-axis baseline 0 by default
- Any non-zero baseline requires explicit justification and disclosure

Usage:
    python validate_axis_integrity.py <spec.json>
    python validate_axis_integrity.py <spec.json> --json

Exit Codes:
    0  - Success
    1  - General failure
    2  - Invalid arguments
    3  - File not found
    10 - Validation failure
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass
class Result:
    success: bool
    message: str
    data: dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat(),
        }


def _load_spec(path: Path) -> Result:
    if not path.exists():
        return Result(False, f"Spec file not found: {path}", errors=["file_not_found"])
    try:
        return Result(True, "spec_loaded", data=json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as exc:
        return Result(False, f"Invalid JSON: {exc}", errors=["invalid_json"])


def validate_axis_integrity(spec: dict) -> Result:
    errors: List[str] = []
    warnings: List[str] = []

    chart_type = str(spec.get("chart_type", "")).lower()
    axis = spec.get("axis", {}) if isinstance(spec, dict) else {}
    if not isinstance(axis, dict):
        return Result(False, "axis must be an object", errors=["invalid_axis_type"])

    y_min = axis.get("y_min")
    baseline_disclosure = str(axis.get("baseline_disclosure", "")).strip()
    nonzero_justification = str(axis.get("nonzero_baseline_justification", "")).strip()

    length_encoded_types = {"bar", "column", "horizontal-bar", "vertical-bar"}
    if chart_type in length_encoded_types:
        if y_min is None:
            errors.append("axis.y_min is required for bar/column charts")
        else:
            try:
                y_min_num = float(y_min)
            except (TypeError, ValueError):
                errors.append("axis.y_min must be numeric")
                y_min_num = None

            if y_min_num is not None and y_min_num != 0.0:
                if not nonzero_justification:
                    errors.append("non-zero y_min requires nonzero_baseline_justification")
                if not baseline_disclosure:
                    errors.append("non-zero y_min requires baseline_disclosure text")
    else:
        # For line/scatter, non-zero baselines may be acceptable but should be disclosed
        if y_min not in (None, 0, 0.0, "0") and not baseline_disclosure:
            warnings.append("non-zero y_min used without baseline disclosure")

    if errors:
        return Result(False, "Axis integrity validation failed", errors=errors, warnings=warnings)

    return Result(True, "Axis integrity validation passed", warnings=warnings)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate axis integrity for chart spec")
    parser.add_argument("spec", type=Path, help="Path to JSON spec")
    parser.add_argument("--json", action="store_true", help="Output JSON result")
    args = parser.parse_args()

    load = _load_spec(args.spec)
    if not load.success:
        if args.json:
            print(json.dumps(load.to_dict(), indent=2))
        else:
            print(load.message, file=sys.stderr)
        sys.exit(3 if "file_not_found" in load.errors else 1)

    result = validate_axis_integrity(load.data)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        stream = sys.stdout if result.success else sys.stderr
        print(result.message, file=stream)
        for err in result.errors:
            print(f"  - {err}", file=sys.stderr)
        for warn in result.warnings:
            print(f"  - warning: {warn}", file=sys.stderr)

    sys.exit(0 if result.success else 10)


if __name__ == "__main__":
    main()
