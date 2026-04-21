"""Tests for batchmark.outlier module."""

import pytest
from batchmark.timer import TimingResult
from batchmark.outlier import OutlierConfig, OutlierResult, detect_outliers, _quartiles


def _r(size: int, duration: float, success: bool = True) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=0 if success else 1, stdout="", stderr="")


def test_quartiles_odd():
    q1, q3 = _quartiles([1.0, 2.0, 3.0, 4.0, 5.0])
    assert q1 == 2.0
    assert q3 == 4.0


def test_quartiles_even():
    q1, q3 = _quartiles([1.0, 2.0, 3.0, 4.0])
    assert q1 == 1.5
    assert q3 == 3.5


def test_detect_outliers_returns_one_per_result():
    results = [_r(10, 0.1), _r(10, 0.1), _r(10, 0.1), _r(10, 0.1), _r(10, 10.0)]
    out = detect_outliers(results)
    assert len(out) == 5


def test_detect_outliers_marks_spike_as_outlier():
    results = [_r(10, 0.1), _r(10, 0.11), _r(10, 0.09), _r(10, 0.1), _r(10, 100.0)]
    out = detect_outliers(results)
    last = out[-1]
    assert last.is_outlier is True


def test_detect_outliers_normal_values_not_outlier():
    results = [_r(10, 0.1), _r(10, 0.11), _r(10, 0.09), _r(10, 0.1), _r(10, 0.105)]
    out = detect_outliers(results)
    assert all(not r.is_outlier for r in out)


def test_detect_outliers_below_min_samples_no_fences():
    results = [_r(10, 0.1), _r(10, 100.0), _r(10, 0.1)]
    out = detect_outliers(results, OutlierConfig(min_samples=4))
    assert all(r.lower_fence is None for r in out)
    assert all(not r.is_outlier for r in out)


def test_detect_outliers_failed_results_not_marked_outlier():
    results = [_r(10, 0.1), _r(10, 0.1), _r(10, 0.1), _r(10, 0.1), _r(10, 999.0, success=False)]
    out = detect_outliers(results)
    failed = next(r for r in out if not r.success)
    assert failed.is_outlier is False


def test_detect_outliers_custom_multiplier():
    results = [_r(10, 1.0), _r(10, 1.0), _r(10, 1.0), _r(10, 1.0), _r(10, 2.5)]
    tight = detect_outliers(results, OutlierConfig(iqr_multiplier=0.1))
    loose = detect_outliers(results, OutlierConfig(iqr_multiplier=10.0))
    assert any(r.is_outlier for r in tight)
    assert not any(r.is_outlier for r in loose)


def test_outlier_result_properties():
    r = _r(128, 0.5)
    out = OutlierResult(result=r, is_outlier=False, lower_fence=0.1, upper_fence=1.0)
    assert out.size == 128
    assert out.duration == 0.5
    assert out.success is True


def test_detect_outliers_empty_input():
    assert detect_outliers([]) == []
