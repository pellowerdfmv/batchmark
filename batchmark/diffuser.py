"""diffuser.py — compute per-size diffs between two labeled result sets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from batchmark.timer import TimingResult
from batchmark.stats import mean


@dataclass(frozen=True)
class DiffEntry:
    size: int
    label_a: str
    label_b: str
    mean_a: Optional[float]   # ms, None when no successful runs
    mean_b: Optional[float]   # ms, None when no successful runs
    delta: Optional[float]    # mean_b - mean_a  (ms)
    pct: Optional[float]      # delta / mean_a * 100


def _mean_ms(results: Sequence[TimingResult]) -> Optional[float]:
    """Return mean duration in ms for successful results, or None."""
    durations = [r.duration * 1000 for r in results if r.returncode == 0]
    if not durations:
        return None
    return sum(durations) / len(durations)


@dataclass(frozen=True)
class DiffConfig:
    label_a: str = "A"
    label_b: str = "B"


def diff_results(
    results_a: Sequence[TimingResult],
    results_b: Sequence[TimingResult],
    config: Optional[DiffConfig] = None,
) -> List[DiffEntry]:
    """Compute per-size mean diff between two result sets.

    Results are matched by *size*.  Sizes present in only one set still
    produce a row; the missing side's mean will be ``None``.
    """
    if config is None:
        config = DiffConfig()

    by_size_a: dict[int, list[TimingResult]] = {}
    for r in results_a:
        by_size_a.setdefault(r.size, []).append(r)

    by_size_b: dict[int, list[TimingResult]] = {}
    for r in results_b:
        by_size_b.setdefault(r.size, []).append(r)

    all_sizes = sorted(set(by_size_a) | set(by_size_b))

    entries: List[DiffEntry] = []
    for size in all_sizes:
        ma = _mean_ms(by_size_a.get(size, []))
        mb = _mean_ms(by_size_b.get(size, []))

        if ma is not None and mb is not None:
            delta: Optional[float] = mb - ma
            pct: Optional[float] = (delta / ma * 100) if ma != 0 else None
        else:
            delta = None
            pct = None

        entries.append(
            DiffEntry(
                size=size,
                label_a=config.label_a,
                label_b=config.label_b,
                mean_a=ma,
                mean_b=mb,
                delta=delta,
                pct=pct,
            )
        )

    return entries


def format_diff_summary(entries: List[DiffEntry]) -> str:
    """Return a one-line human-readable summary of the diff."""
    regressions = [e for e in entries if e.pct is not None and e.pct > 0]
    improvements = [e for e in entries if e.pct is not None and e.pct < 0]
    return (
        f"{len(entries)} size(s) compared — "
        f"{len(regressions)} slower, {len(improvements)} faster"
    )
