"""Formatting helpers for ProfiledResult collections."""

from __future__ import annotations

from typing import List

from batchmark.profiler import ProfiledResult

_COL_WIDTH = 14


def format_profile_header() -> str:
    cols = ["command", "size", "duration_s", "max_rss_kb", "user_s", "sys_s", "status"]
    return "  ".join(c.ljust(_COL_WIDTH) for c in cols).rstrip()


def format_profile_row(r: ProfiledResult) -> str:
    status = "OK" if r.success else "FAIL"
    cols = [
        r.timing.command[:_COL_WIDTH].ljust(_COL_WIDTH),
        str(r.timing.size).ljust(_COL_WIDTH),
        f"{r.timing.duration:.4f}".ljust(_COL_WIDTH),
        str(r.max_rss_kb).ljust(_COL_WIDTH),
        f"{r.user_time_s:.4f}".ljust(_COL_WIDTH),
        f"{r.sys_time_s:.4f}".ljust(_COL_WIDTH),
        status.ljust(_COL_WIDTH),
    ]
    return "  ".join(cols).rstrip()


def format_profile_summary(results: List[ProfiledResult]) -> str:
    if not results:
        return "No profiled results."
    total = len(results)
    ok = sum(1 for r in results if r.success)
    avg_rss = sum(r.max_rss_kb for r in results) / total
    avg_dur = sum(r.timing.duration for r in results) / total
    return (
        f"Runs: {total}  OK: {ok}  FAIL: {total - ok}  "
        f"Avg duration: {avg_dur:.4f}s  Avg RSS: {avg_rss:.1f} KB"
    )


def print_profile_results(results: List[ProfiledResult]) -> None:
    print(format_profile_header())
    print("-" * 100)
    for r in results:
        print(format_profile_row(r))
    print("-" * 100)
    print(format_profile_summary(results))
