"""Trend analysis: detect whether benchmark durations are improving,
degrading, or stable across increasing input sizes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from batchmark.aggregator import AggregatedResult


@dataclass
class TrendResult:
    size: int
    mean: Optional[float]          # ms, None when no successful runs
    delta: Optional[float]         # ms change from previous size, None for first
    delta_pct: Optional[float]     # % change from previous size, None for first
    direction: str                 # "up", "down", "flat", or "n/a"


_FLAT_THRESHOLD_PCT = 5.0          # changes within ±5 % are considered flat


def _direction(delta_pct: Optional[float]) -> str:
    if delta_pct is None:
        return "n/a"
    if delta_pct > _FLAT_THRESHOLD_PCT:
        return "up"
    if delta_pct < -_FLAT_THRESHOLD_PCT:
        return "down"
    return "flat"


def analyze_trend(aggregated: Sequence[AggregatedResult]) -> List[TrendResult]:
    """Return one TrendResult per aggregated row, sorted by size ascending."""
    sorted_rows = sorted(aggregated, key=lambda r: r.size)
    results: List[TrendResult] = []
    prev_mean: Optional[float] = None

    for row in sorted_rows:
        mean = row.mean  # may be None
        delta: Optional[float] = None
        delta_pct: Optional[float] = None

        if mean is not None and prev_mean is not None:
            delta = mean - prev_mean
            if prev_mean != 0.0:
                delta_pct = (delta / prev_mean) * 100.0
            else:
                delta_pct = None

        results.append(
            TrendResult(
                size=row.size,
                mean=mean,
                delta=delta,
                delta_pct=delta_pct,
                direction=_direction(delta_pct),
            )
        )
        if mean is not None:
            prev_mean = mean

    return results


def format_trend_summary(trends: Sequence[TrendResult]) -> str:
    ups = sum(1 for t in trends if t.direction == "up")
    downs = sum(1 for t in trends if t.direction == "down")
    flats = sum(1 for t in trends if t.direction == "flat")
    return (
        f"Trend summary: {ups} size(s) slower, "
        f"{downs} faster, {flats} flat "
        f"(threshold ±{_FLAT_THRESHOLD_PCT:.0f}%)"
    )
