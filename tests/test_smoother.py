"""Tests for batchmark.smoother."""

from __future__ import annotations

from batchmark.smoother import (
    SmootherConfig,
    SmoothedResult,
    smooth_results,
    format_smooth_summary,
)
from batchmark.timer import TimingResult


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


def test_smooth_results_returns_one_per_input():
    results = [_r(10, 0.1), _r(10, 0.2), _r(10, 0.3)]
    out = smooth_results(results)
    assert len(out) == 3


def test_smooth_result_has_none_before_window_filled():
    results = [_r(10, 0.1), _r(10, 0.2), _r(10, 0.3)]
    config = SmootherConfig(window_size=3)
    out = smooth_results(results, config)
    assert out[0].smoothed_duration is None
    assert out[1].smoothed_duration is None
    assert out[2].smoothed_duration is not None


def test_smooth_result_value_is_correct_average():
    results = [_r(10, 0.1), _r(10, 0.2), _r(10, 0.3)]
    config = SmootherConfig(window_size=3)
    out = smooth_results(results, config)
    assert abs(out[2].smoothed_duration - 0.2) < 1e-9


def test_smooth_window_size_one_always_filled():
    results = [_r(5, 0.5), _r(5, 0.6)]
    config = SmootherConfig(window_size=1)
    out = smooth_results(results, config)
    assert out[0].smoothed_duration == 0.5
    assert out[1].smoothed_duration == 0.6


def test_smooth_ignores_failures_by_default():
    results = [_r(10, 0.1), _r(10, 0.9, returncode=1), _r(10, 0.2), _r(10, 0.3)]
    config = SmootherConfig(window_size=3, only_successful=True)
    out = smooth_results(results, config)
    # failed result should have no smoothed value
    assert out[1].smoothed_duration is None
    # third successful result (index 2 in eligible) completes the window
    assert out[3].smoothed_duration is not None


def test_smooth_includes_failures_when_disabled():
    results = [_r(10, 0.1), _r(10, 0.2, returncode=1), _r(10, 0.3)]
    config = SmootherConfig(window_size=2, only_successful=False)
    out = smooth_results(results, config)
    assert out[1].smoothed_duration is not None


def test_smooth_groups_by_size():
    results = [_r(10, 0.1), _r(20, 0.5), _r(10, 0.2), _r(20, 0.6)]
    config = SmootherConfig(window_size=2)
    out = smooth_results(results, config)
    size_10 = [s for s in out if s.size == 10]
    size_20 = [s for s in out if s.size == 20]
    assert size_10[0].smoothed_duration is None
    assert size_10[1].smoothed_duration is not None
    assert size_20[0].smoothed_duration is None
    assert size_20[1].smoothed_duration is not None


def test_smooth_preserves_result_reference():
    r = _r(10, 0.1)
    out = smooth_results([r], SmootherConfig(window_size=1))
    assert out[0].result is r


def test_format_smooth_summary_counts():
    results = [_r(10, 0.1), _r(10, 0.2), _r(10, 0.3)]
    config = SmootherConfig(window_size=3)
    out = smooth_results(results, config)
    summary = format_smooth_summary(out)
    assert "1/3" in summary


def test_smooth_empty_input():
    out = smooth_results([])
    assert out == []
