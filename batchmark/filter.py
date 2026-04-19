"""Filtering utilities for TimingResult collections."""

from typing import List, Optional
from batchmark.timer import TimingResult


def filter_by_size(
    results: List[TimingResult],
    sizes: Optional[List[int]] = None,
) -> List[TimingResult]:
    """Return only results whose size is in *sizes*.

    If *sizes* is None or empty the original list is returned unchanged.
    """
    if not sizes:
        return results
    size_set = set(sizes)
    return [r for r in results if r.size in size_set]


def filter_by_success(results: List[TimingResult]) -> List[TimingResult]:
    """Return only results where the command exited with return-code 0."""
    return [r for r in results if r.returncode == 0]


def filter_by_max_duration(
    results: List[TimingResult],
    max_seconds: float,
) -> List[TimingResult]:
    """Return only results whose elapsed time is <= *max_seconds*."""
    return [r for r in results if r.elapsed <= max_seconds]


def filter_results(
    results: List[TimingResult],
    *,
    sizes: Optional[List[int]] = None,
    only_success: bool = False,
    max_duration: Optional[float] = None,
) -> List[TimingResult]:
    """Convenience wrapper that applies all active filters in sequence."""
    out = results
    if sizes:
        out = filter_by_size(out, sizes)
    if only_success:
        out = filter_by_success(out)
    if max_duration is not None:
        out = filter_by_max_duration(out, max_duration)
    return out
