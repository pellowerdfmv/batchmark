"""Tests for batchmark.streaker."""

from __future__ import annotations

from batchmark.streaker import detect_streaks, format_streak_summary, StreakResult
from batchmark.timer import TimingResult


def _r(size: int, returncode: int, duration: float = 0.1) -> TimingResult:
    return TimingResult(size=size, returncode=returncode, duration=duration, stdout="", stderr="")


def test_detect_streaks_returns_one_row_per_size():
    results = [_r(10, 0), _r(10, 0), _r(20, 1)]
    streaks = detect_streaks(results)
    assert len(streaks) == 2
    assert streaks[0].size == 10
    assert streaks[1].size == 20


def test_detect_streaks_empty_returns_empty():
    assert detect_streaks([]) == []


def test_all_successes_streak():
    results = [_r(10, 0), _r(10, 0), _r(10, 0)]
    s = detect_streaks(results)[0]
    assert s.current_streak == 3
    assert s.streak_type == "success"
    assert s.max_success_streak == 3
    assert s.max_failure_streak == 0


def test_all_failures_streak():
    results = [_r(5, 1), _r(5, 1)]
    s = detect_streaks(results)[0]
    assert s.current_streak == 2
    assert s.streak_type == "failure"
    assert s.max_failure_streak == 2
    assert s.max_success_streak == 0


def test_mixed_streak_ends_on_failure():
    results = [_r(10, 0), _r(10, 0), _r(10, 1)]
    s = detect_streaks(results)[0]
    assert s.streak_type == "failure"
    assert s.current_streak == 1
    assert s.max_success_streak == 2


def test_mixed_streak_ends_on_success():
    results = [_r(10, 1), _r(10, 1), _r(10, 0), _r(10, 0)]
    s = detect_streaks(results)[0]
    assert s.streak_type == "success"
    assert s.current_streak == 2
    assert s.max_failure_streak == 2


def test_total_count_correct():
    results = [_r(100, 0)] * 7
    s = detect_streaks(results)[0]
    assert s.total == 7


def test_preserves_size_order():
    results = [_r(30, 0), _r(10, 0), _r(20, 1)]
    streaks = detect_streaks(results)
    sizes = [s.size for s in streaks]
    assert sizes == [30, 10, 20]


def test_format_streak_summary_contains_header():
    streaks = [StreakResult(size=10, total=3, current_streak=2, streak_type="success",
                            max_success_streak=2, max_failure_streak=1)]
    out = format_streak_summary(streaks)
    assert "Size" in out
    assert "CurStreak" in out
    assert "MaxOK" in out


def test_format_streak_summary_empty():
    assert format_streak_summary([]) == "No streak data."


def test_format_streak_summary_contains_size():
    streaks = [StreakResult(size=512, total=5, current_streak=3, streak_type="failure",
                            max_success_streak=2, max_failure_streak=3)]
    out = format_streak_summary(streaks)
    assert "512" in out
    assert "failure" in out
