"""Tests for batchmark.plotter."""

from __future__ import annotations

import pytest

from batchmark.aggregator import AggregatedResult
from batchmark.plotter import PlotConfig, _sparkline, format_plot, print_plot


def _agg(
    size: int,
    mean_ms: float | None = 100.0,
    successful: int = 5,
    total: int = 5,
) -> AggregatedResult:
    return AggregatedResult(
        size=size,
        total=total,
        successful=successful,
        mean_ms=mean_ms,
        median_ms=mean_ms,
        stdev_ms=0.0,
        min_ms=mean_ms,
        max_ms=mean_ms,
    )


# ── _sparkline ────────────────────────────────────────────────────────────────

def test_sparkline_empty_returns_empty():
    assert _sparkline([], 40) == ""


def test_sparkline_single_value_returns_one_char():
    result = _sparkline([42.0], 40)
    assert len(result) == 1


def test_sparkline_all_same_values_uses_lowest_spark():
    result = _sparkline([10.0, 10.0, 10.0], 40)
    # All equal → all map to bucket 0 → space character
    assert all(c == " " for c in result)


def test_sparkline_ascending_ends_higher():
    result = _sparkline([0.0, 50.0, 100.0], 40)
    assert result[-1] >= result[0]


def test_sparkline_respects_width():
    result = _sparkline(list(range(100)), 20)
    assert len(result) == 20


def test_sparkline_none_treated_as_zero():
    result = _sparkline([None, 100.0], 40)
    assert len(result) == 2


# ── format_plot ───────────────────────────────────────────────────────────────

def test_format_plot_empty_returns_no_data():
    assert format_plot([]) == "(no data to plot)"


def test_format_plot_contains_label():
    rows = [_agg(100, 50.0), _agg(200, 80.0)]
    output = format_plot(rows)
    assert "duration (ms)" in output


def test_format_plot_contains_min_max():
    rows = [_agg(100, 50.0), _agg(200, 150.0)]
    output = format_plot(rows)
    assert "min=50.0" in output
    assert "max=150.0" in output


def test_format_plot_contains_sizes():
    rows = [_agg(100), _agg(500)]
    output = format_plot(rows)
    assert "100" in output
    assert "500" in output


def test_format_plot_sorted_by_size():
    rows = [_agg(500, 90.0), _agg(100, 20.0), _agg(250, 50.0)]
    output = format_plot(rows)
    size_line = [l for l in output.splitlines() if "sizes:" in l][0]
    idx_100 = size_line.index("100")
    idx_250 = size_line.index("250")
    idx_500 = size_line.index("500")
    assert idx_100 < idx_250 < idx_500


def test_format_plot_no_axis_returns_single_line():
    rows = [_agg(100, 30.0), _agg(200, 60.0)]
    cfg = PlotConfig(show_axis=False)
    output = format_plot(rows, cfg)
    assert "\n" not in output


def test_format_plot_all_failed_shows_zeros():
    rows = [_agg(100, mean_ms=None, successful=0)]
    output = format_plot(rows)
    assert "min=0.0" in output


def test_print_plot_outputs_to_stdout(capsys):
    rows = [_agg(100, 40.0), _agg(200, 80.0)]
    print_plot(rows)
    captured = capsys.readouterr()
    assert "duration (ms)" in captured.out
