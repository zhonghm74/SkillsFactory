#!/usr/bin/env python3
"""validate_cjk_font_rendering.py - Validate matplotlib CJK font rendering.

Usage:
    python validate_cjk_font_rendering.py --text "中文标题"

Exit Codes:
    0  - Success
    1  - General failure
    2  - Invalid arguments
    10 - Validation failure
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams


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


def pick_font() -> Result:
    candidates = [
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            font_manager.fontManager.addfont(path)
            return Result(
                True,
                "font_selected",
                data={"font_name": font_manager.FontProperties(fname=path).get_name(), "font_path": path},
            )
    return Result(
        False,
        "No CJK font found (expected WenQuanYi or Droid fallback).",
        errors=["font_not_found"],
    )


def validate_cjk(text: str) -> Result:
    font_result = pick_font()
    if not font_result.success:
        return font_result
    font_name = font_result.data["font_name"]

    rcParams['font.family'] = font_name
    rcParams['font.sans-serif'] = [font_name, 'WenQuanYi Micro Hei', 'Droid Sans Fallback']
    rcParams['axes.unicode_minus'] = False

    warnings.filterwarnings('error', message='.*Glyph.*missing from font.*', category=UserWarning)
    try:
        fig, ax = plt.subplots(figsize=(4, 2), dpi=120)
        ax.set_title(text)
        ax.set_xlabel('月份')
        ax.set_ylabel('收入')
        ax.plot([1, 2, 3], [1, 2, 1])
        fig.canvas.draw()
        plt.close(fig)
    except UserWarning as exc:
        return Result(
            False,
            "CJK font rendering validation failed",
            data={"font_name": font_name},
            errors=[f"missing_glyph: {exc}"],
        )
    except Exception as exc:  # pragma: no cover - defensive
        return Result(
            False,
            "CJK font rendering runtime failure",
            data={"font_name": font_name},
            errors=[f"runtime_error: {exc}"],
        )
    return Result(
        True,
        "CJK font rendering validation passed",
        data={"font_name": font_name},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate CJK rendering in matplotlib')
    parser.add_argument('--text', default='中文渲染检查：增长与客户结构')
    parser.add_argument('--json', action='store_true', help='Output JSON result')
    args = parser.parse_args()

    result = validate_cjk(args.text)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        stream = sys.stdout if result.success else sys.stderr
        print(result.message, file=stream)
        if result.data.get("font_name"):
            print(f"font={result.data['font_name']}", file=stream)
        for err in result.errors:
            print(f"  - {err}", file=sys.stderr)
    if result.success:
        sys.exit(0)
    if "font_not_found" in result.errors:
        sys.exit(10)
    if any(err.startswith("missing_glyph:") for err in result.errors):
        sys.exit(10)
    sys.exit(1)


if __name__ == '__main__':
    main()
