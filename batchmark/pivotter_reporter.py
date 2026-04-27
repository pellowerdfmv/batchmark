"""Console reporter for pivot tables."""

from __future__ import annotations

from typing import Optional

from batchmark.pivotter import PivotTable


def _fmt_ms(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}ms"


def format_pivot_header(table: PivotTable) -> str:
    """Return a formatted header line for the pivot table."""
    metric_cols = "  ".join(f"{m:>12}" for m in table.metrics)
    return f"{'size':>8}  {metric_cols}"


def format_pivot_row(table: PivotTable, row_index: int) -> str:
    """Return a formatted row for the given index."""
    row = table.rows[row_index]
    metric_cols = "  ".join(
        f"{_fmt_ms(row.values.get(m)):>12}" for m in table.metrics
    )
    return f"{row.size:>8}  {metric_cols}"


def print_pivot_report(table: PivotTable) -> None:
    """Print a full pivot table report to stdout."""
    print(format_pivot_header(table))
    print("-" * (10 + 14 * len(table.metrics)))
    for i in range(len(table.rows)):
        print(format_pivot_row(table, i))
    print()
    print(
        f"Sizes: {len(table.rows)}  "
        f"Metrics: {', '.join(table.metrics)}"
    )
