"""Segment timing results into named ranges based on size thresholds."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from batchmark.timer import TimingResult


@dataclass
class SegmentConfig:
    """Configuration for segmenting results by size."""

    # List of (upper_bound_exclusive, label) pairs, sorted ascending.
    # Sizes >= last upper bound fall into the final segment.
    thresholds: List[tuple] = field(default_factory=list)  # [(bound, label), ...]
    default_label: str = "other"


@dataclass
class SegmentedResult:
    result: TimingResult
    segment: str

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> Optional[float]:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def _find_segment(size: int, config: SegmentConfig) -> str:
    for bound, label in sorted(config.thresholds, key=lambda t: t[0]):
        if size < bound:
            return label
    return config.default_label


def segment_results(
    results: Sequence[TimingResult],
    config: Optional[SegmentConfig] = None,
) -> List[SegmentedResult]:
    """Assign each result to a named segment based on its size."""
    if config is None:
        config = SegmentConfig()
    return [SegmentedResult(result=r, segment=_find_segment(r.size, config)) for r in results]


def format_segment_summary(segmented: Sequence[SegmentedResult]) -> str:
    """Return a short summary of how many results fall in each segment."""
    counts: dict = {}
    for s in segmented:
        counts[s.segment] = counts.get(s.segment, 0) + 1
    if not counts:
        return "No results."
    lines = [f"  {label}: {count} result(s)" for label, count in sorted(counts.items())]
    return "Segment summary:\n" + "\n".join(lines)
