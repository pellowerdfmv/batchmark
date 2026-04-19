"""Tests for batchmark.aggregator."""

import pytest
from batchmark.aggregator import aggregate, format_aggregated
from batchmark.timer import TimingResult


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


RESULTS = [
    _r(100, 1.0),
    _r(100, 2.0),
    _r(100, 3.0, returncode=1),
    _r(200, 4.0),
    _r(200, 6.0),
]


def test_aggregate_returns_one_row_per_size():
    rows = aggregate(RESULTS)
    assert len(rows) == 2
    assert rows[0].size == 100
    assert rows[1].size == 200


def test_aggregate_counts_runs():
    rows = aggregate(RESULTS)
    assert rows[0].runs == 3
    assert rows[1].runs == 2


def test_aggregate_counts_successful():
    rows = aggregate(RESULTS)
    assert rows[0].successful == 2
    assert rows[1].successful == 2


def test_aggregate_mean():
    rows = aggregate(RESULTS)
    # mean ignores failures: (1.0 + 2.0) / 2 = 1.5
    assert rows[0].mean == pytest.approx(1.5)
    assert rows[1].mean == pytest.approx(5.0)


def test_aggregate_min_max():
    rows = aggregate(RESULTS)
    assert rows[1].min == pytest.approx(4.0)
    assert rows[1].max == pytest.approx(6.0)


def test_aggregate_empty():
    assert aggregate([]) == []


def test_aggregate_sorted_by_size():
    shuffled = [_r(300, 1.0), _r(100, 2.0), _r(200, 3.0)]
    rows = aggregate(shuffled)
    assert [r.size for r in rows] == [100, 200, 300]


def test_format_aggregated_contains_header():
    rows = aggregate(RESULTS)
    output = format_aggregated(rows)
    assert "Size" in output
    assert "Mean" in output
    assert "Median" in output


def test_format_aggregated_contains_sizes():
    rows = aggregate(RESULTS)
    output = format_aggregated(rows)
    assert "100" in output
    assert "200" in output


def test_format_aggregated_empty():
    output = format_aggregated([])
    assert "Size" in output
