"""clumper.py — group consecutive results into fixed-size clumps and compute per-clump stats."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from batchmark.timer import TimingResult


@dataclass
class ClumpResult:
    clump_index: int
    sizes: List[int]
    results: List[TimingResult]
    mean_ms: Optional[float]
    min_ms: Optional[float]
    max_ms: Optional[float]
    success_count: int
    total_count: int


@dataclass
class ClumperConfig:
    clump_size: int = 5


def _durations(results: Sequence[TimingResult]) -> List[float]:
    return [r.duration_ms for r in results if r.returncode == 0]


def clump_results(
    results: Sequence[TimingResult],
    config: Optional[ClumperConfig] = None,
) -> List[ClumpResult]:
    """Partition *results* into consecutive clumps and return per-clump stats."""
    if config is None:
        config = ClumperConfig()

    clump_size = max(1, config.clump_size)
    clumps: List[ClumpResult] = []

    for idx in range(0, len(results), clump_size):
        chunk = list(results[idx : idx + clump_size])
        durations = _durations(chunk)
        mean_ms: Optional[float] = sum(durations) / len(durations) if durations else None
        min_ms: Optional[float] = min(durations) if durations else None
        max_ms: Optional[float] = max(durations) if durations else None
        clumps.append(
            ClumpResult(
                clump_index=idx // clump_size,
                sizes=[r.size for r in chunk],
                results=chunk,
                mean_ms=mean_ms,
                min_ms=min_ms,
                max_ms=max_ms,
                success_count=len(durations),
                total_count=len(chunk),
            )
        )
    return clumps


def format_clump_summary(clumps: List[ClumpResult]) -> str:
    """Return a human-readable summary of all clumps."""
    lines = [f"{'Clump':>6}  {'Count':>5}  {'OK':>4}  {'Mean ms':>10}  {'Min ms':>10}  {'Max ms':>10}"]
    for c in clumps:
        mean = f"{c.mean_ms:10.2f}" if c.mean_ms is not None else "        N/A"
        mn = f"{c.min_ms:10.2f}" if c.min_ms is not None else "        N/A"
        mx = f"{c.max_ms:10.2f}" if c.max_ms is not None else "        N/A"
        lines.append(f"{c.clump_index:>6}  {c.total_count:>5}  {c.success_count:>4}  {mean}  {mn}  {mx}")
    return "\n".join(lines)
