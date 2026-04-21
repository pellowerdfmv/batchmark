"""Regression detection: flag sizes where mean duration has grown beyond a threshold."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.aggregator import AggregatedResult


@dataclass
class RegressionResult:
    size: int
    baseline_ms: Optional[float]
    current_ms: Optional[float]
    delta_ms: Optional[float]
    delta_pct: Optional[float]
    is_regression: bool


def _pct(current: float, baseline: float) -> float:
    if baseline == 0.0:
        return 0.0
    return (current - baseline) / baseline * 100.0


def detect_regressions(
    results: List[AggregatedResult],
    baselines: dict,  # {size: float}  mean_ms baseline per size
    threshold_pct: float = 10.0,
) -> List[RegressionResult]:
    """Compare aggregated results against a baseline dict.

    A regression is flagged when current mean exceeds baseline by more than
    *threshold_pct* percent.
    """
    output: List[RegressionResult] = []
    for agg in sorted(results, key=lambda r: r.size):
        baseline_ms = baselines.get(agg.size)
        current_ms = agg.mean
        if baseline_ms is None or current_ms is None:
            output.append(
                RegressionResult(
                    size=agg.size,
                    baseline_ms=baseline_ms,
                    current_ms=current_ms,
                    delta_ms=None,
                    delta_pct=None,
                    is_regression=False,
                )
            )
            continue
        delta_ms = current_ms - baseline_ms
        delta_pct = _pct(current_ms, baseline_ms)
        is_regression = delta_pct > threshold_pct
        output.append(
            RegressionResult(
                size=agg.size,
                baseline_ms=baseline_ms,
                current_ms=current_ms,
                delta_ms=delta_ms,
                delta_pct=delta_pct,
                is_regression=is_regression,
            )
        )
    return output


def any_regression(results: List[RegressionResult]) -> bool:
    """Return True if at least one result is flagged as a regression."""
    return any(r.is_regression for r in results)
