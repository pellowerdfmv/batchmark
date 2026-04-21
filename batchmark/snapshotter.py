"""Snapshot module: capture and compare aggregated results over time."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional

from batchmark.aggregator import AggregatedResult


@dataclass
class SnapshotEntry:
    size: int
    mean: Optional[float]
    median: Optional[float]
    stdev: Optional[float]
    min_duration: Optional[float]
    max_duration: Optional[float]
    runs: int
    successful: int


def snapshot_from_aggregated(results: List[AggregatedResult]) -> List[SnapshotEntry]:
    """Convert aggregated results into snapshot entries."""
    entries = []
    for r in results:
        entries.append(SnapshotEntry(
            size=r.size,
            mean=r.mean,
            median=r.median,
            stdev=r.stdev,
            min_duration=r.min_duration,
            max_duration=r.max_duration,
            runs=r.runs,
            successful=r.successful,
        ))
    return entries


def save_snapshot(entries: List[SnapshotEntry], path: str) -> None:
    """Persist snapshot entries to a JSON file."""
    data = [asdict(e) for e in entries]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_snapshot(path: str) -> List[SnapshotEntry]:
    """Load snapshot entries from a JSON file."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return [SnapshotEntry(**d) for d in data]


def lookup_snapshot(entries: List[SnapshotEntry], size: int) -> Optional[SnapshotEntry]:
    """Return the snapshot entry for a given size, or None."""
    for e in entries:
        if e.size == size:
            return e
    return None
