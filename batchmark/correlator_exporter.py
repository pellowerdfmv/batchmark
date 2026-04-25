"""CSV export for correlation results."""
from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import List

from batchmark.correlator import CorrelationResult

_HEADERS = ["size", "mean_ms", "variable", "pearson_r"]


def correlation_to_csv(rows: List[CorrelationResult]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_HEADERS)
    for row in rows:
        writer.writerow([
            row.size,
            f"{row.mean_ms:.6f}" if row.mean_ms is not None else "",
            f"{row.variable:.6f}" if row.variable is not None else "",
            f"{row.pearson_r:.6f}" if row.pearson_r is not None else "",
        ])
    return buf.getvalue()


def correlation_to_csv_file(rows: List[CorrelationResult], path: str | Path) -> None:
    Path(path).write_text(correlation_to_csv(rows), encoding="utf-8")
