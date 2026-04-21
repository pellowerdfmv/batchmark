"""pruner_reporter.py — human-readable table for pruned results."""
from __future__ import annotations

from typing import List

from batchmark.pruner import PrunedResult, format_prune_summary


def _fmt_ms(value) -> str:
    if value is None:
        return "N/A"
    return f"{value * 1000:.2f} ms"


def _status(pr: PrunedResult) -> str:
    if pr.pruned:
        return f"PRUNED ({pr.reason})"
    if not pr.success:
        return "FAIL"
    return "OK"


def format_prune_header() -> str:
    return f"{'Size':>10}  {'Duration':>14}  {'Status':<24}"


def format_prune_row(pr: PrunedResult) -> str:
    return (
        f"{pr.size:>10}  "
        f"{_fmt_ms(pr.duration):>14}  "
        f"{_status(pr):<24}"
    )


def print_prune_report(pruned: List[PrunedResult]) -> None:
    print(format_prune_header())
    print("-" * 52)
    for pr in pruned:
        print(format_prune_row(pr))
    print()
    print(format_prune_summary(pruned))
