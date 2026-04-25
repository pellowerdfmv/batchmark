"""binner.py — groups TimingResults into discrete size bins and computes per-bin stats."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from batchmark.timer import TimingResult


@dataclass
class BinConfig:
    """Configuration for binning.

    edges defines the *right* edges of each bin (inclusive).
    Labels are optional; if omitted, auto-generated from edges.
    """
    edges: List[int]
    labels: List[str] = field(default_factory=list)
    default_label: str = "overflow"


@dataclass
class BinnedResult:
    result: TimingResult
    bin_label: str

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
class BinSummary:
    label: str
    count: int
    successful: int
    mean_ms: Optional[float]


def _resolve_label(config: BinConfig, index: int) -> str:
    if index < len(config.labels):
        return config.labels[index]
    if index < len(config.edges):
        return f"<={config.edges[index]}"
    return config.default_label


def bin_results(results: Sequence[TimingResult], config: BinConfig) -> List[BinnedResult]:
    """Assign each result to a bin based on its size."""
    binned: List[BinnedResult] = []
    for r in results:
        label = config.default_label
        for i, edge in enumerate(config.edges):
            if r.size <= edge:
                label = _resolve_label(config, i)
                break
        binned.append(BinnedResult(result=r, bin_label=label))
    return binned


def summarize_bins(binned: Sequence[BinnedResult]) -> List[BinSummary]:
    """Return one BinSummary per unique bin_label, ordered by first appearance."""
    order: List[str] = []
    groups: dict[str, List[BinnedResult]] = {}
    for b in binned:
        if b.bin_label not in groups:
            order.append(b.bin_label)
            groups[b.bin_label] = []
        groups[b.bin_label].append(b)

    summaries: List[BinSummary] = []
    for label in order:
        items = groups[label]
        successes = [i for i in items if i.success]
        mean_ms: Optional[float] = None
        if successes:
            mean_ms = sum(i.duration for i in successes) / len(successes) * 1000
        summaries.append(BinSummary(
            label=label,
            count=len(items),
            successful=len(successes),
            mean_ms=mean_ms,
        ))
    return summaries
