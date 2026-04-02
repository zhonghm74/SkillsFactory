#!/usr/bin/env python3
"""Build a minimal driver tree artifact from JSON input."""

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build driver tree JSON")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        sys.exit(3)

    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON input: {exc}", file=sys.stderr)
        sys.exit(10)

    objective = payload.get("objective")
    drivers = payload.get("drivers", [])
    if not objective or not isinstance(drivers, list):
        print("Input must include objective and drivers[]", file=sys.stderr)
        sys.exit(10)

    output = {
        "objective": objective,
        "drivers": drivers,
        "meta": {
            "generated_by": "build_driver_tree.py",
            "status": "draft"
        }
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Driver tree written: {args.output}")
    sys.exit(0)


if __name__ == "__main__":
    main()
