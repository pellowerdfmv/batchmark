"""Normalize timing results to a 0-1 scale within each size group."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class NormalizedResult:
    result: TimingResult
    normalized: Optional[float]  # None if normalization not possible

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> float:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


@dataclass
class NormalizerConfig:
    only_successful: bool = True
    clamp: bool = False  # clamp values outside [0, 1] to boundary


def _group_by_size(results: List[TimingResult]):
    groups: dict = {}
    for r in results:
        groups.setdefault(r.size, []).append(r)
    return groups


def normalize_results(
    results: List[TimingResult],
    config: Optional[NormalizerConfig] = None,
) -> List[NormalizedResult]:
    """Return one NormalizedResult per input result.

    Within each size group the duration is scaled so that the minimum
    successful duration maps to 0.0 and the maximum maps to 1.0.
    Results that cannot be normalized (e.g. only one unique value, or
    all failures when only_successful is True) receive ``None``.
    """
    if config is None:
        config = NormalizerConfig()

    groups = _group_by_size(results)

    # Pre-compute per-size min/max from eligible durations
    bounds: dict = {}
    for size, group in groups.items():
        eligible = [
            r.duration
            for r in group
            if (not config.only_successful or r.returncode == 0)
        ]
        if len(eligible) < 2 or max(eligible) == min(eligible):
            bounds[size] = None
        else:
            bounds[size] = (min(eligible), max(eligible))

    out: List[NormalizedResult] = []
    for r in results:
        lo_hi = bounds.get(r.size)
        if lo_hi is None:
            out.append(NormalizedResult(result=r, normalized=None))
            continue
        lo, hi = lo_hi
        norm = (r.duration - lo) / (hi - lo)
        if config.clamp:
            norm = max(0.0, min(1.0, norm))
        out.append(NormalizedResult(result=r, normalized=norm))
    return out


def format_normalized_summary(normalized: List[NormalizedResult]) -> str:
    """Return a compact summary line for the normalized results."""
    total = len(normalized)
    scored = sum(1 for n in normalized if n.normalized is not None)
    return f"Normalized {scored}/{total} results across {len({n.size for n in normalized})} size(s)."
