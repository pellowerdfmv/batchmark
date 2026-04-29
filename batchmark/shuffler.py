"""Shuffler: randomly reorder benchmark results with optional seeding."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass(frozen=True)
class ShufflerConfig:
    seed: Optional[int] = None
    per_size: bool = False


@dataclass(frozen=True)
class ShuffledResult:
    result: TimingResult
    original_index: int
    shuffled_index: int

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> float:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def _shuffle_with_seed(
    items: List[TimingResult], seed: Optional[int]
) -> List[TimingResult]:
    rng = random.Random(seed)
    shuffled = list(items)
    rng.shuffle(shuffled)
    return shuffled


def shuffle_results(
    results: List[TimingResult],
    config: Optional[ShufflerConfig] = None,
) -> List[ShuffledResult]:
    if config is None:
        config = ShufflerConfig()

    if not results:
        return []

    if config.per_size:
        from collections import defaultdict

        groups: dict = defaultdict(list)
        for r in results:
            groups[r.size].append(r)

        shuffled_flat: List[TimingResult] = []
        for size in sorted(groups):
            shuffled_flat.extend(_shuffle_with_seed(groups[size], config.seed))
    else:
        shuffled_flat = _shuffle_with_seed(results, config.seed)

    return [
        ShuffledResult(result=r, original_index=results.index(r), shuffled_index=i)
        for i, r in enumerate(shuffled_flat)
    ]


def format_shuffle_summary(shuffled: List[ShuffledResult]) -> str:
    total = len(shuffled)
    moved = sum(1 for s in shuffled if s.original_index != s.shuffled_index)
    return f"Shuffled {total} result(s); {moved} changed position."
