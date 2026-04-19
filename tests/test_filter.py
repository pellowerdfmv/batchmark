"""Tests for batchmark.filter."""

import pytest
from batchmark.timer import TimingResult
from batchmark.filter import (
    filter_by_size,
    filter_by_success,
    filter_by_max_duration,
    filter_results,
)


def _r(size: int, returncode: int = 0, elapsed: float = 1.0) -> TimingResult:
    return TimingResult(size=size, returncode=returncode, elapsed=elapsed, stdout="", stderr="")


RESULTS = [
    _r(10),
    _r(100, elapsed=2.0),
    _r(1000, returncode=1, elapsed=5.0),
    _r(10000, elapsed=0.5),
]


def test_filter_by_size_keeps_matching():
    out = filter_by_size(RESULTS, [10, 1000])
    assert [r.size for r in out] == [10, 1000]


def test_filter_by_size_none_returns_all():
    assert filter_by_size(RESULTS, None) is RESULTS


def test_filter_by_size_empty_returns_all():
    assert filter_by_size(RESULTS, []) is RESULTS


def test_filter_by_success_removes_failures():
    out = filter_by_success(RESULTS)
    assert all(r.returncode == 0 for r in out)
    assert len(out) == 3


def test_filter_by_max_duration():
    out = filter_by_max_duration(RESULTS, 1.5)
    assert all(r.elapsed <= 1.5 for r in out)
    assert {r.size for r in out} == {10, 10000}


def test_filter_results_combined():
    out = filter_results(RESULTS, sizes=[100, 1000, 10000], only_success=True, max_duration=3.0)
    assert [r.size for r in out] == [100, 10000]


def test_filter_results_no_filters_returns_all():
    out = filter_results(RESULTS)
    assert out == RESULTS


def test_filter_results_max_duration_zero():
    out = filter_results(RESULTS, max_duration=0.0)
    assert out == []
