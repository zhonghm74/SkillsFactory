#!/usr/bin/env python3
"""Build uplift decile table and AUUC/Qini-like diagnostics."""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import pandas as pd


@dataclass
class Result:
    success: bool
    message: str
    errors: List[str] = field(default_factory=list)


def _decile_index(series: pd.Series, n_bins: int = 10) -> pd.Series:
    # Rank-first to avoid qcut failure on many ties.
    ranked = series.rank(method="first")
    return pd.qcut(ranked, q=n_bins, labels=False, duplicates="drop")


def build_uplift_eval(
    df: pd.DataFrame,
    treatment_col: str,
    treated_value: str,
    outcome_col: str,
    score_col: str,
) -> tuple[pd.DataFrame, dict]:
    treated = (df[treatment_col].astype(str) == str(treated_value)).astype(int)
    outcome = pd.to_numeric(df[outcome_col], errors="coerce").fillna(0.0)
    score = pd.to_numeric(df[score_col], errors="coerce")

    work = pd.DataFrame(
        {"treated": treated, "outcome": outcome, "score": score}
    ).dropna(subset=["score"])
    if work.empty:
        raise ValueError("No valid rows after score coercion.")

    work = work.sort_values("score", ascending=False).reset_index(drop=True)
    work["decile"] = _decile_index(work["score"], 10)
    work["decile"] = 10 - work["decile"].astype(int)  # 10 => top uplift bucket

    rows = []
    for decile, g in work.groupby("decile", sort=True):
        n_t = int((g["treated"] == 1).sum())
        n_c = int((g["treated"] == 0).sum())
        y_t = float(g.loc[g["treated"] == 1, "outcome"].sum())
        y_c = float(g.loc[g["treated"] == 0, "outcome"].sum())
        rate_t = y_t / n_t if n_t > 0 else 0.0
        rate_c = y_c / n_c if n_c > 0 else 0.0
        uplift = rate_t - rate_c
        rows.append(
            {
                "decile": int(decile),
                "n": int(len(g)),
                "n_treated": n_t,
                "n_control": n_c,
                "outcome_rate_treated": rate_t,
                "outcome_rate_control": rate_c,
                "uplift_rate": uplift,
            }
        )

    deciles = pd.DataFrame(rows).sort_values("decile", ascending=False).reset_index(drop=True)
    deciles["cum_n"] = deciles["n"].cumsum()
    deciles["cum_uplift"] = deciles["uplift_rate"].cumsum()

    # AUUC-like area from cumulative uplift curve (simple trapezoidal approximation on deciles).
    x = deciles.index.to_series().astype(float)
    y = deciles["cum_uplift"]
    auuc = float((y.shift(fill_value=0) + y).sum() / 2.0)

    # Qini-like score: gain over random baseline approximated by final uplift trend.
    baseline = y.iloc[-1] * (x / max(float(x.iloc[-1]), 1.0))
    qini_like = float((y - baseline).sum())

    metrics = {
        "rows_used": int(len(work)),
        "auuc_like": auuc,
        "qini_like": qini_like,
        "top_decile_uplift_rate": float(deciles.iloc[0]["uplift_rate"]) if not deciles.empty else 0.0,
        "bottom_decile_uplift_rate": float(deciles.iloc[-1]["uplift_rate"]) if not deciles.empty else 0.0,
    }
    return deciles, metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Build uplift evaluation artifacts")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--treatment-col", required=True)
    parser.add_argument("--treated-value", default="1")
    parser.add_argument("--outcome-col", required=True)
    parser.add_argument("--score-col", required=True)
    parser.add_argument("--decile-output", required=True, type=Path)
    parser.add_argument("--metrics-output", required=True, type=Path)
    args = parser.parse_args()

    if not args.input_csv.exists():
        print(f"Input not found: {args.input_csv}", file=sys.stderr)
        sys.exit(3)

    try:
        df = pd.read_csv(args.input_csv)
        deciles, metrics = build_uplift_eval(
            df=df,
            treatment_col=args.treatment_col,
            treated_value=args.treated_value,
            outcome_col=args.outcome_col,
            score_col=args.score_col,
        )
        args.decile_output.parent.mkdir(parents=True, exist_ok=True)
        args.metrics_output.parent.mkdir(parents=True, exist_ok=True)
        deciles.to_csv(args.decile_output, index=False)
        args.metrics_output.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    except ValueError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        sys.exit(10)
    except Exception as exc:
        print(f"Failed to build uplift evaluation: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Deciles written: {args.decile_output}")
    print(f"Metrics written: {args.metrics_output}")
    sys.exit(0)


if __name__ == "__main__":
    main()
