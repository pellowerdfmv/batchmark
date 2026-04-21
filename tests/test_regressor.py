"""Tests for batchmark.regressor."""

from __future__ import annotations

import pytest

from batchmark.aggregator import AggregatedResult
from batchmark.regressor import (
    RegressionResult,
    any_regression,
    detect_regressions,
)


def _agg(size: int, mean: float | None) -> AggregatedResult:
    return AggregatedResult(
        size=size,
        runs=5,
        successful=5 if mean is not None else 0,
        mean=mean,
        median=mean,
        stdev=0.0,
        min=mean,
        max=mean,
    )


def test_detect_regressions_returns_one_row_per_result():
    aggs = [_agg(100, 50.0), _agg(200, 80.0)]
    baselines = {100: 45.0, 200: 75.0}
    rows = detect_regressions(aggs, baselines)
    assert len(rows) == 2


def test_detect_regressions_sorted_by_size():
    aggs = [_agg(300, 90.0), _agg(100, 50.0)]
    baselines = {300: 85.0, 100: 45.0}
    rows = detect_regressions(aggs, baselines)
    assert rows[0].size == 100
    assert rows[1].size == 300


def test_no_regression_within_threshold():
    aggs = [_agg(100, 105.0)]
    baselines = {100: 100.0}
    rows = detect_regressions(aggs, baselines, threshold_pct=10.0)
    assert rows[0].is_regression is False


def test_regression_detected_above_threshold():
    aggs = [_agg(100, 115.0)]
    baselines = {100: 100.0}
    rows = detect_regressions(aggs, baselines, threshold_pct=10.0)
    assert rows[0].is_regression is True


def test_delta_ms_and_pct_computed_correctly():
    aggs = [_agg(100, 120.0)]
    baselines = {100: 100.0}
    row = detect_regressions(aggs, baselines)[0]
    assert row.delta_ms == pytest.approx(20.0)
    assert row.delta_pct == pytest.approx(20.0)


def test_missing_baseline_not_flagged():
    aggs = [_agg(100, 200.0)]
    rows = detect_regressions(aggs, baselines={})
    assert rows[0].is_regression is False
    assert rows[0].delta_pct is None


def test_none_mean_not_flagged():
    aggs = [_agg(100, None)]
    baselines = {100: 100.0}
    rows = detect_regressions(aggs, baselines)
    assert rows[0].is_regression is False


def test_any_regression_true():
    rows = [
        RegressionResult(100, 100.0, 120.0, 20.0, 20.0, True),
        RegressionResult(200, 80.0, 82.0, 2.0, 2.5, False),
    ]
    assert any_regression(rows) is True


def test_any_regression_false():
    rows = [
        RegressionResult(100, 100.0, 105.0, 5.0, 5.0, False),
    ]
    assert any_regression(rows) is False


def test_zero_baseline_delta_pct_is_zero():
    aggs = [_agg(100, 50.0)]
    baselines = {100: 0.0}
    row = detect_regressions(aggs, baselines)[0]
    assert row.delta_pct == pytest.approx(0.0)
