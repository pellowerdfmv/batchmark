"""Merge multiple lists of TimingResults into a unified result set.

Useful when combining results from separate benchmark runs (e.g. different
machines or different time windows) before aggregation or comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class MergeConfig:
    """Configuration for merging result sets."""

    # Optional label to tag the source of each batch (parallel to result_sets)
    labels: Optional[List[str]] = None
    # If True, drop results whose size does not appear in ALL batches
    intersect_sizes: bool = False


@dataclass
class MergedResult:
    """A TimingResult annotated with its source label."""

    result: TimingResult
    label: str

    # Proxy helpers so callers can treat MergedResult like TimingResult
    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> Optional[float]:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def merge_results(
    result_sets: List[List[TimingResult]],
    config: Optional[MergeConfig] = None,
) -> List[MergedResult]:
    """Merge *result_sets* into a flat list of :class:`MergedResult`.

    Parameters
    ----------
    result_sets:
        One or more lists of :class:`~batchmark.timer.TimingResult`.
    config:
        Optional :class:`MergeConfig` controlling labels and size filtering.

    Returns
    -------
    list[MergedResult]
        Flat, label-annotated results ordered by source batch then by size.
    """
    if config is None:
        config = MergeConfig()

    labels: List[str] = []
    if config.labels:
        labels = list(config.labels)
    # Pad missing labels with generated defaults
    for i in range(len(labels), len(result_sets)):
        labels.append(f"batch_{i}")

    if config.intersect_sizes and result_sets:
        common: set = set(r.size for r in result_sets[0])
        for batch in result_sets[1:]:
            common &= set(r.size for r in batch)
    else:
        common = None  # type: ignore[assignment]

    merged: List[MergedResult] = []
    for label, batch in zip(labels, result_sets):
        for result in sorted(batch, key=lambda r: r.size):
            if common is not None and result.size not in common:
                continue
            merged.append(MergedResult(result=result, label=label))

    return merged


def format_merge_summary(merged: List[MergedResult]) -> str:
    """Return a human-readable summary of a merged result set."""
    if not merged:
        return "No merged results."
    labels = sorted({m.label for m in merged})
    lines = [f"Merged {len(merged)} result(s) from {len(labels)} source(s):"]
    for label in labels:
        subset = [m for m in merged if m.label == label]
        sizes = sorted({m.size for m in subset})
        lines.append(f"  [{label}] {len(subset)} result(s), sizes: {sizes}")
    return "\n".join(lines)
