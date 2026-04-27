"""CSV export for ZippedPair results."""

from __future__ import annotations

import csv
import io
from typing import List, Optional

from batchmark.zipper import ZipConfig, ZippedPair


def _fmt(value: Optional[float]) -> str:
    return "" if value is None else f"{value:.6f}"


def zipped_to_csv(
    pairs: List[ZippedPair],
    config: Optional[ZipConfig] = None,
) -> str:
    if config is None:
        config = ZipConfig()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["size", "index", config.left_label, config.right_label, "delta"]
    )
    for p in pairs:
        writer.writerow(
            [
                p.size,
                p.index,
                _fmt(p.left_duration),
                _fmt(p.right_duration),
                _fmt(p.delta),
            ]
        )
    return buf.getvalue()


def zipped_to_csv_file(
    pairs: List[ZippedPair],
    path: str,
    config: Optional[ZipConfig] = None,
) -> None:
    with open(path, "w", newline="") as fh:
        fh.write(zipped_to_csv(pairs, config))
