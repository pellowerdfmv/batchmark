from __future__ import annotations

from typing import List

from batchmark.capper import CappedResult


def _fmt_ms(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value * 1000:.2f}ms"


def _status(result: CappedResult) -> str:
    if not result.success:
        return "FAIL"
    if result.capped:
        return "CAPPED"
    return "OK"


def format_cap_header() -> str:
    return f"{'Size':>10}  {'Duration':>12}  {'Original':>12}  {'Cap':>12}  {'Status':>8}"


def format_cap_row(result: CappedResult) -> str:
    cap_str = _fmt_ms(result.cap_limit) if result.cap_limit is not None else "none"
    return (
        f"{result.size:>10}  "
        f"{_fmt_ms(result.duration):>12}  "
        f"{_fmt_ms(result.original_duration):>12}  "
        f"{cap_str:>12}  "
        f"{_status(result):>8}"
    )


def format_cap_summary(results: List[CappedResult]) -> str:
    total = len(results)
    capped = sum(1 for r in results if r.capped)
    failed = sum(1 for r in results if not r.success)
    lines = [
        f"Total : {total}",
        f"Capped: {capped}",
        f"Failed: {failed}",
    ]
    return "\n".join(lines)


def print_cap_report(results: List[CappedResult]) -> None:
    print(format_cap_header())
    for r in results:
        print(format_cap_row(r))
    print()
    print(format_cap_summary(results))
