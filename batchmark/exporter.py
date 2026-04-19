"""CSV export for benchmark timing results."""

import csv
import io
from pathlib import Path
from typing import List, Union

from batchmark.timer import TimingResult

FIELDS = ["command", "input_size", "elapsed_seconds", "returncode", "success"]


def results_to_csv(results: List[TimingResult], dest: Union[str, Path, None] = None) -> str:
    """Serialize results to CSV. Writes to *dest* if provided, returns CSV string."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    for r in results:
        writer.writerow({
            "command": r.command,
            "input_size": r.input_size,
            "elapsed_seconds": round(r.elapsed_seconds, 6),
            "returncode": r.returncode,
            "success": r.success,
        })
    csv_str = output.getvalue()
    if dest is not None:
        Path(dest).write_text(csv_str, encoding="utf-8")
    return csv_str
