"""Tests for batchmark.notifier."""

import pytest
from batchmark.timer import TimingResult
from batchmark.notifier import (
    NotifyConfig,
    Notification,
    _mean_ms,
    check_results,
    notify_all,
)


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, output="")


# --- _mean_ms ---

def test_mean_ms_basic():
    results = [_r(10, 0.1), _r(10, 0.3)]
    assert _mean_ms(results) == pytest.approx(200.0)


def test_mean_ms_ignores_failures():
    results = [_r(10, 0.1), _r(10, 0.5, returncode=1)]
    assert _mean_ms(results) == pytest.approx(100.0)


def test_mean_ms_all_failed_returns_none():
    results = [_r(10, 0.1, returncode=1)]
    assert _mean_ms(results) is None


def test_mean_ms_empty_returns_none():
    assert _mean_ms([]) is None


# --- check_results ---

def test_check_results_no_thresholds_returns_empty():
    results = [_r(10, 1.0)]
    notes = check_results(results, NotifyConfig())
    assert notes == []


def test_check_results_warn_triggered():
    results = [_r(10, 0.5)]  # 500 ms
    cfg = NotifyConfig(warn_above_ms=400.0)
    notes = check_results(results, cfg)
    assert len(notes) == 1
    assert notes[0].level == "warn"
    assert notes[0].size == 10


def test_check_results_fail_triggered():
    results = [_r(10, 1.0)]  # 1000 ms
    cfg = NotifyConfig(fail_above_ms=500.0)
    notes = check_results(results, cfg)
    assert len(notes) == 1
    assert notes[0].level == "fail"


def test_check_results_fail_takes_priority_over_warn():
    results = [_r(10, 1.0)]
    cfg = NotifyConfig(warn_above_ms=200.0, fail_above_ms=500.0)
    notes = check_results(results, cfg)
    levels = [n.level for n in notes]
    assert "fail" in levels
    assert "warn" not in levels


def test_check_results_on_any_failure():
    results = [_r(10, 0.1), _r(10, 0.1, returncode=1)]
    cfg = NotifyConfig(on_any_failure=True)
    notes = check_results(results, cfg)
    assert any(n.level == "fail" for n in notes)


def test_check_results_below_threshold_no_notification():
    results = [_r(10, 0.1)]  # 100 ms
    cfg = NotifyConfig(warn_above_ms=500.0)
    assert check_results(results, cfg) == []


# --- notify_all ---

def test_notify_all_groups_by_size():
    results = [
        _r(10, 1.0),   # 1000 ms — should warn
        _r(100, 0.1),  # 100 ms  — should not
    ]
    cfg = NotifyConfig(warn_above_ms=500.0)
    notes = notify_all(results, cfg)
    assert len(notes) == 1
    assert notes[0].size == 10


def test_notify_all_empty_returns_empty():
    assert notify_all([], NotifyConfig(warn_above_ms=100.0)) == []
