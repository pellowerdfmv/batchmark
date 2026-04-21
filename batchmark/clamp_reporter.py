"""Reporter for clamped/capped results showing original vs clamped duration."""

from typing import List
from batchmark.capper import CappedResult


def _fmt_ms(ms: float | None) -> str:
    if ms is None:
        return "N/A"
    return f"{ms:.2f}ms"


def _status(result: CappedResult) -> str:
    if not result.success:
        return "FAIL"
    if result.was_clamped:
        return "CLAMPED"
    return "OK"


def format_clamp_header() -> str:
    return f"{'Size':>10}  {'Original':>12}  {'Clamped':>12}  {'Cap':>12}  {'Status':>8}"


def format_clamp_row(result: CappedResult) -> str:
    original = _fmt_ms(result.original_duration)
    clamped = _fmt_ms(result.duration)
    cap = _fmt_ms(result.cap)
    status = _status(result)
    return f"{result.size:>10}  {original:>12}  {clamped:>12}  {cap:>12}  {status:>8}"


def format_clamp_summary(results: List[CappedResult]) -> str:
    total = len(results)
    clamped = sum(1 for r in results if r.was_clamped)
    failed = sum(1 for r in results if not r.success)
    lines = [
        f"Total:   {total}",
        f"Clamped: {clamped}",
        f"Failed:  {failed}",
    ]
    return "\n".join(lines)


def print_clamp_report(results: List[CappedResult]) -> None:
    print(format_clamp_header())
    print("-" * 60)
    for r in results:
        print(format_clamp_row(r))
    print("-" * 60)
    print(format_clamp_summary(results))
