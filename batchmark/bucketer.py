"""Bucketer: assign timing results into named duration buckets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from batchmark.timer import TimingResult


@dataclass
class BucketConfig:
    """Configuration for bucketing results by duration.

    Thresholds are (upper_bound_ms, label) pairs sorted ascending.
    Results exceeding all thresholds fall into *default_label*.
    """
    thresholds: List[Tuple[float, str]] = field(default_factory=list)
    default_label: str = "slow"


@dataclass
class BucketedResult:
    result: TimingResult
    bucket: Optional[str]

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> Optional[float]:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.success


def _find_bucket(duration_ms: float, config: BucketConfig) -> str:
    sorted_thresholds = sorted(config.thresholds, key=lambda t: t[0])
    for upper, label in sorted_thresholds:
        if duration_ms <= upper:
            return label
    return config.default_label


def bucket_results(
    results: Sequence[TimingResult],
    config: Optional[BucketConfig] = None,
) -> List[BucketedResult]:
    """Assign each result to a bucket based on its duration in milliseconds.

    Failed results (success=False) receive bucket=None.
    """
    if config is None:
        config = BucketConfig()

    bucketed: List[BucketedResult] = []
    for r in results:
        if not r.success or r.duration is None:
            bucketed.append(BucketedResult(result=r, bucket=None))
        else:
            duration_ms = r.duration * 1000.0
            label = _find_bucket(duration_ms, config)
            bucketed.append(BucketedResult(result=r, bucket=label))
    return bucketed


def format_bucket_summary(bucketed: Sequence[BucketedResult]) -> str:
    """Return a short summary of how many results fell into each bucket."""
    counts: dict[str, int] = {}
    failed = 0
    for br in bucketed:
        if br.bucket is None:
            failed += 1
        else:
            counts[br.bucket] = counts.get(br.bucket, 0) + 1
    parts = [f"{label}={n}" for label, n in sorted(counts.items())]
    if failed:
        parts.append(f"failed={failed}")
    return "buckets: " + ", ".join(parts) if parts else "buckets: (empty)"
