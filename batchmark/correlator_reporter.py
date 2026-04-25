"""Reporter for correlation results."""
from __future__ import annotations

from typing import List

from batchmark.correlator import CorrelationResult

_COL_WIDTH = 14


def _fmt(val: object, width: int = _COL_WIDTH) -> str:
    return str(val).rjust(width)


def format_correlation_header() -> str:
    cols = ["Size", "Mean (ms)", "Variable", "Pearson r"]
    return "  ".join(c.rjust(_COL_WIDTH) for c in cols)


def format_correlation_row(row: CorrelationResult) -> str:
    mean_str = f"{row.mean_ms:.3f}" if row.mean_ms is not None else "N/A"
    var_str = f"{row.variable:.4f}" if row.variable is not None else "N/A"
    r_str = f"{row.pearson_r:.4f}" if row.pearson_r is not None else "N/A"
    parts = [str(row.size), mean_str, var_str, r_str]
    return "  ".join(p.rjust(_COL_WIDTH) for p in parts)


def print_correlation_report(rows: List[CorrelationResult]) -> None:
    print(format_correlation_header())
    print("-" * (_COL_WIDTH * 4 + 6))
    for row in rows:
        print(format_correlation_row(row))
    if rows:
        r_val = rows[0].pearson_r
        r_str = f"{r_val:.4f}" if r_val is not None else "N/A"
        print(f"\nPearson r = {r_str}")
