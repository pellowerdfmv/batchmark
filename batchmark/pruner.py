"""pruner.py — remove results that fall outside a percentile band."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class PrunerConfig:
    """Configuration for percentile-based pruning."""
    lower_pct: float = 0.0   # e.g. 0.05 removes bottom 5 %
    upper_pct: float = 1.0   # e.g. 0.95 removes top 5 %
    only_successful: bool = True  # only consider successful runs when computing bounds


@dataclass
class PrunedResult:
    result: TimingResult
    pruned: bool
    reason: Optional[str]

    # Proxy helpers so callers can treat PrunedResult like TimingResult.
    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> Optional[float]:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def _sorted_durations(results: List[TimingResult], only_successful: bool) -> List[float]:
    durations = [
        r.duration
        for r in results
        if r.duration is not None and (not only_successful or r.returncode == 0)
    ]
    return sorted(durations)


def _percentile(sorted_values: List[float], pct: float) -> Optional[float]:
    if not sorted_values:
        return None
    idx = pct * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def prune_results(
    results: List[TimingResult],
    config: Optional[PrunerConfig] = None,
) -> List[PrunedResult]:
    """Tag each result as pruned/kept based on percentile bounds."""
    if config is None:
        config = PrunerConfig()

    sorted_d = _sorted_durations(results, config.only_successful)
    lower_bound = _percentile(sorted_d, config.lower_pct)
    upper_bound = _percentile(sorted_d, config.upper_pct)

    pruned: List[PrunedResult] = []
    for r in results:
        d = r.duration
        if d is None:
            pruned.append(PrunedResult(result=r, pruned=False, reason=None))
            continue
        if lower_bound is not None and d < lower_bound:
            pruned.append(PrunedResult(result=r, pruned=True, reason="below_lower_pct"))
        elif upper_bound is not None and d > upper_bound:
            pruned.append(PrunedResult(result=r, pruned=True, reason="above_upper_pct"))
        else:
            pruned.append(PrunedResult(result=r, pruned=False, reason=None))
    return pruned


def format_prune_summary(pruned: List[PrunedResult]) -> str:
    total = len(pruned)
    n_pruned = sum(1 for p in pruned if p.pruned)
    kept = total - n_pruned
    return f"Pruner: {total} results — {kept} kept, {n_pruned} pruned."
