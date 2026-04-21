"""Tests for batchmark.windower."""

import pytest
from batchmark.timer import TimingResult
from batchmark.windower import (
    WindowConfig,
    compute_windows,
    format_window_summary,
)


def _r(size: int, duration: float, rc: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=rc, output="")


RESULTS = [_r(s, float(s)) for s in [10, 20, 30, 40, 50]]


def test_compute_windows_default_size():
    cfg = WindowConfig(size=3, step=1)
    windows = compute_windows(RESULTS, cfg)
    # 5 results, size=3, step=1 → 3 windows
    assert len(windows) == 3


def test_compute_windows_indices_are_sequential():
    cfg = WindowConfig(size=2, step=2)
    windows = compute_windows(RESULTS, cfg)
    assert [w.window_index for w in windows] == list(range(len(windows)))


def test_compute_windows_sizes_field_correct():
    cfg = WindowConfig(size=2, step=1)
    windows = compute_windows(RESULTS, cfg)
    assert windows[0].sizes == [10, 20]
    assert windows[1].sizes == [20, 30]


def test_compute_windows_count_matches_window_size():
    cfg = WindowConfig(size=3, step=1)
    windows = compute_windows(RESULTS, cfg)
    for w in windows:
        assert w.count == 3


def test_compute_windows_mean_is_average_of_durations():
    cfg = WindowConfig(size=3, step=1)
    windows = compute_windows(RESULTS, cfg)
    # first window: sizes 10,20,30 → durations 10,20,30 → mean 20
    assert windows[0].mean_ms == pytest.approx(20.0)


def test_compute_windows_only_successful_excludes_failures():
    results = [_r(10, 5.0), _r(20, 10.0, rc=1), _r(30, 15.0)]
    cfg = WindowConfig(size=3, step=1, only_successful=True)
    windows = compute_windows(results, cfg)
    assert len(windows) == 1
    assert windows[0].successful == 2
    # mean of 5.0 and 15.0
    assert windows[0].mean_ms == pytest.approx(10.0)


def test_compute_windows_only_successful_false_includes_all():
    results = [_r(10, 5.0), _r(20, 10.0, rc=1), _r(30, 15.0)]
    cfg = WindowConfig(size=3, step=1, only_successful=False)
    windows = compute_windows(results, cfg)
    assert windows[0].mean_ms == pytest.approx(10.0)


def test_compute_windows_empty_input_returns_empty():
    assert compute_windows([], WindowConfig()) == []


def test_compute_windows_fewer_results_than_window_size():
    results = [_r(10, 5.0), _r(20, 10.0)]
    cfg = WindowConfig(size=5, step=1)
    assert compute_windows(results, cfg) == []


def test_format_window_summary_no_windows():
    summary = format_window_summary([])
    assert "No windows" in summary


def test_format_window_summary_contains_count():
    cfg = WindowConfig(size=2, step=1)
    windows = compute_windows(RESULTS, cfg)
    summary = format_window_summary(windows)
    assert str(len(windows)) in summary
