#!/usr/bin/env python3
"""Validate executive report has BLUF and Minto-like sections."""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

REQUIRED_HEADERS = [
    "# Executive Assertion",
    "## Supporting Arguments",
    "## Evidence Summary",
    "## Recommended Actions",
]


@dataclass
class Result:
    success: bool
    message: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def validate_report(path: Path) -> Result:
    try:
        if not path.exists():
            return Result(False, f"Report not found: {path}", errors=["report_not_found"])

        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return Result(False, f"Failed to read report: {exc}", errors=["report_read_error"])

    missing = [h for h in REQUIRED_HEADERS if h not in content]
    if missing:
        return Result(False, "Missing required report sections", errors=[f"missing:{h}" for h in missing])

    owner_ok = "Owner:" in content or "owner:" in content
    timeline_ok = "Timeline:" in content or "timeline:" in content
    if not (owner_ok and timeline_ok):
        return Result(
            False,
            "Recommended Actions must include Owner and Timeline",
            errors=["missing_owner_or_timeline"],
        )

    return Result(True, "Report validation passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate business analysis report structure")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    result = validate_report(args.report)
    stream = sys.stdout if result.success else sys.stderr
    print(result.message, file=stream)
    for err in result.errors:
        print(f"  - {err}", file=sys.stderr)
    for warn in result.warnings:
        print(f"  - warning: {warn}", file=sys.stderr)

    if result.success:
        sys.exit(0)
    if "report_not_found" in result.errors:
        sys.exit(3)
    sys.exit(10)


if __name__ == "__main__":
    main()
