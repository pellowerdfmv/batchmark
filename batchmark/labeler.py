"""Attach human-readable labels to benchmark results for grouping and display."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class LabeledResult:
    """A TimingResult decorated with an arbitrary string label."""

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


@dataclass
class LabelConfig:
    """Mapping from label name to a list of sizes that belong to that label."""

    label_map: Dict[str, List[int]] = field(default_factory=dict)
    default_label: str = "unlabeled"


def _build_size_to_label(config: LabelConfig) -> Dict[int, str]:
    """Invert the label_map so we can look up a label by size in O(1)."""
    mapping: Dict[int, str] = {}
    for label, sizes in config.label_map.items():
        for size in sizes:
            mapping[size] = label
    return mapping


def label_results(
    results: List[TimingResult],
    config: LabelConfig,
) -> List[LabeledResult]:
    """Attach a label to every result according to *config*.

    Sizes not covered by *config.label_map* receive *config.default_label*.
    """
    lookup = _build_size_to_label(config)
    labeled: List[LabeledResult] = []
    for r in results:
        lbl = lookup.get(r.size, config.default_label)
        labeled.append(LabeledResult(result=r, label=lbl))
    return labeled


def group_by_label(
    labeled: List[LabeledResult],
) -> Dict[str, List[LabeledResult]]:
    """Partition a list of LabeledResult objects by their label."""
    groups: Dict[str, List[LabeledResult]] = {}
    for lr in labeled:
        groups.setdefault(lr.label, []).append(lr)
    return groups


def available_labels(labeled: List[LabeledResult]) -> List[str]:
    """Return the sorted, deduplicated list of labels present in *labeled*."""
    return sorted({lr.label for lr in labeled})
