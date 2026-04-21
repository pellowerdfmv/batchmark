"""splitter.py — split timing results into named partitions based on size ranges."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class SplitConfig:
    """Configuration for partitioning results into named buckets.

    partitions: mapping of partition name -> (min_size, max_size) inclusive.
    default_partition: name to use when no range matches; None drops the result.
    """

    partitions: Dict[str, tuple]  # name -> (min_size, max_size)
    default_partition: Optional[str] = None


@dataclass
class SplitResult:
    result: TimingResult
    partition: Optional[str]

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> float:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def _find_partition(size: int, config: SplitConfig) -> Optional[str]:
    for name, (lo, hi) in config.partitions.items():
        if lo <= size <= hi:
            return name
    return config.default_partition


def split_results(
    results: List[TimingResult], config: SplitConfig
) -> List[SplitResult]:
    """Assign each result to a partition; results with no matching partition
    and no default are still included with partition=None."""
    return [
        SplitResult(result=r, partition=_find_partition(r.size, config))
        for r in results
    ]


def group_by_partition(
    split: List[SplitResult],
) -> Dict[Optional[str], List[SplitResult]]:
    """Return a dict mapping partition name -> list of SplitResults."""
    groups: Dict[Optional[str], List[SplitResult]] = {}
    for sr in split:
        groups.setdefault(sr.partition, []).append(sr)
    return groups


def format_split_summary(groups: Dict[Optional[str], List[SplitResult]]) -> str:
    lines = ["Partition summary:"]
    for name, items in sorted(groups.items(), key=lambda kv: (kv[0] is None, kv[0])):
        label = name if name is not None else "(unmatched)"
        ok = sum(1 for sr in items if sr.success)
        lines.append(f"  {label}: {len(items)} results, {ok} successful")
    return "\n".join(lines)
