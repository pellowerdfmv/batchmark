"""binner_exporter.py — CSV export for binned results and bin summaries."""
from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Sequence

from batchmark.binner import BinnedResult, BinSummary


def binned_to_csv(binned: Sequence[BinnedResult]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["bin", "size", "duration_ms", "returncode", "success"])
    for b in binned:
        dur = f"{b.duration * 1000:.4f}" if b.success else ""
        writer.writerow([
            b.bin_label,
            b.size,
            dur,
            b.result.returncode,
            str(b.success).lower(),
        ])
    return buf.getvalue()


def bin_summary_to_csv(summaries: Sequence[BinSummary]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["bin", "count", "successful", "mean_ms"])
    for s in summaries:
        mean = f"{s.mean_ms:.4f}" if s.mean_ms is not None else ""
        writer.writerow([s.label, s.count, s.successful, mean])
    return buf.getvalue()


def binned_to_csv_file(binned: Sequence[BinnedResult], path: str | Path) -> None:
    Path(path).write_text(binned_to_csv(binned), encoding="utf-8")


def bin_summary_to_csv_file(summaries: Sequence[BinSummary], path: str | Path) -> None:
    Path(path).write_text(bin_summary_to_csv(summaries), encoding="utf-8")
