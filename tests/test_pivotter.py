"""Tests for batchmark.pivotter, pivotter_reporter, and pivotter_exporter."""

from __future__ import annotations

import pytest

from batchmark.aggregator import AggregatedResult
from batchmark.pivotter import (
    available_metrics,
    format_pivot_summary,
    pivot_results,
)
from batchmark.pivotter_exporter import pivot_to_csv
from batchmark.pivotter_reporter import format_pivot_header, format_pivot_row


def _agg(size: int, mean: float = 10.0, median: float = 9.5,
         stdev: float = 1.0, mn: float = 8.0, mx: float = 12.0) -> AggregatedResult:
    return AggregatedResult(
        size=size, runs=5, successful=5,
        mean=mean, median=median, stdev=stdev, min=mn, max=mx,
    )


def test_available_metrics_contains_expected():
    keys = available_metrics()
    for k in ("mean", "median", "stdev", "min", "max"):
        assert k in keys


def test_pivot_results_returns_one_row_per_size():
    results = [_agg(100), _agg(200), _agg(300)]
    table = pivot_results(results)
    assert len(table.rows) == 3


def test_pivot_results_sorted_by_size():
    results = [_agg(300), _agg(100), _agg(200)]
    table = pivot_results(results)
    assert [r.size for r in table.rows] == [100, 200, 300]


def test_pivot_results_default_metrics_all_present():
    table = pivot_results([_agg(100)])
    assert set(table.metrics) == {"mean", "median", "stdev", "min", "max"}


def test_pivot_results_subset_metrics():
    table = pivot_results([_agg(100)], metrics=["mean", "min"])
    assert table.metrics == ["mean", "min"]
    assert "stdev" not in table.rows[0].values


def test_pivot_results_unknown_metric_raises():
    with pytest.raises(ValueError, match="Unknown metrics"):
        pivot_results([_agg(100)], metrics=["bogus"])


def test_pivot_row_values_correct():
    table = pivot_results([_agg(100, mean=20.0, median=19.0)], metrics=["mean", "median"])
    row = table.rows[0]
    assert row.values["mean"] == pytest.approx(20.0)
    assert row.values["median"] == pytest.approx(19.0)


def test_format_pivot_summary():
    table = pivot_results([_agg(100), _agg(200)])
    summary = format_pivot_summary(table)
    assert "2" in summary
    assert "mean" in summary


def test_format_pivot_header_contains_metrics():
    table = pivot_results([_agg(100)], metrics=["mean", "stdev"])
    header = format_pivot_header(table)
    assert "mean" in header
    assert "stdev" in header
    assert "size" in header


def test_format_pivot_row_shows_size():
    table = pivot_results([_agg(512)], metrics=["mean"])
    row_str = format_pivot_row(table, 0)
    assert "512" in row_str


def test_format_pivot_row_shows_na_for_none():
    agg = _agg(100)
    agg.stdev = None
    table = pivot_results([agg], metrics=["stdev"])
    row_str = format_pivot_row(table, 0)
    assert "N/A" in row_str


def test_pivot_to_csv_has_header():
    table = pivot_results([_agg(100)], metrics=["mean", "min"])
    csv_str = pivot_to_csv(table)
    assert csv_str.splitlines()[0] == "size,mean,min"


def test_pivot_to_csv_row_count():
    table = pivot_results([_agg(100), _agg(200)], metrics=["mean"])
    lines = [l for l in pivot_to_csv(table).splitlines() if l]
    assert len(lines) == 3  # header + 2 data rows


def test_pivot_to_csv_empty_value_for_none():
    agg = _agg(100)
    agg.mean = None
    table = pivot_results([agg], metrics=["mean"])
    csv_str = pivot_to_csv(table)
    data_row = csv_str.splitlines()[1]
    assert data_row.endswith(",")
