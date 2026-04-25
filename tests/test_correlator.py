"""Tests for batchmark.correlator."""
from __future__ import annotations

from batchmark.aggregator import AggregatedResult
from batchmark.correlator import (
    CorrelationResult,
    _pearson,
    correlate,
    format_correlation_summary,
)


def _agg(size: int, mean: float | None) -> AggregatedResult:
    return AggregatedResult(
        size=size,
        runs=3,
        successful=3 if mean is not None else 0,
        mean=mean,
        median=mean,
        stdev=0.0,
        min=mean,
        max=mean,
    )


def test_correlate_returns_one_row_per_result():
    results = [_agg(10, 100.0), _agg(20, 200.0), _agg(30, 300.0)]
    variables = {10: 1.0, 20: 2.0, 30: 3.0}
    rows = correlate(results, variables)
    assert len(rows) == 3


def test_correlate_sorted_by_size():
    results = [_agg(30, 300.0), _agg(10, 100.0), _agg(20, 200.0)]
    variables = {10: 1.0, 20: 2.0, 30: 3.0}
    rows = correlate(results, variables)
    assert [r.size for r in rows] == [10, 20, 30]


def test_correlate_perfect_positive_correlation():
    results = [_agg(10, 10.0), _agg(20, 20.0), _agg(30, 30.0)]
    variables = {10: 1.0, 20: 2.0, 30: 3.0}
    rows = correlate(results, variables)
    assert rows[0].pearson_r is not None
    assert abs(rows[0].pearson_r - 1.0) < 1e-9


def test_correlate_perfect_negative_correlation():
    results = [_agg(10, 30.0), _agg(20, 20.0), _agg(30, 10.0)]
    variables = {10: 1.0, 20: 2.0, 30: 3.0}
    rows = correlate(results, variables)
    assert rows[0].pearson_r is not None
    assert abs(rows[0].pearson_r - (-1.0)) < 1e-9


def test_correlate_missing_variable_gives_none():
    results = [_agg(10, 10.0), _agg(20, 20.0)]
    variables = {10: 1.0}  # size 20 missing
    rows = correlate(results, variables)
    size20 = next(r for r in rows if r.size == 20)
    assert size20.variable is None


def test_correlate_none_mean_excluded_from_pearson():
    # Only one valid pair -> pearson_r should be None
    results = [_agg(10, None), _agg(20, 20.0)]
    variables = {10: 1.0, 20: 2.0}
    rows = correlate(results, variables)
    assert rows[0].pearson_r is None


def test_pearson_identical_values_returns_none():
    # Zero variance -> undefined correlation
    assert _pearson([5.0, 5.0, 5.0], [1.0, 2.0, 3.0]) is None


def test_pearson_single_pair_returns_none():
    assert _pearson([1.0], [1.0]) is None


def test_format_correlation_summary_shows_r():
    rows = [CorrelationResult(size=10, mean_ms=10.0, variable=1.0, pearson_r=0.9876)]
    summary = format_correlation_summary(rows)
    assert "0.9876" in summary


def test_format_correlation_summary_empty():
    assert "No correlation" in format_correlation_summary([])
