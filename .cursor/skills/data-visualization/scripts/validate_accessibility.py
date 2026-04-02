#!/usr/bin/env python3
"""
validate_accessibility.py - Validate chart accessibility metadata and contrast values.

Checks:
- Required accessibility fields exist
- Contrast thresholds meet WCAG-inspired minima
- Color-independent encoding signals are present
- Alt text exists and includes an insight statement

Usage:
    python validate_accessibility.py <spec.json>
    python validate_accessibility.py <spec.json> --json

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


def validate_accessibility(spec: dict) -> Result:
    errors: List[str] = []
    warnings: List[str] = []

    acc = spec.get("accessibility", {}) if isinstance(spec, dict) else {}
    if not isinstance(acc, dict):
        return Result(False, "accessibility must be an object", errors=["invalid_accessibility_type"])

    # Required keys
    required = [
        "regular_text_contrast",
        "large_text_contrast",
        "graphical_contrast",
        "uses_color_independent_encoding",
        "alt_text",
    ]
    for key in required:
        if key not in acc:
            errors.append(f"missing accessibility.{key}")

    def _num(name: str, minimum: float):
        value = acc.get(name)
        if value is None:
            return
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            errors.append(f"{name} must be numeric")
            return
        if numeric < minimum:
            errors.append(f"{name}={numeric} below minimum {minimum}")

    _num("regular_text_contrast", 4.5)
    _num("large_text_contrast", 3.0)
    _num("graphical_contrast", 3.0)

    color_independent = acc.get("uses_color_independent_encoding")
    if isinstance(color_independent, bool):
        if not color_independent:
            errors.append("uses_color_independent_encoding must be true")
    elif color_independent is not None:
        errors.append("uses_color_independent_encoding must be boolean")

    alt_text = acc.get("alt_text", "")
    if isinstance(alt_text, str):
        if len(alt_text.strip()) < 20:
            errors.append("alt_text too short")
        # Soft heuristic: should imply insight, not only geometry
        insight_markers = ["increase", "decrease", "higher", "lower", "trend", "peak", "drop", "because"]
        if not any(m in alt_text.lower() for m in insight_markers):
            warnings.append("alt_text may describe geometry but not insight")
    elif alt_text is not None:
        errors.append("alt_text must be string")

    if errors:
        return Result(False, "Accessibility validation failed", errors=errors, warnings=warnings)

    return Result(True, "Accessibility validation passed", warnings=warnings)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate accessibility metadata for chart spec")
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

    result = validate_accessibility(load.data)

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
