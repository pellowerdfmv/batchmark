"""Console reporter for WindowResult lists."""

from __future__ import annotations

from typing import List, Optional

from batchmark.windower import WindowResult

_COL_W = 8


def _fmt_ms(value: Optional[float]) -> str:
    return f"{value:.1f}" if value is not None else "N/A"


def format_window_header() -> str:
    cols = ["WIN", "SIZES", "COUNT", "OK", "MEAN(ms)", "STDEV(ms)", "MIN(ms)", "MAX(ms)"]
    return "  ".join(c.ljust(_COL_W) for c in cols)


def format_window_row(w: WindowResult) -> str:
    sizes_str = "|".join(str(s) for s in w.sizes)
    cols = [
        str(w.window_index).ljust(_COL_W),
        sizes_str.ljust(_COL_W),
        str(w.count).ljust(_COL_W),
        str(w.successful).ljust(_COL_W),
        _fmt_ms(w.mean_ms).ljust(_COL_W),
        _fmt_ms(w.stdev_ms).ljust(_COL_W),
        _fmt_ms(w.min_ms).ljust(_COL_W),
        _fmt_ms(w.max_ms).ljust(_COL_W),
    ]
    return "  ".join(cols)


def format_window_summary(windows: List[WindowResult]) -> str:
    total = len(windows)
    if total == 0:
        return "No windows."
    total_ok = sum(w.successful for w in windows)
    total_runs = sum(w.count for w in windows)
    valid_means = [w.mean_ms for w in windows if w.mean_ms is not None]
    overall = f"{sum(valid_means) / len(valid_means):.1f} ms" if valid_means else "N/A"
    return (
        f"Windows: {total}  total runs: {total_runs}  "
        f"successful: {total_ok}  avg window mean: {overall}"
    )


def print_window_report(windows: List[WindowResult]) -> None:
    print(format_window_header())
    print("-" * 72)
    for w in windows:
        print(format_window_row(w))
    print("-" * 72)
    print(format_window_summary(windows))
