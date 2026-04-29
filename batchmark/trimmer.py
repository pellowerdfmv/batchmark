"""Trimmer: remove leading and trailing results from each size group."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass(frozen=True)
class TrimmerConfig:
    head: int = 0  # number of results to drop from the start of each size group
    tail: int = 0  # number of results to drop from the end of each size group

    def __post_init__(self) -> None:
        if self.head < 0:
            raise ValueError("head must be >= 0")
        if self.tail < 0:
            raise ValueError("tail must be >= 0")


@dataclass(frozen=True)
class TrimmedResult:
    result: TimingResult
    size: int
    duration: float
    success: bool
    trimmed: bool


def _group_by_size(results: List[TimingResult]) -> dict:
    groups: dict = {}
    for r in results:
        groups.setdefault(r.size, []).append(r)
    return groups


def trim_results(
    results: List[TimingResult],
    config: Optional[TrimmerConfig] = None,
) -> List[TrimmedResult]:
    """Return TrimmedResult for every input, marking trimmed entries."""
    if config is None:
        config = TrimmerConfig()

    groups = _group_by_size(results)
    output: List[TrimmedResult] = []

    for size in sorted(groups):
        group = groups[size]
        n = len(group)
        keep_start = config.head
        keep_end = n - config.tail

        for idx, r in enumerate(group):
            trimmed = idx < keep_start or idx >= keep_end
            output.append(
                TrimmedResult(
                    result=r,
                    size=r.size,
                    duration=r.duration,
                    success=r.returncode == 0,
                    trimmed=trimmed,
                )
            )

    return output


def format_trim_summary(results: List[TrimmedResult]) -> str:
    total = len(results)
    trimmed = sum(1 for r in results if r.trimmed)
    kept = total - trimmed
    return f"Trimmer: {total} total, {kept} kept, {trimmed} trimmed"
