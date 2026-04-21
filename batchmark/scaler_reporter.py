"""Console reporter for ScaledResult lists."""

from __future__ import annotations

from typing import List

from batchmark.scaler import ScaledResult


def _fmt_ms(value: float) -> str:
    return f"{value * 1000:.2f} ms"


def _status(sr: ScaledResult) -> str:
    return "OK" if sr.success else "FAIL"


def format_scale_header() -> str:
    return f"{'Size':>10}  {'Status':>6}  {'Raw':>12}  {'Scaled':>12}  {'Factor':>8}"


def format_scale_row(sr: ScaledResult) -> str:
    raw = _fmt_ms(sr.duration)
    scaled = _fmt_ms(sr.scaled_duration) if sr.scaled_duration is not None else "N/A"
    return (
        f"{sr.size:>10}  "
        f"{_status(sr):>6}  "
        f"{raw:>12}  "
        f"{scaled:>12}  "
        f"{sr.scale_factor:>8.4f}"
    )


def format_scale_summary(scaled: List[ScaledResult]) -> str:
    total = len(scaled)
    ok = sum(1 for s in scaled if s.success)
    failed = total - ok
    parts = [f"Total: {total}", f"OK: {ok}"]
    if failed:
        parts.append(f"Failed: {failed}")
    if scaled:
        parts.append(f"Factor: {scaled[0].scale_factor:.4f}")
    return " | ".join(parts)


def print_scale_report(scaled: List[ScaledResult]) -> None:
    print(format_scale_header())
    print("-" * 56)
    for sr in scaled:
        print(format_scale_row(sr))
    print("-" * 56)
    print(format_scale_summary(scaled))
