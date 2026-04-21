"""CSV export for matrix results."""

import csv
import io
from typing import List, Optional

from batchmark.matrix import MatrixCell


_FIELDS = ["size", "variant", "duration_s", "returncode", "stdout", "stderr"]


def matrix_to_csv(cells: List[MatrixCell], path: Optional[str] = None) -> str:
    """Serialise matrix cells to CSV.  Returns the CSV string."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_FIELDS, lineterminator="\n")
    writer.writeheader()
    for cell in cells:
        r = cell.result
        writer.writerow(
            {
                "size": cell.size,
                "variant": cell.variant,
                "duration_s": f"{r.duration:.6f}" if r.duration is not None else "",
                "returncode": r.returncode,
                "stdout": (r.stdout or "").strip(),
                "stderr": (r.stderr or "").strip(),
            }
        )
    csv_text = buf.getvalue()
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(csv_text)
    return csv_text
