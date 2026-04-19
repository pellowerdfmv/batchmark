"""Filtering utilities for TimingResult lists."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class FilterConfig:
    sizes: List[int] = field(default_factory=list)
    only_success: bool = False
    max_duration: Optional[float] = None


def filter_by_size(results: List[TimingResult], sizes: List[int]) -> List[TimingResult]:
    if not sizes:
        return results
    size_set = set(sizes)
    return [r for r in results if r.size in size_set]


def filter_by_success(results: List[TimingResult]) -> List[TimingResult]:
    return [r for r in results if r.success]


def filter_by_max_duration(
    results: List[TimingResult], max_duration: float
) -> List[TimingResult]:
    return [r for r in results if r.duration <= max_duration]


def filter_results(
    results: List[TimingResult], config: FilterConfig
) -> List[TimingResult]:
    out = filter_by_size(results, config.sizes)
    if config.only_success:
        out = filter_by_success(out)
    if config.max_duration is not None:
        out = filter_by_max_duration(out, config.max_duration)
    return out
