"""CSV export for capped results."""

from __future__ import annotations

import csv
import io
from typing import List

from batchmark.capper import CappedResult


def _fmt(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def capped_to_csv(results: List[CappedResult]) -> str:
    """Serialise capped results to a CSV string."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["size", "duration_ms", "success", "was_capped", "original_duration_ms"])
    for r in results:
        writer.writerow([
            r.size,
            _fmt(r.duration),
            int(r.success),
            int(r.was_capped),
            _fmt(r.original_duration),
        ])
    return buf.getvalue()


def capped_to_csv_file(results: List[CappedResult], path: str) -> None:
    """Write capped results as CSV to *path*."""
    with open(path, "w", newline="") as fh:
        fh.write(capped_to_csv(results))
