"""Reporter for snapshot diff results."""

from __future__ import annotations

from typing import List

from batchmark.snapshot_comparator import SnapshotDiff

_COL = 14


def _fmt(v: object, width: int = _COL) -> str:
    return str(v).rjust(width)


def _fmt_ms(v: object) -> str:
    if v is None:
        return _fmt("N/A")
    return _fmt(f"{v:.2f} ms")


def _fmt_pct(v: object) -> str:
    if v is None:
        return _fmt("N/A")
    sign = "+" if v > 0 else ""
    return _fmt(f"{sign}{v:.1f}%")


def format_snapshot_header() -> str:
    cols = ["Size", "Current", "Snapshot", "Delta", "Delta%", "Status"]
    return "  ".join(c.rjust(_COL) for c in cols)


def format_snapshot_row(diff: SnapshotDiff) -> str:
    status = "REGRESS" if diff.regression else "OK"
    parts = [
        _fmt(diff.size),
        _fmt_ms(diff.current_mean),
        _fmt_ms(diff.snapshot_mean),
        _fmt_ms(diff.delta_ms),
        _fmt_pct(diff.delta_pct),
        _fmt(status),
    ]
    return "  ".join(parts)


def format_snapshot_summary(diffs: List[SnapshotDiff]) -> str:
    total = len(diffs)
    regressions = sum(1 for d in diffs if d.regression)
    return f"Snapshot diff: {total} sizes checked, {regressions} regression(s) detected."


def print_snapshot_report(diffs: List[SnapshotDiff]) -> None:
    print(format_snapshot_header())
    print("-" * (_COL * 6 + 10))
    for d in diffs:
        print(format_snapshot_row(d))
    print()
    print(format_snapshot_summary(diffs))
