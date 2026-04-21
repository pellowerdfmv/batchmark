"""Deduplicator: remove duplicate TimingResult entries based on size and run index."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from batchmark.timer import TimingResult


@dataclass
class DeduplicatorConfig:
    """Configuration for deduplication behaviour."""
    keep: str = "first"  # "first" | "last" | "fastest"


def _key(result: TimingResult) -> Tuple[int, int]:
    """Return a (size, run_index) key for grouping."""
    return (result.size, result.run_index)


def _pick(candidates: List[TimingResult], keep: str) -> TimingResult:
    """Select one result from a group of duplicates."""
    if keep == "last":
        return candidates[-1]
    if keep == "fastest":
        successful = [r for r in candidates if r.returncode == 0]
        pool = successful if successful else candidates
        return min(pool, key=lambda r: r.duration)
    # default: "first"
    return candidates[0]


def deduplicate(results: List[TimingResult], config: DeduplicatorConfig | None = None) -> List[TimingResult]:
    """Return a deduplicated list of TimingResult, preserving original order of first occurrences."""
    if config is None:
        config = DeduplicatorConfig()

    groups: dict[Tuple[int, int], List[TimingResult]] = {}
    order: List[Tuple[int, int]] = []

    for r in results:
        k = _key(r)
        if k not in groups:
            groups[k] = []
            order.append(k)
        groups[k].append(r)

    return [_pick(groups[k], config.keep) for k in order]


def format_dedup_summary(before: int, after: int) -> str:
    """Return a human-readable summary of how many duplicates were removed."""
    removed = before - after
    return (
        f"Deduplication: {before} results -> {after} kept, {removed} duplicate(s) removed."
    )
