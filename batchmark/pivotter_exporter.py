"""CSV export for pivot tables."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Optional

from batchmark.pivotter import PivotTable


def _fmt(value: Optional[float]) -> str:
    return "" if value is None else f"{value:.6f}"


def pivot_to_csv(table: PivotTable) -> str:
    """Serialise a PivotTable to a CSV string."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["size"] + table.metrics)
    for row in table.rows:
        writer.writerow(
            [str(row.size)] + [_fmt(row.values.get(m)) for m in table.metrics]
        )
    return buf.getvalue()


def pivot_to_csv_file(table: PivotTable, path: str | Path) -> None:
    """Write a PivotTable to a CSV file."""
    Path(path).write_text(pivot_to_csv(table), encoding="utf-8")
