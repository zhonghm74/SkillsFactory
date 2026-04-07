#!/usr/bin/env python3
"""Build a minimal driver tree artifact from JSON input."""

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


def build_driver_tree(input_path: Path, output_path: Path) -> Result:
    if not input_path.exists():
        return Result(False, f"Input not found: {input_path}", errors=["file_not_found"])

    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return Result(False, f"Invalid JSON input: {exc}", errors=["invalid_json"])
    except Exception as exc:
        return Result(False, f"Failed to read input: {exc}", errors=["read_error"])

    objective = payload.get("objective")
    drivers = payload.get("drivers", [])
    if not objective or not isinstance(drivers, list):
        return Result(False, "Input must include objective and drivers[]", errors=["invalid_payload"])

    output = {
        "objective": objective,
        "drivers": drivers,
        "meta": {
            "generated_by": "build_driver_tree.py",
            "status": "draft",
        },
    }

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    except Exception as exc:
        return Result(False, f"Failed to write output: {exc}", errors=["write_error"])

    return Result(True, f"Driver tree written: {output_path}", data=output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build driver tree JSON")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = build_driver_tree(args.input, args.output)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        stream = sys.stdout if result.success else sys.stderr
        print(result.message, file=stream)
        for err in result.errors:
            print(f"  - {err}", file=sys.stderr)

    if result.success:
        sys.exit(0)
    if "file_not_found" in result.errors:
        sys.exit(3)
    if "invalid_payload" in result.errors or "invalid_json" in result.errors:
        sys.exit(10)
    sys.exit(1)


if __name__ == "__main__":
    main()
