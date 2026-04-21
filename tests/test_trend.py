"""Tests for batchmark.trend."""

from __future__ import annotations

from batchmark.aggregator import AggregatedResult
from batchmark.trend import TrendResult, analyze_trend, format_trend_summary


def _agg(size: int, mean: float | None, successful: int = 3) -> AggregatedResult:
    return AggregatedResult(
        size=size,
        runs=successful,
        successful=successful,
        mean=mean,
        median=mean,
        stdev=0.0,
        min=mean,
        max=mean,
    )


# --- analyze_trend -----------------------------------------------------------

def test_analyze_trend_returns_one_row_per_input():
    rows = [_agg(100, 50.0), _agg(200, 80.0), _agg(400, 70.0)]
    result = analyze_trend(rows)
    assert len(result) == 3


def test_analyze_trend_sorted_by_size():
    rows = [_agg(400, 70.0), _agg(100, 50.0), _agg(200, 80.0)]
    result = analyze_trend(rows)
    assert [r.size for r in result] == [100, 200, 400]


def test_first_row_has_no_delta():
    rows = [_agg(100, 50.0), _agg(200, 80.0)]
    result = analyze_trend(rows)
    assert result[0].delta is None
    assert result[0].delta_pct is None
    assert result[0].direction == "n/a"


def test_direction_up_when_significantly_slower():
    rows = [_agg(100, 100.0), _agg(200, 150.0)]  # +50 %
    result = analyze_trend(rows)
    assert result[1].direction == "up"


def test_direction_down_when_significantly_faster():
    rows = [_agg(100, 100.0), _agg(200, 50.0)]  # -50 %
    result = analyze_trend(rows)
    assert result[1].direction == "down"


def test_direction_flat_within_threshold():
    rows = [_agg(100, 100.0), _agg(200, 103.0)]  # +3 %, within ±5 %
    result = analyze_trend(rows)
    assert result[1].direction == "flat"


def test_delta_value_is_correct():
    rows = [_agg(100, 200.0), _agg(200, 250.0)]
    result = analyze_trend(rows)
    assert abs(result[1].delta - 50.0) < 1e-9


def test_delta_pct_value_is_correct():
    rows = [_agg(100, 200.0), _agg(200, 250.0)]
    result = analyze_trend(rows)
    assert abs(result[1].delta_pct - 25.0) < 1e-9


def test_none_mean_skipped_for_prev():
    """A size with None mean should not update the previous-mean reference."""
    rows = [_agg(100, 100.0), _agg(200, None, successful=0), _agg(400, 120.0)]
    result = analyze_trend(rows)
    # third row should compare against size-100 mean (100.0), not None
    assert result[2].delta is not None
    assert abs(result[2].delta - 20.0) < 1e-9


def test_empty_input_returns_empty_list():
    assert analyze_trend([]) == []


# --- format_trend_summary ----------------------------------------------------

def test_format_trend_summary_counts_directions():
    trends = [
        TrendResult(100, 50.0, None, None, "n/a"),
        TrendResult(200, 80.0, 30.0, 60.0, "up"),
        TrendResult(400, 70.0, -10.0, -12.5, "down"),
        TrendResult(800, 71.0, 1.0, 1.4, "flat"),
    ]
    summary = format_trend_summary(trends)
    assert "1 size(s) slower" in summary
    assert "1 faster" in summary
    assert "1 flat" in summary
