"""Smoothing module: applies a rolling average over TimingResult sequences per size."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class SmoothedResult:
    result: TimingResult
    smoothed_duration: Optional[float]  # None if not enough data
    window_size: int

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
class SmootherConfig:
    window_size: int = 3
    only_successful: bool = True


def _group_by_size(results: List[TimingResult]) -> dict:
    groups: dict = {}
    for r in results:
        groups.setdefault(r.size, []).append(r)
    return groups


def _rolling_average(values: List[float], index: int, window: int) -> Optional[float]:
    start = max(0, index - window + 1)
    window_vals = values[start : index + 1]
    if len(window_vals) < window:
        return None
    return sum(window_vals) / len(window_vals)


def smooth_results(
    results: List[TimingResult],
    config: Optional[SmootherConfig] = None,
) -> List[SmoothedResult]:
    if config is None:
        config = SmootherConfig()

    groups = _group_by_size(results)
    smoothed: List[SmoothedResult] = []

    for size in sorted(groups):
        group = groups[size]
        eligible = [
            r for r in group if (r.returncode == 0 or not config.only_successful)
        ]
        durations = [r.duration for r in eligible]

        eligible_idx = 0
        for r in group:
            is_eligible = r.returncode == 0 or not config.only_successful
            if is_eligible:
                avg = _rolling_average(durations, eligible_idx, config.window_size)
                eligible_idx += 1
            else:
                avg = None
            smoothed.append(SmoothedResult(result=r, smoothed_duration=avg, window_size=config.window_size))

    return smoothed


def format_smooth_summary(smoothed: List[SmoothedResult]) -> str:
    total = len(smoothed)
    computed = sum(1 for s in smoothed if s.smoothed_duration is not None)
    return f"Smoothing summary: {computed}/{total} results have a smoothed value (window={smoothed[0].window_size if smoothed else 'n/a'})"
