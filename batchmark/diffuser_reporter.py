"""diffuser_reporter.py — human-readable table for DiffEntry results."""
from __future__ import annotations

from typing import List

from batchmark.diffuser import DiffEntry


def _fmt_ms(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f} ms"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def _direction(pct: float | None) -> str:
    if pct is None:
        return "?"
    if pct > 5:
        return "▲ slower"
    if pct < -5:
        return "▼ faster"
    return "≈ same"


def format_diff_header(entry: DiffEntry) -> str:
    a, b = entry.label_a, entry.label_b
    return f"{'size':>8}  {'mean_' + a:>12}  {'mean_' + b:>12}  {'delta':>12}  {'change%':>10}  direction"


def format_diff_row(entry: DiffEntry) -> str:
    return (
        f"{entry.size:>8}  "
        f"{_fmt_ms(entry.mean_a):>12}  "
        f"{_fmt_ms(entry.mean_b):>12}  "
        f"{_fmt_ms(entry.delta):>12}  "
        f"{_fmt_pct(entry.pct):>10}  "
        f"{_direction(entry.pct)}"
    )


def print_diff_report(entries: List[DiffEntry]) -> None:
    if not entries:
        print("No diff entries to display.")
        return
    print(format_diff_header(entries[0]))
    print("-" * 74)
    for entry in entries:
        print(format_diff_row(entry))
    regressions = sum(1 for e in entries if e.pct is not None and e.pct > 5)
    improvements = sum(1 for e in entries if e.pct is not None and e.pct < -5)
    print("-" * 74)
    print(f"Summary: {len(entries)} size(s), {regressions} slower, {improvements} faster")
