"""Tests for batchmark.sorter."""

import pytest
from batchmark.timer import TimingResult
from batchmark.sorter import sort_results, available_sort_keys


def _r(size: int, duration: float, rc: int = 0, label: str = "cmd") -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=rc, label=label)


def test_available_sort_keys_contains_expected():
    keys = available_sort_keys()
    for k in ("size", "duration", "returncode", "label"):
        assert k in keys


def test_sort_by_size_ascending():
    results = [_r(300, 1.0), _r(100, 2.0), _r(200, 0.5)]
    out = sort_results(results, key="size")
    assert [r.size for r in out] == [100, 200, 300]


def test_sort_by_size_descending():
    results = [_r(100, 1.0), _r(300, 2.0), _r(200, 0.5)]
    out = sort_results(results, key="size", reverse=True)
    assert [r.size for r in out] == [300, 200, 100]


def test_sort_by_duration():
    results = [_r(1, 3.0), _r(2, 1.0), _r(3, 2.0)]
    out = sort_results(results, key="duration")
    assert [r.duration for r in out] == [1.0, 2.0, 3.0]


def test_sort_by_duration_failed_last():
    """Failed results (duration < 0) should sort after successful ones."""
    results = [_r(1, -1.0, rc=1), _r(2, 0.5), _r(3, 2.0)]
    out = sort_results(results, key="duration")
    assert out[0].duration == 0.5
    assert out[-1].returncode == 1


def test_sort_by_label():
    results = [_r(1, 1.0, label="zzz"), _r(2, 1.0, label="aaa"), _r(3, 1.0, label="mmm")]
    out = sort_results(results, key="label")
    assert [r.label for r in out] == ["aaa", "mmm", "zzz"]


def test_sort_by_returncode():
    results = [_r(1, 1.0, rc=2), _r(2, 1.0, rc=0), _r(3, 1.0, rc=1)]
    out = sort_results(results, key="returncode")
    assert [r.returncode for r in out] == [0, 1, 2]


def test_sort_does_not_mutate_input():
    results = [_r(300, 1.0), _r(100, 2.0)]
    original_order = [r.size for r in results]
    sort_results(results, key="size")
    assert [r.size for r in results] == original_order


def test_unknown_key_raises():
    with pytest.raises(ValueError, match="Unknown sort key"):
        sort_results([], key="nonexistent")
