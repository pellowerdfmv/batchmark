"""Flatten nested or grouped results into a single ordered sequence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from batchmark.timer import TimingResult


@dataclass(frozen=True)
class FlattenedResult:
    result: TimingResult
    source_label: str
    flat_index: int

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
class FlattenConfig:
    labels: Optional[List[str]] = None
    sort_by_size: bool = False
    include_failures: bool = True


def flatten_results(
    groups: List[List[TimingResult]],
    config: Optional[FlattenConfig] = None,
) -> List[FlattenedResult]:
    """Flatten a list of result groups into a single list of FlattenedResult.

    Each group is assigned a label from *config.labels* (padded with
    "set_N" if fewer labels than groups are provided).  Results that
    failed are excluded when *config.include_failures* is False.
    """
    if config is None:
        config = FlattenConfig()

    flat: List[FlattenedResult] = []
    flat_index = 0

    for group_idx, group in enumerate(groups):
        if config.labels and group_idx < len(config.labels):
            label = config.labels[group_idx]
        else:
            label = f"set_{group_idx}"

        for result in group:
            if not config.include_failures and result.returncode != 0:
                continue
            flat.append(
                FlattenedResult(
                    result=result,
                    source_label=label,
                    flat_index=flat_index,
                )
            )
            flat_index += 1

    if config.sort_by_size:
        flat = sorted(flat, key=lambda r: r.size)
        # Re-number indices after sort
        flat = [
            FlattenedResult(
                result=fr.result,
                source_label=fr.source_label,
                flat_index=i,
            )
            for i, fr in enumerate(flat)
        ]

    return flat


def format_flatten_summary(results: List[FlattenedResult]) -> str:
    total = len(results)
    failed = sum(1 for r in results if not r.success)
    labels = sorted({r.source_label for r in results})
    label_str = ", ".join(labels) if labels else "(none)"
    return (
        f"Flattened {total} result(s) from [{label_str}]; "
        f"{failed} failure(s)"
    )
