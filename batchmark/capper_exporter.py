from __future__ import annotations

import csv
import io
from typing import List, Optional

from batchmark.capper import CappedResult


def _fmt(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:.4f}"


def capped_to_csv(results: List[CappedResult]) -> str:
    """Serialise a list of CappedResult objects to a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["size", "duration_ms", "success", "was_capped", "cap_limit_ms"])
    for r in results:
        writer.writerow([
            r.size,
            _fmt(r.duration()),
            int(r.success()),
            int(r.was_capped),
            _fmt(r.cap_limit_ms),
        ])
    return output.getvalue()


def capped_to_csv_file(results: List[CappedResult], path: str) -> None:
    """Write capped results as CSV to *path*."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(capped_to_csv(results))
