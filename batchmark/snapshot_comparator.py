"""Compare current aggregated results against a saved snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.aggregator import AggregatedResult
from batchmark.snapshotter import SnapshotEntry, lookup_snapshot


@dataclass
class SnapshotDiff:
    size: int
    current_mean: Optional[float]
    snapshot_mean: Optional[float]
    delta_ms: Optional[float]       # current - snapshot
    delta_pct: Optional[float]      # (delta / snapshot) * 100
    regression: bool                # True when slower by >0


def _pct(current: float, baseline: float) -> float:
    if baseline == 0.0:
        return 0.0
    return ((current - baseline) / baseline) * 100.0


def diff_against_snapshot(
    results: List[AggregatedResult],
    snapshot: List[SnapshotEntry],
) -> List[SnapshotDiff]:
    """Produce one SnapshotDiff per aggregated result."""
    diffs: List[SnapshotDiff] = []
    for r in results:
        entry = lookup_snapshot(snapshot, r.size)
        if entry is None or entry.mean is None or r.mean is None:
            diffs.append(SnapshotDiff(
                size=r.size,
                current_mean=r.mean,
                snapshot_mean=entry.mean if entry else None,
                delta_ms=None,
                delta_pct=None,
                regression=False,
            ))
            continue
        delta = r.mean - entry.mean
        diffs.append(SnapshotDiff(
            size=r.size,
            current_mean=r.mean,
            snapshot_mean=entry.mean,
            delta_ms=delta,
            delta_pct=_pct(r.mean, entry.mean),
            regression=delta > 0,
        ))
    return sorted(diffs, key=lambda d: d.size)
