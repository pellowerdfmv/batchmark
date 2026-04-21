"""Console reporter for regression detection results."""

from __future__ import annotations

from typing import List

from batchmark.regressor import RegressionResult, any_regression

_COL_W = 12


def _fmt(value: float | None, decimals: int = 2, suffix: str = "") -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}{suffix}"


def _flag(r: RegressionResult) -> str:
    return "REGRESSED" if r.is_regression else "ok"


def format_regression_header() -> str:
    cols = ["size", "baseline_ms", "current_ms", "delta_ms", "delta_pct", "status"]
    return "  ".join(c.ljust(_COL_W) for c in cols)


def format_regression_row(r: RegressionResult) -> str:
    cols = [
        str(r.size).ljust(_COL_W),
        _fmt(r.baseline_ms).ljust(_COL_W),
        _fmt(r.current_ms).ljust(_COL_W),
        _fmt(r.delta_ms, suffix="ms").ljust(_COL_W),
        _fmt(r.delta_pct, suffix="%").ljust(_COL_W),
        _flag(r).ljust(_COL_W),
    ]
    return "  ".join(cols)


def format_regression_summary(results: List[RegressionResult]) -> str:
    total = len(results)
    flagged = sum(1 for r in results if r.is_regression)
    verdict = "REGRESSIONS DETECTED" if flagged else "no regressions"
    return f"sizes checked: {total}  regressions: {flagged}  verdict: {verdict}"


def print_regression_report(
    results: List[RegressionResult],
    threshold_pct: float = 10.0,
) -> None:
    print(f"Regression report  (threshold: {threshold_pct:.1f}%)")
    print(format_regression_header())
    print("-" * (_COL_W * 6 + 10))
    for r in results:
        print(format_regression_row(r))
    print()
    print(format_regression_summary(results))
