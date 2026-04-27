"""Pivot aggregated results into a size x metric table."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.aggregator import AggregatedResult


@dataclass
class PivotTable:
    """A pivot table with sizes as rows and metrics as columns."""

    metrics: List[str]
    rows: List["PivotRow"]


@dataclass
class PivotRow:
    size: int
    values: Dict[str, Optional[float]] = field(default_factory=dict)


_AVAILABLE_METRICS = ("mean", "median", "stdev", "min", "max")


def available_metrics() -> List[str]:
    return list(_AVAILABLE_METRICS)


def _extract(result: AggregatedResult, metric: str) -> Optional[float]:
    return {
        "mean": result.mean,
        "median": result.median,
        "stdev": result.stdev,
        "min": result.min,
        "max": result.max,
    }.get(metric)


def pivot_results(
    results: List[AggregatedResult],
    metrics: Optional[List[str]] = None,
) -> PivotTable:
    """Build a PivotTable from aggregated results.

    Args:
        results: Aggregated benchmark results (one per size).
        metrics: Subset of metrics to include; defaults to all.

    Returns:
        A PivotTable with one row per size.
    """
    if metrics is None:
        metrics = list(_AVAILABLE_METRICS)

    unknown = [m for m in metrics if m not in _AVAILABLE_METRICS]
    if unknown:
        raise ValueError(f"Unknown metrics: {unknown}")

    sorted_results = sorted(results, key=lambda r: r.size)
    rows: List[PivotRow] = []
    for r in sorted_results:
        values = {m: _extract(r, m) for m in metrics}
        rows.append(PivotRow(size=r.size, values=values))

    return PivotTable(metrics=list(metrics), rows=rows)


def format_pivot_summary(table: PivotTable) -> str:
    """Return a human-readable summary line for the pivot table."""
    return (
        f"Pivot table: {len(table.rows)} size(s), "
        f"{len(table.metrics)} metric(s): {', '.join(table.metrics)}"
    )
