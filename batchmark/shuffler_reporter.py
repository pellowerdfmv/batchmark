"""Reporter for shuffled benchmark results."""

from __future__ import annotations

from typing import List

from batchmark.shuffler import ShuffledResult, format_shuffle_summary


_COLUMNS = ["orig_idx", "new_idx", "size", "duration_ms", "status"]


def _fmt_ms(value: float) -> str:
    return f"{value * 1000:.2f}"


def _status(s: ShuffledResult) -> str:
    return "ok" if s.success else "FAIL"


def format_shuffle_header() -> str:
    return "  ".join(f"{c:<12}" for c in _COLUMNS)


def format_shuffle_row(s: ShuffledResult) -> str:
    moved = "*" if s.original_index != s.shuffled_index else " "
    fields = [
        f"{s.original_index:<12}",
        f"{s.shuffled_index:<12}",
        f"{s.size:<12}",
        f"{_fmt_ms(s.duration):<12}",
        f"{_status(s):<12}",
    ]
    return moved + "  ".join(fields)


def print_shuffle_report(
    shuffled: List[ShuffledResult],
    *,
    show_summary: bool = True,
) -> List[ShuffledResult]:
    print(format_shuffle_header())
    for s in shuffled:
        print(format_shuffle_row(s))
    if show_summary:
        print(format_shuffle_summary(shuffled))
    return shuffled
