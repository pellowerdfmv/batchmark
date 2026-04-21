"""Export sparkline plot data to CSV for external graphing tools."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import List, Optional, Union

from batchmark.aggregator import AggregatedResult


_HEADERS = ["size", "mean_ms", "min_ms", "max_ms", "successful", "total"]


def _fmt(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:.4f}"


def plot_data_to_csv(results: List[AggregatedResult]) -> str:
    """Serialise aggregated results to a CSV string suitable for plotting."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_HEADERS)
    for r in sorted(results, key=lambda x: x.size):
        writer.writerow([
            r.size,
            _fmt(r.mean_ms),
            _fmt(r.min_ms),
            _fmt(r.max_ms),
            r.successful,
            r.total,
        ])
    return buf.getvalue()


def plot_data_to_csv_file(
    results: List[AggregatedResult],
    path: Union[str, Path],
) -> None:
    """Write aggregated plot data as CSV to *path*."""
    Path(path).write_text(plot_data_to_csv(results), encoding="utf-8")


def plot_data_from_csv(text: str) -> List[dict]:
    """Parse CSV text produced by :func:`plot_data_to_csv` into plain dicts.

    Useful for reading back exported data without reconstructing full
    ``AggregatedResult`` objects.
    """
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        rows.append({
            "size": int(row["size"]),
            "mean_ms": float(row["mean_ms"]) if row["mean_ms"] else None,
            "min_ms": float(row["min_ms"]) if row["min_ms"] else None,
            "max_ms": float(row["max_ms"]) if row["max_ms"] else None,
            "successful": int(row["successful"]),
            "total": int(row["total"]),
        })
    return rows
