"""Checkpoint support: save and resume partial benchmark runs."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class CheckpointEntry:
    size: int
    run_index: int
    duration: float
    returncode: int
    stdout: str
    stderr: str


def _entry_from_result(size: int, run_index: int, result: TimingResult) -> CheckpointEntry:
    return CheckpointEntry(
        size=size,
        run_index=run_index,
        duration=result.duration,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def _result_from_entry(entry: CheckpointEntry) -> TimingResult:
    return TimingResult(
        duration=entry.duration,
        returncode=entry.returncode,
        stdout=entry.stdout,
        stderr=entry.stderr,
    )


def save_checkpoint(path: str, entries: List[CheckpointEntry]) -> None:
    """Persist checkpoint entries to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([asdict(e) for e in entries], fh, indent=2)


def load_checkpoint(path: str) -> List[CheckpointEntry]:
    """Load checkpoint entries from a JSON file. Returns empty list if missing."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [CheckpointEntry(**item) for item in raw]


def already_run(entries: List[CheckpointEntry], size: int, run_index: int) -> bool:
    """Return True if (size, run_index) pair exists in checkpoint entries."""
    return any(e.size == size and e.run_index == run_index for e in entries)


def results_from_checkpoint(
    entries: List[CheckpointEntry], size: int
) -> List[TimingResult]:
    """Reconstruct TimingResult list for a given size from checkpoint entries."""
    matching = sorted(
        (e for e in entries if e.size == size), key=lambda e: e.run_index
    )
    return [_result_from_entry(e) for e in matching]


def append_entry(
    path: str,
    entries: List[CheckpointEntry],
    size: int,
    run_index: int,
    result: TimingResult,
) -> List[CheckpointEntry]:
    """Append a new entry and persist the updated list."""
    entry = _entry_from_result(size, run_index, result)
    entries = entries + [entry]
    save_checkpoint(path, entries)
    return entries
