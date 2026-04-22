"""Streak detection: find consecutive runs of successes or failures per size."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class StreakResult:
    size: int
    total: int
    current_streak: int
    streak_type: Optional[str]  # "success", "failure", or None
    max_success_streak: int
    max_failure_streak: int


def _compute_streaks(results: List[TimingResult]) -> StreakResult:
    """Compute streak statistics for a list of results sharing the same size."""
    if not results:
        raise ValueError("results must be non-empty")

    size = results[0].size
    current_streak = 0
    streak_type: Optional[str] = None
    max_success = 0
    max_failure = 0
    run_success = 0
    run_failure = 0

    for r in results:
        s = r.returncode == 0
        if streak_type is None:
            streak_type = "success" if s else "failure"
            current_streak = 1
        elif (streak_type == "success") == s:
            current_streak += 1
        else:
            streak_type = "success" if s else "failure"
            current_streak = 1

        if s:
            run_success = current_streak if streak_type == "success" else 1
            max_success = max(max_success, run_success)
        else:
            run_failure = current_streak if streak_type == "failure" else 1
            max_failure = max(max_failure, run_failure)

    return StreakResult(
        size=size,
        total=len(results),
        current_streak=current_streak,
        streak_type=streak_type,
        max_success_streak=max_success,
        max_failure_streak=max_failure,
    )


def detect_streaks(results: List[TimingResult]) -> List[StreakResult]:
    """Group results by size (preserving order) and compute streaks for each group."""
    from collections import OrderedDict

    groups: OrderedDict[int, List[TimingResult]] = OrderedDict()
    for r in results:
        groups.setdefault(r.size, []).append(r)

    return [_compute_streaks(group) for group in groups.values()]


def format_streak_summary(streaks: List[StreakResult]) -> str:
    """Return a human-readable summary of streak results."""
    if not streaks:
        return "No streak data."
    lines = [f"{'Size':>8}  {'Total':>5}  {'CurStreak':>9}  {'Type':>8}  {'MaxOK':>5}  {'MaxFail':>7}"]
    for s in streaks:
        stype = s.streak_type or "-"
        lines.append(
            f"{s.size:>8}  {s.total:>5}  {s.current_streak:>9}  {stype:>8}  "
            f"{s.max_success_streak:>5}  {s.max_failure_streak:>7}"
        )
    return "\n".join(lines)
