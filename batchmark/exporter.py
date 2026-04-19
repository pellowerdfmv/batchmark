"""Export TimingResults or AggregatedResults to CSV."""

import csv
import io
from typing import List, Union

from batchmark.timer import TimingResult


def results_to_csv(results: List[TimingResult], file=None) -> str:
    """Serialise a list of TimingResult to CSV.

    If *file* is given the CSV is written there; the raw string is always
    returned.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["size", "duration", "returncode", "stdout", "stderr"])
    for r in results:
        writer.writerow([r.size, r.duration, r.returncode, r.stdout, r.stderr])
    content = buf.getvalue()
    if file is not None:
        if isinstance(file, str):
            with open(file, "w", newline="") as fh:
                fh.write(content)
        else:
            file.write(content)
    return content


def aggregated_to_csv(rows, file=None) -> str:
    """Serialise a list of AggregatedResult to CSV."""
    from batchmark.aggregator import AggregatedResult  # local to avoid circular

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["size", "runs", "successful", "mean", "median", "stdev", "min", "max"])
    for r in rows:
        writer.writerow([r.size, r.runs, r.successful,
                         round(r.mean, 6), round(r.median, 6),
                         round(r.stdev, 6), round(r.min, 6), round(r.max, 6)])
    content = buf.getvalue()
    if file is not None:
        if isinstance(file, str):
            with open(file, "w", newline="") as fh:
                fh.write(content)
        else:
            file.write(content)
    return content
