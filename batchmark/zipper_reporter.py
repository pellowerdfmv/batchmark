"""Reporter for ZippedPair results."""

from __future__ import annotations

from typing import List, Optional

from batchmark.zipper import ZipConfig, ZippedPair


def _fmt_ms(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value * 1000:.2f} ms"


def _fmt_delta(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 1000:.2f} ms"


def format_zip_header(config: Optional[ZipConfig] = None) -> str:
    if config is None:
        config = ZipConfig()
    cols = ["size", "idx", config.left_label, config.right_label, "delta"]
    return "  ".join(f"{c:<14}" for c in cols)


def format_zip_row(pair: ZippedPair) -> str:
    cols = [
        str(pair.size),
        str(pair.index),
        _fmt_ms(pair.left_duration),
        _fmt_ms(pair.right_duration),
        _fmt_delta(pair.delta),
    ]
    return "  ".join(f"{c:<14}" for c in cols)


def print_zip_report(
    pairs: List[ZippedPair],
    config: Optional[ZipConfig] = None,
) -> None:
    from batchmark.zipper import format_zip_summary

    if config is None:
        config = ZipConfig()
    print(format_zip_header(config))
    print("-" * 74)
    for pair in pairs:
        print(format_zip_row(pair))
    print()
    print(format_zip_summary(pairs, config))
