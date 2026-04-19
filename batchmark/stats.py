"""Statistical aggregation utilities for timing results."""

from __future__ import annotations

import math
from typing import List

from batchmark.timer import TimingResult


def _durations(results: List[TimingResult]) -> List[float]:
    return [r.duration for r in results if r.returncode == 0]


def mean(results: List[TimingResult]) -> float:
    """Return mean duration of successful runs, or NaN if none."""
    d = _durations(results)
    if not d:
        return float("nan")
    return sum(d) / len(d)


def median(results: List[TimingResult]) -> float:
    """Return median duration of successful runs, or NaN if none."""
    d = sorted(_durations(results))
    n = len(d)
    if not n:
        return float("nan")
    mid = n // 2
    return d[mid] if n % 2 else (d[mid - 1] + d[mid]) / 2.0


def stdev(results: List[TimingResult]) -> float:
    """Return sample standard deviation of successful runs, or NaN if < 2."""
    d = _durations(results)
    if len(d) < 2:
        return float("nan")
    m = sum(d) / len(d)
    variance = sum((x - m) ** 2 for x in d) / (len(d) - 1)
    return math.sqrt(variance)


def min_duration(results: List[TimingResult]) -> float:
    d = _durations(results)
    return min(d) if d else float("nan")


def max_duration(results: List[TimingResult]) -> float:
    d = _durations(results)
    return max(d) if d else float("nan")


def summarise(results: List[TimingResult]) -> dict:
    """Return a dict of all stats for a list of results sharing the same size."""
    return {
        "count": len(results),
        "success": sum(1 for r in results if r.returncode == 0),
        "mean": mean(results),
        "median": median(results),
        "stdev": stdev(results),
        "min": min_duration(results),
        "max": max_duration(results),
    }
