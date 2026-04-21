"""Scale timing results by a factor or relative to a reference size."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class ScaledResult:
    result: TimingResult
    scale_factor: float
    scaled_duration: Optional[float]  # None if result failed

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
class ScalerConfig:
    factor: Optional[float] = None          # fixed multiplier
    reference_size: Optional[int] = None    # scale relative to mean of this size


def _mean_duration(results: List[TimingResult]) -> Optional[float]:
    durations = [r.duration for r in results if r.returncode == 0]
    if not durations:
        return None
    return sum(durations) / len(durations)


def scale_results(
    results: List[TimingResult],
    config: ScalerConfig,
) -> List[ScaledResult]:
    """Return a ScaledResult for every input result.

    If *factor* is set, every duration is multiplied by that factor.
    If *reference_size* is set, the factor is derived from the mean duration
    of results whose size matches *reference_size* (factor = 1 / mean_ref).
    If neither is set, factor defaults to 1.0 (identity).
    """
    factor = config.factor

    if factor is None and config.reference_size is not None:
        ref_results = [r for r in results if r.size == config.reference_size]
        ref_mean = _mean_duration(ref_results)
        factor = (1.0 / ref_mean) if ref_mean else 1.0

    if factor is None:
        factor = 1.0

    scaled: List[ScaledResult] = []
    for r in results:
        sd = r.duration * factor if r.returncode == 0 else None
        scaled.append(ScaledResult(result=r, scale_factor=factor, scaled_duration=sd))
    return scaled


def format_scale_summary(scaled: List[ScaledResult]) -> str:
    if not scaled:
        return "No results to scale."
    factor = scaled[0].scale_factor
    applied = sum(1 for s in scaled if s.scaled_duration is not None)
    return (
        f"Scale factor: {factor:.4f} | "
        f"Applied to {applied}/{len(scaled)} results"
    )
