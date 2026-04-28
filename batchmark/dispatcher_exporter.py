"""CSV export for dispatched results."""

from __future__ import annotations

import csv
import io
from typing import List, Optional

from batchmark.dispatcher import DispatchedResult


def dispatched_to_csv(dispatched: List[DispatchedResult]) -> str:
    """Return CSV text for *dispatched* results."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["size", "handler", "duration_s", "returncode", "success"])
    for dr in dispatched:
        writer.writerow([
            dr.size,
            dr.handler,
            f"{dr.duration:.6f}" if dr.duration is not None else "",
            dr.result.returncode,
            int(dr.success),
        ])
    return buf.getvalue()


def dispatched_to_csv_file(
    dispatched: List[DispatchedResult],
    path: str,
) -> None:
    """Write CSV for *dispatched* results to *path*."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(dispatched_to_csv(dispatched))
