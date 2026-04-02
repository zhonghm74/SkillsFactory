#!/usr/bin/env python3
"""Validate executive report has BLUF and Minto-like sections."""

import argparse
import sys
from pathlib import Path

REQUIRED_HEADERS = [
    "# Executive Assertion",
    "## Supporting Arguments",
    "## Evidence Summary",
    "## Recommended Actions",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate business analysis report structure")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    if not args.report.exists():
        print(f"Report not found: {args.report}", file=sys.stderr)
        sys.exit(3)

    content = args.report.read_text(encoding="utf-8")

    missing = [h for h in REQUIRED_HEADERS if h not in content]
    if missing:
        print("Report validation failed. Missing sections:", file=sys.stderr)
        for h in missing:
            print(f"- {h}", file=sys.stderr)
        sys.exit(10)

    # Owner/timeline minimal check
    owner_ok = "Owner:" in content or "owner:" in content
    timeline_ok = "Timeline:" in content or "timeline:" in content
    if not (owner_ok and timeline_ok):
        print("Report validation failed. Recommended Actions must include Owner and Timeline.", file=sys.stderr)
        sys.exit(10)

    print("Report validation passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
