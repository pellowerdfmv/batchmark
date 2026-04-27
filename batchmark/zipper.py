"""Zipper: pair results from two runs side-by-side by size and run index."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from batchmark.timer import TimingResult


@dataclass(frozen=True)
class ZippedPair:
    size: int
    index: int
    left: Optional[TimingResult]
    right: Optional[TimingResult]

    @property
    def left_duration(self) -> Optional[float]:
        if self.left is not None and self.left.returncode == 0:
            return self.left.duration
        return None

    @property
    def right_duration(self) -> Optional[float]:
        if self.right is not None and self.right.returncode == 0:
            return self.right.duration
        return None

    @property
    def delta(self) -> Optional[float]:
        if self.left_duration is not None and self.right_duration is not None:
            return self.right_duration - self.left_duration
        return None

    @property
    def both_present(self) -> bool:
        return self.left is not None and self.right is not None


@dataclass(frozen=True)
class ZipConfig:
    left_label: str = "left"
    right_label: str = "right"


def _group_by_size(
    results: Sequence[TimingResult],
) -> dict[int, List[TimingResult]]:
    groups: dict[int, List[TimingResult]] = {}
    for r in results:
        groups.setdefault(r.size, []).append(r)
    return groups


def zip_results(
    left: Sequence[TimingResult],
    right: Sequence[TimingResult],
    config: Optional[ZipConfig] = None,
) -> List[ZippedPair]:
    """Pair results from *left* and *right* by size and positional index."""
    if config is None:
        config = ZipConfig()

    left_groups = _group_by_size(left)
    right_groups = _group_by_size(right)
    all_sizes = sorted(set(left_groups) | set(right_groups))

    pairs: List[ZippedPair] = []
    for size in all_sizes:
        ls = left_groups.get(size, [])
        rs = right_groups.get(size, [])
        length = max(len(ls), len(rs))
        for i in range(length):
            l_item = ls[i] if i < len(ls) else None
            r_item = rs[i] if i < len(rs) else None
            pairs.append(ZippedPair(size=size, index=i, left=l_item, right=r_item))
    return pairs


def format_zip_summary(pairs: List[ZippedPair], config: Optional[ZipConfig] = None) -> str:
    if config is None:
        config = ZipConfig()
    complete = sum(1 for p in pairs if p.both_present)
    faster = sum(1 for p in pairs if p.delta is not None and p.delta < 0)
    slower = sum(1 for p in pairs if p.delta is not None and p.delta > 0)
    return (
        f"Zipped {len(pairs)} pair(s) | complete: {complete} | "
        f"{config.right_label} faster: {faster} | {config.right_label} slower: {slower}"
    )
