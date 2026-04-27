"""stacker_reporter.py – tabular console output for stacked benchmark rows."""
from __future__ import annotations

from typing import List, Optional

from batchmark.stacker import StackedRow


_NA = "N/A"


def _fmt_ms(seconds: Optional[float]) -> str:
    if seconds is None:
        return _NA
    return f"{seconds * 1000:.2f} ms"


def _status(success: bool) -> str:
    return "OK" if success else "FAIL"


def format_stack_header() -> str:
    return f"{'Size':>8}  {'Label':<16}  {'Run':>4}  {'Status':<6}  {'Duration':>12}"


def format_stack_row(row: StackedRow) -> str:
    return (
        f"{row.size:>8}  "
        f"{row.label:<16}  "
        f"{row.run_index:>4}  "
        f"{_status(row.success):<6}  "
        f"{_fmt_ms(row.duration):>12}"
    )


def format_stack_summary_counts(rows: List[StackedRow]) -> str:
    total = len(rows)
    ok = sum(1 for r in rows if r.success)
    return f"Total: {total}  OK: {ok}  FAIL: {total - ok}"


def print_stack_report(rows: List[StackedRow]) -> None:
    print(format_stack_header())
    print("-" * 56)
    for row in rows:
        print(format_stack_row(row))
    print("-" * 56)
    print(format_stack_summary_counts(rows))
