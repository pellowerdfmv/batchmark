"""CSV export for outlier detection results."""

import csv
import io
from typing import List, Optional
from batchmark.outlier import OutlierResult


def _fmt(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def outlier_results_to_csv(results: List[OutlierResult]) -> str:
    """Serialize outlier results to a CSV string."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["size", "duration", "success", "is_outlier", "lower_fence", "upper_fence"])
    for r in results:
        writer.writerow([
            r.size,
            _fmt(r.duration),
            str(r.success).lower(),
            str(r.is_outlier).lower(),
            _fmt(r.lower_fence),
            _fmt(r.upper_fence),
        ])
    return buf.getvalue()


def outlier_results_to_csv_file(results: List[OutlierResult], path: str) -> None:
    """Write outlier results CSV to a file."""
    content = outlier_results_to_csv(results)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(content)
