"""Reporter for displaying baseline comparison results in the terminal."""

from __future__ import annotations

from typing import List, Optional

from batchmark.baseline import BaselineEntry, lookup_baseline

_HEADER_FMT = "{:<10}  {:>12}  {:>12}  {:>10}  {:>8}"
_ROW_FMT = "{:<10}  {:>12.2f}  {:>12}  {:>+10.1f}  {:>8}"


def format_baseline_header() -> str:
    return _HEADER_FMT.", "CURRENT ms", "BASELINE ms", "DELTA ms", "RATIO")


def format_baseline_row(
    size: int,
    current_ms: float,
    baseline: Optional[BaselineEntry],
) -> str:
    if baseline is None:
        return _HEADER_FMT.format(size, f"{current_ms:.2f}", "n/a", "n/an    delta = current_ms - baseline.mean_ms
    ratio = current_ms / baseline.mean_ms if baseline.mean_ms > 0 else float("inf")
    return _ROW_FMT.format(size, current_ms, f"{baseline.mean_ms:.2f}", delta, f"{ratio:.3f}x")


def format_baseline_summary(
    current_entries: List[BaselineEntry],
    baseline_entries: List[BaselineEntry],
) -> str:
    faster = slower = unchanged = missing = 0
    for entry in current_entries:
        ref = lookup_baseline(baseline_entries, entry.size)
        if ref is None:
            missing += 1
            continue
        delta = entry.mean_ms - ref.mean_ms
        if abs(delta) < 0.5:
            unchanged += 1
        elif delta < 0:
            faster += 1
        else:
            slower += 1
    parts = [f"faster={faster}", f"slower={slower}", f"unchanged={unchanged}"]
    if missing:
        parts.append(f"no-baseline={missing}")
    return "  ".join(parts)


def print_baseline_report(
    current_entries: List[BaselineEntry],
    baseline_entries: List[BaselineEntry],
) -> None:
    print(format_baseline_header())
    print("-" * 60)
    for entry in current_entries:
        ref = lookup_baseline(baseline_entries, entry.size)
        print(format_baseline_row(entry.size, entry.mean_ms, ref))
    print("-" * 60)
    print(format_baseline_summary(current_entries, baseline_entries))
