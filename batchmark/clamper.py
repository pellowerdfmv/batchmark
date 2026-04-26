"""Clamp result durations to a configurable floor and ceiling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class ClampedResult:
    result: TimingResult
    original_duration: float
    clamped_duration: Optional[float]
    clamped: bool
    clamp_reason: Optional[str]  # "floor", "ceiling", or None

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> float:
        return self.clamped_duration if self.clamped_duration is not None else self.original_duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


@dataclass
class ClamperConfig:
    floor: Optional[float] = None   # minimum duration in seconds
    ceiling: Optional[float] = None  # maximum duration in seconds
    clamp_failures: bool = False     # whether to clamp failed results


def clamp_results(
    results: List[TimingResult],
    config: Optional[ClamperConfig] = None,
) -> List[ClampedResult]:
    """Apply floor/ceiling clamping to a list of timing results."""
    if config is None:
        config = ClamperConfig()

    clamped: List[ClampedResult] = []
    for r in results:
        original = r.duration
        is_failure = r.returncode != 0

        if is_failure and not config.clamp_failures:
            clamped.append(ClampedResult(
                result=r,
                original_duration=original,
                clamped_duration=original,
                clamped=False,
                clamp_reason=None,
            ))
            continue

        new_duration = original
        reason: Optional[str] = None

        if config.floor is not None and new_duration < config.floor:
            new_duration = config.floor
            reason = "floor"

        if config.ceiling is not None and new_duration > config.ceiling:
            new_duration = config.ceiling
            reason = "ceiling"

        clamped.append(ClampedResult(
            result=r,
            original_duration=original,
            clamped_duration=new_duration,
            clamped=(new_duration != original),
            clamp_reason=reason,
        ))

    return clamped


def format_clamp_summary(results: List[ClampedResult]) -> str:
    total = len(results)
    n_clamped = sum(1 for r in results if r.clamped)
    n_floor = sum(1 for r in results if r.clamp_reason == "floor")
    n_ceiling = sum(1 for r in results if r.clamp_reason == "ceiling")
    return (
        f"Clamped {n_clamped}/{total} results "
        f"(floor={n_floor}, ceiling={n_ceiling})"
    )
