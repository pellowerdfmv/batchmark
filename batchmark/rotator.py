"""rotator.py – round-robin rotation of result sets across named slots.

Useful when you want to cycle benchmark results through a fixed number of
named slots (e.g. 'run-1', 'run-2', 'run-3') and track which slot each
result occupies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from batchmark.timer import TimingResult


@dataclass
class RotatedResult:
    result: TimingResult
    slot: str
    slot_index: int

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
class RotatorConfig:
    slots: List[str] = field(default_factory=lambda: ["run-1", "run-2", "run-3"])

    def __post_init__(self) -> None:
        if not self.slots:
            raise ValueError("RotatorConfig requires at least one slot.")


def rotate_results(
    results: Sequence[TimingResult],
    config: Optional[RotatorConfig] = None,
) -> List[RotatedResult]:
    """Assign each result to a slot in round-robin order."""
    cfg = config or RotatorConfig()
    n = len(cfg.slots)
    rotated: List[RotatedResult] = []
    for i, result in enumerate(results):
        slot_index = i % n
        rotated.append(
            RotatedResult(
                result=result,
                slot=cfg.slots[slot_index],
                slot_index=slot_index,
            )
        )
    return rotated


def format_rotate_summary(rotated: Sequence[RotatedResult]) -> str:
    """Return a one-line summary of how many results landed in each slot."""
    if not rotated:
        return "No results to rotate."
    counts: dict[str, int] = {}
    for r in rotated:
        counts[r.slot] = counts.get(r.slot, 0) + 1
    parts = ", ".join(f"{slot}: {cnt}" for slot, cnt in counts.items())
    return f"Rotation summary – {parts}"
