"""Baseline management: save and load reference timing results for comparison."""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class BaselineEntry:
    size: int
    mean_ms: float
    runs: int


def save_baseline(entries: List[BaselineEntry], path: str) -> None:
    """Write baseline entries to a CSV file."""
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["size", "mean_ms", "runs"])
        for e in entries:
            writer.writerow([e.size, f"{e.mean_ms:.4f}", e.runs])


def load_baseline(path: str) -> List[BaselineEntry]:
    """Read baseline entries from a CSV file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Baseline file not found: {path}")
    entries: List[BaselineEntry] = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            entries.append(
                BaselineEntry(
                    size=int(row["size"]),
                    mean_ms=float(row["mean_ms"]),
                    runs=int(row["runs"]),
                )
            )
    return entries


def baseline_from_results(
    results: List[TimingResult],
) -> List[BaselineEntry]:
    """Compute baseline entries from a list of TimingResult objects."""
    groups: Dict[int, List[float]] = {}
    for r in results:
        if r.returncode == 0:
            groups.setdefault(r.size, []).append(r.duration_ms)
    entries: List[BaselineEntry] = []
    for size, durations in sorted(groups.items()):
        mean_ms = sum(durations) / len(durations)
        entries.append(BaselineEntry(size=size, mean_ms=mean_ms, runs=len(durations)))
    return entries


def lookup_baseline(
    entries: List[BaselineEntry], size: int
) -> Optional[BaselineEntry]:
    """Return the baseline entry for a given size, or None."""
    for e in entries:
        if e.size == size:
            return e
    return None
