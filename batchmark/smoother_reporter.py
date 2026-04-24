"""Reporter for smoothed results."""

from __future__ import annotations

from typing import List

from batchmark.smoother import SmoothedResult


def _fmt_ms(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value * 1000:.2f}ms"


def _status(sr: SmoothedResult) -> str:
    return "OK" if sr.success else "FAIL"


def format_smooth_header() -> str:
    return f"{'Size':>8}  {'Status':>6}  {'Raw':>12}  {'Smoothed':>12}"


def format_smooth_row(sr: SmoothedResult) -> str:
    return (
        f"{sr.size:>8}  "
        f"{_status(sr):>6}  "
        f"{_fmt_ms(sr.duration):>12}  "
        f"{_fmt_ms(sr.smoothed_duration):>12}"
    )


def format_smooth_summary(smoothed: List[SmoothedResult]) -> str:
    total = len(smoothed)
    computed = sum(1 for s in smoothed if s.smoothed_duration is not None)
    window = smoothed[0].window_size if smoothed else 0
    return f"{computed}/{total} smoothed values computed (window={window})"


def print_smooth_report(smoothed: List[SmoothedResult]) -> None:
    print(format_smooth_header())
    for sr in smoothed:
        print(format_smooth_row(sr))
    print()
    print(format_smooth_summary(smoothed))
