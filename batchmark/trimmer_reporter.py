"""Reporter for trimmed results."""
from __future__ import annotations

from typing import List

from batchmark.trimmer import TrimmedResult, format_trim_summary


def _fmt_ms(value: float) -> str:
    return f"{value * 1000:.2f}ms"


def _status(r: TrimmedResult) -> str:
    if r.trimmed:
        return "TRIMMED"
    return "OK" if r.success else "FAIL"


def format_trim_header() -> str:
    return f"{'size':>8}  {'duration':>12}  {'status':<10}"


def format_trim_row(r: TrimmedResult) -> str:
    dur = _fmt_ms(r.duration) if not r.trimmed else "---"
    return f"{r.size:>8}  {dur:>12}  {_status(r):<10}"


def print_trim_report(results: List[TrimmedResult]) -> None:
    print(format_trim_header())
    print("-" * 36)
    for r in results:
        print(format_trim_row(r))
    print()
    print(format_trim_summary(results))
