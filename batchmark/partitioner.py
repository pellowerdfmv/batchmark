"""Partition timing results into named time-based buckets (e.g. fast / medium / slow)
based on configurable percentile thresholds."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from batchmark.timer import TimingResult


@dataclass
class PartitionConfig:
    """Thresholds (in ms) that separate partitions.

    Partitions are named in *labels* from lowest to highest.  There must be
    exactly ``len(thresholds) + 1`` labels.
    """

    thresholds: List[float] = field(default_factory=lambda: [200.0, 1000.0])
    labels: List[str] = field(default_factory=lambda: ["fast", "medium", "slow"])

    def __post_init__(self) -> None:
        if len(self.labels) != len(self.thresholds) + 1:
            raise ValueError(
                "len(labels) must equal len(thresholds) + 1, "
                f"got {len(self.labels)} labels and {len(self.thresholds)} thresholds"
            )


@dataclass
class PartitionedResult:
    result: TimingResult
    partition: Optional[str]

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> Optional[float]:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def _find_partition(duration_ms: float, config: PartitionConfig) -> str:
    for threshold, label in zip(config.thresholds, config.labels):
        if duration_ms < threshold:
            return label
    return config.labels[-1]


def partition_results(
    results: Sequence[TimingResult],
    config: Optional[PartitionConfig] = None,
) -> List[PartitionedResult]:
    """Assign each result to a named partition based on its duration.

    Failed results (non-zero returncode) are assigned ``None`` as the partition.
    """
    if config is None:
        config = PartitionConfig()

    out: List[PartitionedResult] = []
    for r in results:
        if r.returncode != 0 or r.duration is None:
            out.append(PartitionedResult(result=r, partition=None))
        else:
            duration_ms = r.duration * 1000.0
            out.append(
                PartitionedResult(result=r, partition=_find_partition(duration_ms, config))
            )
    return out


def format_partition_summary(partitioned: Sequence[PartitionedResult]) -> str:
    """Return a one-line summary of partition counts."""
    counts: dict[str, int] = {}
    failed = 0
    for pr in partitioned:
        if pr.partition is None:
            failed += 1
        else:
            counts[pr.partition] = counts.get(pr.partition, 0) + 1
    parts = [f"{label}={n}" for label, n in counts.items()]
    if failed:
        parts.append(f"failed={failed}")
    return "partitions: " + ", ".join(parts) if parts else "partitions: (none)"
