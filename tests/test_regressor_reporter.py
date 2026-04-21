"""Tests for batchmark.regressor_reporter."""

from __future__ import annotations

import io
from contextlib import redirect_stdout

from batchmark.regressor import RegressionResult
from batchmark.regressor_reporter import (
    format_regression_header,
    format_regression_row,
    format_regression_summary,
    print_regression_report,
)


def _r(size: int, baseline: float, current: float, regression: bool) -> RegressionResult:
    delta = current - baseline
    pct = (delta / baseline * 100.0) if baseline else 0.0
    return RegressionResult(
        size=size,
        baseline_ms=baseline,
        current_ms=current,
        delta_ms=delta,
        delta_pct=pct,
        is_regression=regression,
    )


def test_format_regression_header_contains_columns():
    header = format_regression_header()
    for col in ("size", "baseline_ms", "current_ms", "delta_ms", "delta_pct", "status"):
        assert col in header


def test_format_regression_row_ok():
    row = format_regression_row(_r(100, 100.0, 105.0, False))
    assert "100" in row
    assert "ok" in row
    assert "REGRESSED" not in row


def test_format_regression_row_regressed():
    row = format_regression_row(_r(200, 100.0, 125.0, True))
    assert "REGRESSED" in row
    assert "200" in row


def test_format_regression_row_none_values():
    r = RegressionResult(size=50, baseline_ms=None, current_ms=None,
                         delta_ms=None, delta_pct=None, is_regression=False)
    row = format_regression_row(r)
    assert "N/A" in row


def test_format_regression_summary_no_regressions():
    rows = [_r(100, 100.0, 102.0, False)]
    summary = format_regression_summary(rows)
    assert "no regressions" in summary
    assert "1" in summary


def test_format_regression_summary_with_regression():
    rows = [_r(100, 100.0, 120.0, True), _r(200, 80.0, 82.0, False)]
    summary = format_regression_summary(rows)
    assert "REGRESSIONS DETECTED" in summary
    assert "1" in summary


def test_print_regression_report_output():
    rows = [_r(100, 100.0, 115.0, True)]
    buf = io.StringIO()
    with redirect_stdout(buf):
        print_regression_report(rows, threshold_pct=10.0)
    out = buf.getvalue()
    assert "REGRESSED" in out
    assert "10.0%" in out
