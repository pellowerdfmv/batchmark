"""Tests for batchmark.scorer."""

from __future__ import annotations

from typing import Optional

import pytest

from batchmark.aggregator import AggregatedResult
from batchmark.scorer import ScoredResult, format_scored, score_results


def _agg(size: int, mean: Optional[float]) -> AggregatedResult:
    return AggregatedResult(
        size=size,
        runs=3,
        successful=3,
        mean=mean,
        median=mean,
        stdev=0.0,
        min=mean,
        max=mean,
    )


def test_score_results_returns_one_row_per_result():
    results = [_agg(100, 200.0), _agg(200, 400.0)]
    baseline = [_agg(100, 100.0), _agg(200, 200.0)]
    scored = score_results(results, baseline)
    assert len(scored) == 2


def test_score_is_ratio_of_mean_to_baseline():
    results = [_agg(100, 300.0)]
    baseline = [_agg(100, 100.0)]
    scored = score_results(results, baseline)
    assert scored[0].score == pytest.approx(3.0)


def test_score_one_when_equal_to_baseline():
    results = [_agg(100, 50.0)]
    baseline = [_agg(100, 50.0)]
    scored = score_results(results, baseline)
    assert scored[0].score == pytest.approx(1.0)


def test_delta_pct_positive_when_slower():
    results = [_agg(100, 150.0)]
    baseline = [_agg(100, 100.0)]
    scored = score_results(results, baseline)
    assert scored[0].delta_pct == pytest.approx(50.0)


def test_delta_pct_negative_when_faster():
    results = [_agg(100, 80.0)]
    baseline = [_agg(100, 100.0)]
    scored = score_results(results, baseline)
    assert scored[0].delta_pct == pytest.approx(-20.0)


def test_score_none_when_baseline_missing():
    results = [_agg(999, 100.0)]
    baseline = [_agg(100, 50.0)]
    scored = score_results(results, baseline)
    assert scored[0].score is None
    assert scored[0].delta_pct is None
    assert scored[0].baseline_mean is None


def test_score_none_when_result_mean_is_none():
    results = [_agg(100, None)]
    baseline = [_agg(100, 50.0)]
    scored = score_results(results, baseline)
    assert scored[0].score is None


def test_score_none_when_baseline_mean_is_zero():
    results = [_agg(100, 50.0)]
    baseline = [_agg(100, 0.0)]
    scored = score_results(results, baseline)
    assert scored[0].score is None


def test_format_scored_contains_header_columns():
    rows = [ScoredResult(size=100, mean=120.0, baseline_mean=100.0, score=1.2, delta_pct=20.0)]
    output = format_scored(rows)
    assert "Size" in output
    assert "Mean" in output
    assert "Score" in output
    assert "Delta" in output


def test_format_scored_shows_na_for_none():
    rows = [ScoredResult(size=100, mean=None, baseline_mean=None, score=None, delta_pct=None)]
    output = format_scored(rows)
    assert "N/A" in output
