"""CSV export utilities for capped results."""

from __future__ import annotations

import csv
import io
from typing import List

from batchmark.capper import CappedResult


_HEADER = ["size", "duration_ms", "capped_duration_ms", "was_capped", "success"]


def _fmt(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value * 1000:.3f}"


def capped_to_csv(results: List[CappedResult]) -> str:
    """Serialise capped results to a CSV string."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_HEADER)
    for r in results:
        writer.writerow([
            r.size,
            _fmt(r.duration),
            _fmt(r.capped_duration),
            r.was_capped,
            r.success,
        ])
    return buf.getvalue()


def capped_to_csv_file(results: List[CappedResult], path: str) -> None:
    """Write capped results to *path* as CSV."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(capped_to_csv(results))
