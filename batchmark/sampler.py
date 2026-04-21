"""Random and systematic sampling of timing results."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class SamplerConfig:
    """Configuration for result sampling."""
    fraction: float = 1.0          # 0.0–1.0, fraction of results to keep
    max_per_size: Optional[int] = None  # cap results per input size
    seed: Optional[int] = None     # random seed for reproducibility
    only_successful: bool = False  # sample only from successful runs


def _group_by_size(results: List[TimingResult]):
    groups: dict = {}
    for r in results:
        groups.setdefault(r.size, []).append(r)
    return groups


def sample_results(
    results: List[TimingResult],
    config: SamplerConfig,
) -> List[TimingResult]:
    """Return a sampled subset of *results* according to *config*."""
    rng = random.Random(config.seed)

    candidates = (
        [r for r in results if r.returncode == 0]
        if config.only_successful
        else list(results)
    )

    groups = _group_by_size(candidates)
    sampled: List[TimingResult] = []

    for size in sorted(groups):
        group = groups[size]
        # Apply fraction
        k = max(1, round(len(group) * config.fraction)) if group else 0
        k = min(k, len(group))
        chosen = rng.sample(group, k)
        # Apply per-size cap
        if config.max_per_size is not None:
            chosen = chosen[: config.max_per_size]
        sampled.extend(chosen)

    return sampled


def format_sample_summary(original: List[TimingResult], sampled: List[TimingResult]) -> str:
    """Return a one-line summary of how many results were sampled."""
    pct = (len(sampled) / len(original) * 100) if original else 0.0
    return (
        f"Sampled {len(sampled)}/{len(original)} results "
        f"({pct:.1f}%) across {len({r.size for r in sampled})} size(s)"
    )
