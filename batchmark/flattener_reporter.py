"""Reporter for flattened results."""

from __future__ import annotations

from typing import List

from batchmark.flattener import FlattenedResult, format_flatten_summary

_COL_WIDTH = 12


def _fmt_ms(value: float) -> str:
    return f"{value * 1000:.2f} ms"


def _status(result: FlattenedResult) -> str:
    return "OK" if result.success else "FAIL"


def format_flatten_header() -> str:
    cols = ["Index", "Source", "Size", "Duration", "Status"]
    return "  ".join(c.ljust(_COL_WIDTH) for c in cols)


def format_flatten_row(result: FlattenedResult) -> str:
    cols = [
        str(result.flat_index).ljust(_COL_WIDTH),
        result.source_label.ljust(_COL_WIDTH),
        str(result.size).ljust(_COL_WIDTH),
        _fmt_ms(result.duration).ljust(_COL_WIDTH),
        _status(result).ljust(_COL_WIDTH),
    ]
    return "  ".join(cols)


def print_flatten_report(
    results: List[FlattenedResult],
    *,
    show_summary: bool = True,
) -> None:
    print(format_flatten_header())
    print("-" * (_COL_WIDTH * 5 + 8))
    for r in results:
        print(format_flatten_row(r))
    if show_summary:
        print()
        print(format_flatten_summary(results))
