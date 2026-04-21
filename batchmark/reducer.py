"""reducer.py — reduce a list of TimingResults per size into a single representative result.

Supported strategies: mean, median, min, max.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Literal

from batchmark.timer import TimingResult
from batchmark.stats import mean, median, min_duration, max_duration


ReduceStrategy = Literal["mean", "median", "min", "max"]

AVAILABLE_STRATEGIES: List[ReduceStrategy] = ["mean", "median", "min", "max"]


@dataclass
class ReducedResult:
    size: int
    strategy: str
    duration: Optional[float]  # seconds; None if no successful runs
    total_runs: int
    successful_runs: int

    @property
    def success(self) -> bool:
        return self.duration is not None


def _apply_strategy(results: List[TimingResult], strategy: ReduceStrategy) -> Optional[float]:
    """Return the representative duration in seconds, or None."""
    if strategy == "mean":
        ms = mean(results)
    elif strategy == "median":
        ms = median(results)
    elif strategy == "min":
        ms = min_duration(results)
    elif strategy == "max":
        ms = max_duration(results)
    else:
        raise ValueError(f"Unknown strategy: {strategy!r}")

    return ms / 1000.0 if ms is not None else None


def reduce_results(
    results: List[TimingResult],
    strategy: ReduceStrategy = "mean",
) -> List[ReducedResult]:
    """Reduce *results* grouped by size using *strategy*.

    Returns one :class:`ReducedResult` per distinct size, sorted ascending.
    """
    if strategy not in AVAILABLE_STRATEGIES:
        raise ValueError(
            f"Unknown strategy {strategy!r}. Choose from {AVAILABLE_STRATEGIES}."
        )

    groups: dict[int, List[TimingResult]] = {}
    for r in results:
        groups.setdefault(r.size, []).append(r)

    reduced: List[ReducedResult] = []
    for size in sorted(groups):
        group = groups[size]
        duration = _apply_strategy(group, strategy)
        successful = sum(1 for r in group if r.returncode == 0)
        reduced.append(
            ReducedResult(
                size=size,
                strategy=strategy,
                duration=duration,
                total_runs=len(group),
                successful_runs=successful,
            )
        )
    return reduced


def format_reduced_summary(reduced: List[ReducedResult]) -> str:
    """Return a short human-readable summary string."""
    if not reduced:
        return "No reduced results."
    strategy = reduced[0].strategy
    lines = [f"Reduction strategy: {strategy}", f"{'Size':>10}  {'Duration (ms)':>14}  {'Runs':>6}  {'OK':>4}"]
    for r in reduced:
        dur = f"{r.duration * 1000:.2f}" if r.duration is not None else "N/A"
        lines.append(f"{r.size:>10}  {dur:>14}  {r.total_runs:>6}  {r.successful_runs:>4}")
    return "\n".join(lines)
