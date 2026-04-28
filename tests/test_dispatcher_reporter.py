"""Tests for batchmark.dispatcher_reporter."""

from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.dispatcher import DispatchConfig, DispatchedResult, dispatch_results
from batchmark.dispatcher_reporter import (
    format_dispatch_header,
    format_dispatch_row,
    format_dispatch_summary_table,
    print_dispatch_report,
)


def _r(size: int, rc: int = 0, dur: float = 0.25) -> TimingResult:
    return TimingResult(size=size, returncode=rc, duration=dur, stdout="", stderr="")


def _dr(size: int, handler: str = "default", rc: int = 0) -> DispatchedResult:
    return DispatchedResult(result=_r(size, rc=rc), handler=handler)


def test_format_dispatch_header_contains_columns():
    header = format_dispatch_header()
    for col in ("Size", "Handler", "Duration", "Status"):
        assert col in header


def test_format_dispatch_row_shows_size():
    row = format_dispatch_row(_dr(512))
    assert "512" in row


def test_format_dispatch_row_shows_handler():
    row = format_dispatch_row(_dr(10, handler="fast_lane"))
    assert "fast_lane" in row


def test_format_dispatch_row_ok_status():
    row = format_dispatch_row(_dr(10, rc=0))
    assert "OK" in row


def test_format_dispatch_row_fail_status():
    row = format_dispatch_row(_dr(10, rc=1))
    assert "FAIL" in row


def test_format_dispatch_summary_table_contains_handler_name():
    items = [_dr(10, "alpha"), _dr(20, "alpha"), _dr(30, "beta")]
    table = format_dispatch_summary_table(items)
    assert "alpha" in table
    assert "beta" in table


def test_format_dispatch_summary_table_counts_ok_fail():
    items = [_dr(10, "h", rc=0), _dr(20, "h", rc=1), _dr(30, "h", rc=0)]
    table = format_dispatch_summary_table(items)
    # 2 OK, 1 FAIL
    assert "2" in table
    assert "1" in table


def test_print_dispatch_report_runs_without_error(capsys):
    cfg = DispatchConfig(rules=[(1, 100, "small")])
    dispatched = dispatch_results([_r(50), _r(75)], cfg)
    print_dispatch_report(dispatched)  # should not raise
    captured = capsys.readouterr()
    assert "small" in captured.out
