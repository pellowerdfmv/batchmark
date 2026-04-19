"""Tests for batchmark.comparator."""

import pytest

from batchmark.comparator import ComparisonRow, compare, format_comparison
from batchmark.timer import TimingResult


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(command="cmd", size=size, duration=duration, returncode=returncode, stdout="", stderr="")


RESULTS_A = [_r(10, 1.0), _r(10, 1.2), _r(100, 5.0), _r(100, 5.4)]
RESULTS_B = [_r(10, 0.8), _r(10, 0.6), _r(100, 5.2), _r(100, 4.8)]


def test_compare_returns_one_row_per_size():
    rows = compare(RESULTS_A, RESULTS_B)
    assert len(rows) == 2
    assert {r.size for r in rows} == {10, 100}


def test_compare_delta_sign():
    rows = compare(RESULTS_A, RESULTS_B)
    row10 = next(r for r in rows if r.size == 10)
    # B is faster, delta should be negative
    assert row10.delta is not None
    assert row10.delta < 0


def test_compare_ratio():
    rows = compare(RESULTS_A, RESULTS_B)
    row10 = next(r for r in rows if r.size == 10)
    assert row10.ratio is not None
    assert row10.mean_a is not None and row10.mean_b is not None
    assert abs(row10.ratio - row10.mean_b / row10.mean_a) < 1e-9


def test_compare_missing_size_in_one_set():
    a = [_r(10, 1.0)]
    b = [_r(10, 0.9), _r(200, 3.0)]
    rows = compare(a, b)
    assert len(rows) == 2
    row200 = next(r for r in rows if r.size == 200)
    assert row200.mean_a is None
    assert row200.delta is None
    assert row200.ratio is None


def test_compare_all_failures_gives_none_mean():
    a = [_r(10, -1.0, returncode=-1)]
    b = [_r(10, 0.5)]
    rows = compare(a, b)
    assert rows[0].mean_a is None
    assert rows[0].delta is None


def test_format_comparison_contains_size():
    rows = compare(RESULTS_A, RESULTS_B)
    output = format_comparison(rows)
    assert "10" in output
    assert "100" in output


def test_format_comparison_contains_header_columns():
    rows = compare(RESULTS_A, RESULTS_B)
    output = format_comparison(rows)
    assert "Mean A" in output
    assert "Mean B" in output
    assert "Delta" in output
    assert "Ratio" in output


def test_format_comparison_empty():
    output = format_comparison([])
    assert "Size" in output
