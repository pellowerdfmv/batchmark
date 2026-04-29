"""CSV export for trimmed results."""
from __future__ import annotations

import csv
import io
from typing import List, Optional

from batchmark.trimmer import TrimmedResult


def _fmt(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def trimmed_to_csv(results: List[TrimmedResult]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["size", "duration_s", "success", "trimmed"])
    for r in results:
        writer.writerow([
            r.size,
            _fmt(r.duration),
            str(r.success),
            str(r.trimmed),
        ])
    return buf.getvalue()


def trimmed_to_csv_file(results: List[TrimmedResult], path: str) -> None:
    with open(path, "w", newline="") as fh:
        fh.write(trimmed_to_csv(results))
