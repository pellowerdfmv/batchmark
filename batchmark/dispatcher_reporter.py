"""Reporter for dispatched results."""

from __future__ import annotations

from typing import List

from batchmark.dispatcher import DispatchedResult, group_by_handler


def _fmt_ms(value: float) -> str:
    return f"{value * 1000:.2f} ms"


def _status(dr: DispatchedResult) -> str:
    return "OK" if dr.success else "FAIL"


def format_dispatch_header() -> str:
    return f"{'Size':>8}  {'Handler':<20}  {'Duration':>12}  {'Status':<6}"


def format_dispatch_row(dr: DispatchedResult) -> str:
    dur = _fmt_ms(dr.duration) if dr.duration is not None else "N/A"
    return f"{dr.size:>8}  {dr.handler:<20}  {dur:>12}  {_status(dr):<6}"


def format_dispatch_summary_table(dispatched: List[DispatchedResult]) -> str:
    groups = group_by_handler(dispatched)
    lines = ["Handler Summary:", f"  {'Handler':<20}  {'Count':>6}  {'OK':>6}  {'FAIL':>6}"]
    for name, items in sorted(groups.items()):
        ok = sum(1 for d in items if d.success)
        fail = len(items) - ok
        lines.append(f"  {name:<20}  {len(items):>6}  {ok:>6}  {fail:>6}")
    return "\n".join(lines)


def print_dispatch_report(dispatched: List[DispatchedResult]) -> None:
    print(format_dispatch_header())
    for dr in dispatched:
        print(format_dispatch_row(dr))
    print()
    print(format_dispatch_summary_table(dispatched))
