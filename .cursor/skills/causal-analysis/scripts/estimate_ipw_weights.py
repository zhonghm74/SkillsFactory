#!/usr/bin/env python3
"""Estimate propensity score and stabilized IPW weights with balance diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class Result:
    success: bool
    message: str
    errors: List[str] = field(default_factory=list)
    data: Dict = field(default_factory=dict)


def _weighted_mean(x: np.ndarray, w: np.ndarray) -> float:
    return float(np.sum(w * x) / np.sum(w))


def _weighted_var(x: np.ndarray, w: np.ndarray) -> float:
    mu = _weighted_mean(x, w)
    return float(np.sum(w * (x - mu) ** 2) / np.sum(w))


def _smd(
    x_t: np.ndarray,
    x_c: np.ndarray,
    w_t: np.ndarray | None = None,
    w_c: np.ndarray | None = None,
) -> float:
    if w_t is None:
        mu_t = float(np.mean(x_t))
        var_t = float(np.var(x_t))
    else:
        mu_t = _weighted_mean(x_t, w_t)
        var_t = _weighted_var(x_t, w_t)

    if w_c is None:
        mu_c = float(np.mean(x_c))
        var_c = float(np.var(x_c))
    else:
        mu_c = _weighted_mean(x_c, w_c)
        var_c = _weighted_var(x_c, w_c)

    pooled = np.sqrt((var_t + var_c) / 2.0)
    if pooled == 0:
        return 0.0
    return float((mu_t - mu_c) / pooled)


def _build_preprocessor(df: pd.DataFrame, feature_cols: List[str]) -> ColumnTransformer:
    num_cols = [c for c in feature_cols if pd.api.types.is_numeric_dtype(df[c])]
    cat_cols = [c for c in feature_cols if c not in num_cols]

    num_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    cat_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", num_pipe, num_cols),
            ("cat", cat_pipe, cat_cols),
        ]
    )


def estimate_ipw(
    input_csv: Path,
    treatment_col: str,
    treated_value: str,
    output_csv: Path,
    diagnostics_json: Path,
) -> Result:
    if not input_csv.exists():
        return Result(False, f"Input file not found: {input_csv}", errors=["file_not_found"])

    try:
        df = pd.read_csv(input_csv)
    except Exception as exc:
        return Result(False, f"Failed to read csv: {exc}", errors=["csv_read_error"])

    if treatment_col not in df.columns:
        return Result(False, f"Treatment column missing: {treatment_col}", errors=["missing_treatment_col"])

    t = (df[treatment_col].astype(str) == str(treated_value)).astype(int)
    if t.nunique() < 2:
        return Result(False, "Treatment has only one class", errors=["single_class_treatment"])

    feature_cols = [c for c in df.columns if c != treatment_col]
    if not feature_cols:
        return Result(False, "No covariates found", errors=["no_covariates"])

    try:
        pre = _build_preprocessor(df, feature_cols)
        model = Pipeline(
            steps=[
                ("pre", pre),
                ("clf", LogisticRegression(max_iter=2000, solver="lbfgs")),
            ]
        )
        model.fit(df[feature_cols], t)
        ps = model.predict_proba(df[feature_cols])[:, 1]
    except Exception as exc:
        return Result(False, f"Propensity model failed: {exc}", errors=["propensity_model_failed"])

    eps = 1e-6
    ps = np.clip(ps, eps, 1 - eps)
    p_treated = float(t.mean())
    weights = np.where(t == 1, p_treated / ps, (1 - p_treated) / (1 - ps))

    out = df.copy()
    out["_treatment_binary"] = t
    out["_propensity_score"] = ps
    out["_ipw_stabilized"] = weights

    # balance diagnostics for numeric columns only
    num_cols = [c for c in feature_cols if pd.api.types.is_numeric_dtype(df[c])]
    smd_rows = []
    treat_mask = t == 1
    ctrl_mask = t == 0
    for c in num_cols:
        x = pd.to_numeric(df[c], errors="coerce")
        valid = x.notna()
        tm = treat_mask & valid
        cm = ctrl_mask & valid
        if tm.sum() < 2 or cm.sum() < 2:
            continue
        x_t = x.loc[tm].to_numpy()
        x_c = x.loc[cm].to_numpy()
        w_t = weights[tm.to_numpy()]
        w_c = weights[cm.to_numpy()]
        smd_raw = _smd(x_t, x_c)
        smd_w = _smd(x_t, x_c, w_t=w_t, w_c=w_c)
        smd_rows.append(
            {
                "feature": c,
                "smd_before": smd_raw,
                "smd_after": smd_w,
                "abs_before": abs(smd_raw),
                "abs_after": abs(smd_w),
            }
        )

    diag = {
        "n_rows": int(len(df)),
        "treated_rate": p_treated,
        "weight_summary": {
            "min": float(np.min(weights)),
            "p01": float(np.quantile(weights, 0.01)),
            "p50": float(np.quantile(weights, 0.50)),
            "p99": float(np.quantile(weights, 0.99)),
            "max": float(np.max(weights)),
        },
        "balance": smd_rows,
        "threshold_note": "abs(SMD) < 0.1 is commonly considered acceptable balance.",
    }

    try:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        diagnostics_json.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(output_csv, index=False)
        diagnostics_json.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    except Exception as exc:
        return Result(False, f"Failed writing outputs: {exc}", errors=["write_error"])

    return Result(
        True,
        f"IPW estimation completed. weighted={output_csv}, diagnostics={diagnostics_json}",
        data={"rows": int(len(df)), "num_balance_features": len(smd_rows)},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate stabilized IPW weights from observational data.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--treatment-col", required=True)
    parser.add_argument("--treated-value", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--diagnostics", required=True, type=Path)
    args = parser.parse_args()

    result = estimate_ipw(
        input_csv=args.input_csv,
        treatment_col=args.treatment_col,
        treated_value=args.treated_value,
        output_csv=args.output,
        diagnostics_json=args.diagnostics,
    )

    stream = sys.stdout if result.success else sys.stderr
    print(result.message, file=stream)
    if result.errors:
        for err in result.errors:
            print(f"  - {err}", file=sys.stderr)

    if result.success:
        sys.exit(0)
    if "file_not_found" in result.errors:
        sys.exit(3)
    if any(e in result.errors for e in ["missing_treatment_col", "single_class_treatment", "no_covariates"]):
        sys.exit(10)
    sys.exit(1)


if __name__ == "__main__":
    main()
