"""Correlates timing results against an external numeric variable per size."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from batchmark.aggregator import AggregatedResult


@dataclass
class CorrelationResult:
    size: int
    mean_ms: Optional[float]
    variable: Optional[float]
    # Pearson r computed across all sizes (same value on every row for convenience)
    pearson_r: Optional[float]


def _pearson(xs: List[float], ys: List[float]) -> Optional[float]:
    """Return Pearson correlation coefficient or None if not computable."""
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denom_x = sum((x - mx) ** 2 for x in xs) ** 0.5
    denom_y = sum((y - my) ** 2 for y in ys) ** 0.5
    if denom_x == 0 or denom_y == 0:
        return None
    return num / (denom_x * denom_y)


def correlate(
    results: List[AggregatedResult],
    variables: Dict[int, float],
) -> List[CorrelationResult]:
    """Pair each aggregated result with an external variable and compute Pearson r."""
    paired_means: List[float] = []
    paired_vars: List[float] = []

    sorted_results = sorted(results, key=lambda r: r.size)

    for r in sorted_results:
        if r.mean is not None and r.size in variables:
            paired_means.append(r.mean)
            paired_vars.append(variables[r.size])

    r_value = _pearson(paired_means, paired_vars)

    rows: List[CorrelationResult] = []
    for r in sorted_results:
        rows.append(
            CorrelationResult(
                size=r.size,
                mean_ms=r.mean,
                variable=variables.get(r.size),
                pearson_r=r_value,
            )
        )
    return rows


def format_correlation_summary(rows: List[CorrelationResult]) -> str:
    if not rows:
        return "No correlation data."
    r_val = rows[0].pearson_r
    r_str = f"{r_val:.4f}" if r_val is not None else "N/A"
    return f"Pearson r across {len(rows)} size(s): {r_str}"
