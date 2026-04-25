"""binner_reporter.py — console formatting for BinnedResult / BinSummary."""
from __future__ import annotations

from typing import List, Sequence

from batchmark.binner import BinnedResult, BinSummary, summarize_bins

_COL_W = 14


def _fmt_ms(ms: float | None) -> str:
    if ms is None:
        return "N/A"
    return f"{ms:.2f} ms"


def _status(b: BinnedResult) -> str:
    return "OK" if b.success else "FAIL"


def format_bin_header() -> str:
    cols = ["Bin", "Size", "Duration (ms)", "Status"]
    return "  ".join(c.ljust(_COL_W) for c in cols)


def format_bin_row(b: BinnedResult) -> str:
    dur = f"{b.duration * 1000:.2f}" if b.success else "N/A"
    cols = [b.bin_label, str(b.size), dur, _status(b)]
    return "  ".join(c.ljust(_COL_W) for c in cols)


def format_bin_summary(summaries: Sequence[BinSummary]) -> str:
    lines = ["Bin Summary:", f"  {'Bin':<16} {'Count':>6} {'OK':>6} {'Mean':>12}"]
    for s in summaries:
        lines.append(
            f"  {s.label:<16} {s.count:>6} {s.successful:>6} {_fmt_ms(s.mean_ms):>12}"
        )
    return "\n".join(lines)


def print_bin_report(binned: Sequence[BinnedResult]) -> None:
    print(format_bin_header())
    for b in binned:
        print(format_bin_row(b))
    summaries = summarize_bins(binned)
    print()
    print(format_bin_summary(summaries))
