"""Rank aggregated results by mean duration, assigning position and tier labels."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.aggregator import AggregatedResult


@dataclass
class RankedResult:
    aggregated: AggregatedResult
    rank: int          # 1-based, lower is faster
    tier: str          # "fast", "medium", "slow"

    @property
    def size(self) -> int:
        return self.aggregated.size

    @property
    def mean(self) -> Optional[float]:
        return self.aggregated.mean


def _tier(rank: int, total: int) -> str:
    """Assign a tier label based on relative rank position."""
    if total <= 1:
        return "fast"
    pct = (rank - 1) / (total - 1)  # 0.0 … 1.0
    if pct <= 0.33:
        return "fast"
    if pct <= 0.66:
        return "medium"
    return "slow"


def rank_results(aggregated: List[AggregatedResult]) -> List[RankedResult]:
    """Sort aggregated results by mean duration (ascending) and assign ranks.

    Results with no mean (all runs failed) are placed at the end.
    """
    with_mean = [a for a in aggregated if a.mean is not None]
    without_mean = [a for a in aggregated if a.mean is None]

    sorted_results = sorted(with_mean, key=lambda a: a.mean)  # type: ignore[arg-type]
    total = len(sorted_results) + len(without_mean)

    ranked: List[RankedResult] = []
    for i, agg in enumerate(sorted_results):
        rank = i + 1
        ranked.append(RankedResult(aggregated=agg, rank=rank, tier=_tier(rank, total)))

    tail_start = len(sorted_results) + 1
    for j, agg in enumerate(without_mean):
        rank = tail_start + j
        ranked.append(RankedResult(aggregated=agg, rank=rank, tier="slow"))

    return ranked


def format_ranked(ranked: List[RankedResult]) -> str:
    """Return a plain-text table of ranked results."""
    lines = [f"{'Rank':<6} {'Size':>10} {'Mean (ms)':>12} {'Tier':<8}"]
    lines.append("-" * 40)
    for r in ranked:
        mean_str = f"{r.mean:.2f}" if r.mean is not None else "N/A"
        lines.append(f"{r.rank:<6} {r.size:>10} {mean_str:>12} {r.tier:<8}")
    return "\n".join(lines)
