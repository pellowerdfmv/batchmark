"""Console reporter for scored benchmark results."""

from __future__ import annotations

from typing import List

from batchmark.scorer import ScoredResult, format_scored

# Thresholds for colour-coded verdict
_FAST_THRESHOLD = 0.95   # score <= this => faster than baseline
_SLOW_THRESHOLD = 1.05   # score >= this => slower than baseline


def _verdict(score: float | None) -> str:
    if score is None:
        return "?"
    if score <= _FAST_THRESHOLD:
        return "FASTER"
    if score >= _SLOW_THRESHOLD:
        return "SLOWER"
    return "~SAME"


def _summary_line(rows: List[ScoredResult]) -> str:
    faster = sum(1 for r in rows if r.score is not None and r.score <= _FAST_THRESHOLD)
    slower = sum(1 for r in rows if r.score is not None and r.score >= _SLOW_THRESHOLD)
    same = sum(
        1 for r in rows
        if r.score is not None and _FAST_THRESHOLD < r.score < _SLOW_THRESHOLD
    )
    unknown = sum(1 for r in rows if r.score is None)
    parts = [f"faster={faster}", f"slower={slower}", f"same={same}"]
    if unknown:
        parts.append(f"unknown={unknown}")
    return "Summary: " + "  ".join(parts)


def print_score_results(rows: List[ScoredResult], *, verbose: bool = False) -> None:
    """Print scored results table and a short summary to stdout."""
    print(format_scored(rows))
    print()
    if verbose:
        for r in rows:
            verdict = _verdict(r.score)
            delta_s = f"{r.delta_pct:+.1f}%" if r.delta_pct is not None else "N/A"
            print(f"  size={r.size:>8}  verdict={verdict:<8}  delta={delta_s}")
        print()
    print(_summary_line(rows))
