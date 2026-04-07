#!/usr/bin/env python3
"""
Validate and sanitize literal escape sequences in plot annotations.

This script prevents text bugs where raw "\\n" appears in rendered figures
instead of real line breaks.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


LITERAL_ESCAPE_PATTERN = re.compile(r"\\[nrt]")


def normalize_literal_escapes(text: str) -> str:
    """Convert common literal escapes to real control characters."""
    normalized = text.replace(r"\r\n", "\n")
    normalized = normalized.replace(r"\n", "\n")
    normalized = normalized.replace(r"\r", "\r")
    normalized = normalized.replace(r"\t", "\t")
    return normalized


def detect_literal_escapes(text: str) -> list[str]:
    """Return all literal escape tokens still present in text."""
    return LITERAL_ESCAPE_PATTERN.findall(text)


def assert_no_literal_escapes(text: str, field_name: str = "text") -> None:
    """Raise when literal escape tokens remain after sanitization."""
    found = detect_literal_escapes(text)
    if found:
        uniq = ", ".join(sorted(set(found)))
        raise ValueError(f"{field_name} still contains literal escape tokens: {uniq}")


def sanitize_and_validate(text: str, field_name: str = "text") -> str:
    """Sanitize text and fail fast when bad escapes still remain."""
    normalized = normalize_literal_escapes(text)
    assert_no_literal_escapes(normalized, field_name=field_name)
    return normalized


def _read_input(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.input_file is not None:
        return Path(args.input_file).read_text(encoding="utf-8")
    raise ValueError("Provide either --text or --input-file")


def _write_output(output: str, args: argparse.Namespace) -> None:
    if args.output_file:
        Path(args.output_file).write_text(output, encoding="utf-8")
    elif args.inplace and args.input_file:
        Path(args.input_file).write_text(output, encoding="utf-8")
    else:
        print(output)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sanitize and validate literal escape sequences in plot text."
    )
    parser.add_argument("--text", help="Inline text to validate.")
    parser.add_argument("--input-file", help="Path to text file to validate.")
    parser.add_argument("--output-file", help="Optional output path for sanitized text.")
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite --input-file with sanitized text.",
    )
    parser.add_argument(
        "--field-name",
        default="text",
        help="Label used in error messages.",
    )
    parser.add_argument(
        "--sanitize",
        action="store_true",
        help="Emit sanitized text instead of only validating.",
    )
    args = parser.parse_args()

    try:
        raw = _read_input(args)
        if args.sanitize:
            sanitized = sanitize_and_validate(raw, field_name=args.field_name)
            _write_output(sanitized, args)
            print("✓ text sanitization and validation passed")
        else:
            assert_no_literal_escapes(raw, field_name=args.field_name)
            print("✓ text escape validation passed")
        return 0
    except Exception as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
