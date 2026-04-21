"""Group timing results into named buckets based on size ranges."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from batchmark.timer import TimingResult


@dataclass
class GroupConfig:
    """Configuration for grouping results into named size buckets."""
    # List of (label, min_size, max_size) tuples; max_size=None means unbounded
    buckets: List[Tuple[str, int, Optional[int]]] = field(default_factory=list)
    default_label: str = "other"


@dataclass
class GroupedResult:
    """A timing result annotated with its bucket label."""
    result: TimingResult
    label: str

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> float:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def _find_label(size: int, config: GroupConfig) -> str:
    for label, lo, hi in config.buckets:
        if size >= lo and (hi is None or size <= hi):
            return label
    return config.default_label


def group_results(
    results: List[TimingResult],
    config: GroupConfig,
) -> List[GroupedResult]:
    """Assign each result to a bucket label based on its size."""
    return [GroupedResult(result=r, label=_find_label(r.size, config)) for r in results]


def results_by_label(
    grouped: List[GroupedResult],
) -> Dict[str, List[GroupedResult]]:
    """Return a dict mapping each label to its list of GroupedResults."""
    out: Dict[str, List[GroupedResult]] = {}
    for g in grouped:
        out.setdefault(g.label, []).append(g)
    return out
