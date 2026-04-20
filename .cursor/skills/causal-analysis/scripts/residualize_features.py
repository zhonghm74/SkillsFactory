#!/usr/bin/env python3
"""Residualize selected variables against confounders (FWL-style helper)."""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd


@dataclass
class Result:
    success: bool
    message: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)


def _ols_fit_predict_residual(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """OLS with intercept; return residuals."""
    x_design = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(x_design, y, rcond=None)
    y_hat = x_design @ beta
    return y - y_hat


def run_residualization(
    input_csv: Path,
    confounders: List[str],
    residualize_cols: List[str],
    outcome_col: str,
    output_csv: Path,
    diagnostics_json: Path,
) -> Result:
    if not input_csv.exists():
        return Result(False, f"Input CSV not found: {input_csv}", errors=["input_not_found"])

    try:
        df = pd.read_csv(input_csv)
    except Exception as exc:
        return Result(False, f"Failed to read input CSV: {exc}", errors=["input_read_error"])

    required = set(confounders + residualize_cols + [outcome_col])
    missing = [c for c in required if c not in df.columns]
    if missing:
        return Result(False, f"Missing required columns: {missing}", errors=["missing_columns"])

    cols_for_model = list(required)
    model_df = df[cols_for_model].copy()
    model_df = model_df.apply(pd.to_numeric, errors="coerce")
    valid_mask = model_df.notna().all(axis=1)
    kept = int(valid_mask.sum())
    dropped = int((~valid_mask).sum())

    if kept < 20:
        return Result(
            False,
            "Too few valid rows after numeric coercion and NA filtering.",
            errors=["insufficient_rows"],
        )

    x = model_df.loc[valid_mask, confounders].to_numpy(dtype=float)
    out_df = df.copy()

    residual_cols = []
    variance_ratio = {}

    for col in residualize_cols + [outcome_col]:
        y = model_df.loc[valid_mask, col].to_numpy(dtype=float)
        resid = _ols_fit_predict_residual(y, x)
        resid_col = f"{col}_resid"
        out_df[resid_col] = np.nan
        out_df.loc[valid_mask, resid_col] = resid
        residual_cols.append(resid_col)

        var_y = float(np.var(y))
        var_r = float(np.var(resid))
        variance_ratio[col] = var_r / var_y if var_y > 0 else None

    try:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        diagnostics_json.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(output_csv, index=False)
        diagnostics_json.write_text(
            json.dumps(
                {
                    "confounders": confounders,
                    "residualized_columns": residualize_cols,
                    "outcome_column": outcome_col,
                    "output_residual_columns": residual_cols,
                    "rows_total": int(len(df)),
                    "rows_kept_for_fit": kept,
                    "rows_dropped_for_fit": dropped,
                    "residual_variance_ratio": variance_ratio,
                    "note": "ratio closer to 0 means stronger variance explained by confounders",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except Exception as exc:
        return Result(False, f"Failed to write outputs: {exc}", errors=["write_error"])

    warnings = []
    if dropped > 0:
        warnings.append(f"dropped_rows_for_fit:{dropped}")

    return Result(
        True,
        f"Residualization finished: {output_csv}",
        warnings=warnings,
        data={
            "rows_total": int(len(df)),
            "rows_kept_for_fit": kept,
            "rows_dropped_for_fit": dropped,
            "residual_columns": residual_cols,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Residualize variables against confounders")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--confounders", required=True, type=str)
    parser.add_argument("--residualize-cols", required=True, type=str)
    parser.add_argument("--outcome-col", required=True, type=str)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--diagnostics", required=True, type=Path)
    args = parser.parse_args()

    confounders = [c.strip() for c in args.confounders.split(",") if c.strip()]
    residualize_cols = [c.strip() for c in args.residualize_cols.split(",") if c.strip()]

    result = run_residualization(
        input_csv=args.input_csv,
        confounders=confounders,
        residualize_cols=residualize_cols,
        outcome_col=args.outcome_col,
        output_csv=args.output,
        diagnostics_json=args.diagnostics,
    )

    stream = sys.stdout if result.success else sys.stderr
    print(result.message, file=stream)
    for warn in result.warnings:
        print(f"  - warning: {warn}", file=sys.stderr)
    for err in result.errors:
        print(f"  - {err}", file=sys.stderr)

    if result.success:
        sys.exit(0)
    if "input_not_found" in result.errors:
        sys.exit(3)
    if any(code in result.errors for code in ["missing_columns", "insufficient_rows"]):
        sys.exit(10)
    sys.exit(1)


if __name__ == "__main__":
    main()

