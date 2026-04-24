"""CSV export for classified timing results."""
from __future__ import annotations

import csv
import io
from typing import List, Optional

from batchmark.classifier import ClassifiedResult


_FIELDS = ["size", "duration", "returncode", "classification"]


def classified_to_csv(classified: List[ClassifiedResult]) -> str:
    """Return CSV string for a list of ClassifiedResult objects."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_FIELDS)
    writer.writeheader()
    for cr in classified:
        writer.writerow({
            "size": cr.size,
            "duration": cr.duration if cr.duration is not None else "",
            "returncode": cr.result.returncode,
            "classification": cr.classification,
        })
    return buf.getvalue()


def classified_to_csv_file(
    classified: List[ClassifiedResult],
    path: str,
) -> None:
    """Write classified results to *path* as CSV."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(classified_to_csv(classified))
