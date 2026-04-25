"""Tests for batchmark.correlator_reporter."""
from __future__ import annotations

import io
from contextlib import redirect_stdout

from batchmark.correlator import CorrelationResult
from batchmark.correlator_reporter import (
    format_correlation_header,
    format_correlation_row,
    print_correlation_report,
)


def _row(
    size: int = 100,
    mean_ms: float | None = 42.5,
    variable: float | None = 3.14,
    pearson_r: float | None = 0.95,
) -> CorrelationResult:
    return CorrelationResult(size=size, mean_ms=mean_ms, variable=variable, pearson_r=pearson_r)


def test_format_correlation_header_contains_columns():
    header = format_correlation_header()
    for col in ["Size", "Mean", "Variable", "Pearson"]:
        assert col in header


def test_format_correlation_row_shows_size():
    row = format_correlation_row(_row(size=256))
    assert "256" in row


def test_format_correlation_row_shows_mean():
    row = format_correlation_row(_row(mean_ms=99.123))
    assert "99.123" in row


def test_format_correlation_row_none_mean_shows_na():
    row = format_correlation_row(_row(mean_ms=None))
    assert "N/A" in row


def test_format_correlation_row_none_variable_shows_na():
    row = format_correlation_row(_row(variable=None))
    assert "N/A" in row


def test_format_correlation_row_none_pearson_shows_na():
    row = format_correlation_row(_row(pearson_r=None))
    assert "N/A" in row


def test_print_correlation_report_outputs_rows():
    rows = [_row(size=10), _row(size=20)]
    buf = io.StringIO()
    with redirect_stdout(buf):
        print_correlation_report(rows)
    output = buf.getvalue()
    assert "10" in output
    assert "20" in output


def test_print_correlation_report_shows_pearson_summary():
    rows = [_row(pearson_r=0.8765)]
    buf = io.StringIO()
    with redirect_stdout(buf):
        print_correlation_report(rows)
    assert "0.8765" in buf.getvalue()
