"""Outlier detection for timing results using IQR-based filtering."""

from dataclasses import dataclass
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class OutlierConfig:
    iqr_multiplier: float = 1.5
    min_samples: int = 4


@dataclass
class OutlierResult:
    result: TimingResult
    is_outlier: bool
    lower_fence: Optional[float]
    upper_fence: Optional[float]

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> float:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.success


def _quartiles(values: List[float]):
    """Return (Q1, Q3) for a sorted list of values."""
    n = len(values)
    mid = n // 2
    lower = sorted(values[:mid])
    upper = sorted(values[mid:]) if n % 2 == 0 else sorted(values[mid + 1:])
    q1 = lower[len(lower) // 2] if len(lower) % 2 == 1 else (lower[len(lower) // 2 - 1] + lower[len(lower) // 2]) / 2
    q3 = upper[len(upper) // 2] if len(upper) % 2 == 1 else (upper[len(upper) // 2 - 1] + upper[len(upper) // 2]) / 2
    return q1, q3


def detect_outliers(
    results: List[TimingResult],
    config: Optional[OutlierConfig] = None,
) -> List[OutlierResult]:
    """Tag each result as an outlier or not using the IQR method."""
    if config is None:
        config = OutlierConfig()

    successful = [r for r in results if r.success]
    durations = sorted(r.duration for r in successful)

    lower_fence: Optional[float] = None
    upper_fence: Optional[float] = None

    if len(durations) >= config.min_samples:
        q1, q3 = _quartiles(durations)
        iqr = q3 - q1
        lower_fence = q1 - config.iqr_multiplier * iqr
        upper_fence = q3 + config.iqr_multiplier * iqr

    outlier_results = []
    for r in results:
        if not r.success or lower_fence is None or upper_fence is None:
            is_outlier = False
        else:
            is_outlier = r.duration < lower_fence or r.duration > upper_fence
        outlier_results.append(
            OutlierResult(
                result=r,
                is_outlier=is_outlier,
                lower_fence=lower_fence,
                upper_fence=upper_fence,
            )
        )
    return outlier_results
