"""Tests for batchmark.clamp_reporter."""

import pytest
from batchmark.capper import CappedResult
from batchmark.timer import TimingResult
from batchmark.clamp_reporter import (
    format_clamp_header,
    format_clamp_row,
    format_clamp_summary,
    print_clamp_report,
)


def _r(
    size: int,
    duration: float,
    original_duration: float,
    cap: float | None = None,
    was_clamped: bool = False,
    ok: bool = True,
) -> CappedResult:
    inner = TimingResult(
        command="echo test",
        size=size,
        duration=duration,
        returncode=0 if ok else 1,
        stdout="",
        stderr="",
    )
    return CappedResult(
        result=inner,
        original_duration=original_duration,
        cap=cap,
        was_clamped=was_clamped,
    )


def test_format_clamp_header_contains_columns():
    header = format_clamp_header()
    assert "Size" in header
    assert "Original" in header
    assert "Clamped" in header
    assert "Cap" in header
    assert "Status" in header


def test_format_clamp_row_ok():
    r = _r(100, 50.0, 50.0, cap=200.0, was_clamped=False)
    row = format_clamp_row(r)
    assert "100" in row
    assert "50.00ms" in row
    assert "OK" in row


def test_format_clamp_row_clamped():
    r = _r(200, 100.0, 350.0, cap=100.0, was_clamped=True)
    row = format_clamp_row(r)
    assert "CLAMPED" in row
    assert "100.00ms" in row
    assert "350.00ms" in row


def test_format_clamp_row_fail():
    r = _r(300, 0.0, 0.0, ok=False)
    row = format_clamp_row(r)
    assert "FAIL" in row


def test_format_clamp_summary_counts():
    results = [
        _r(10, 50.0, 50.0, was_clamped=False),
        _r(20, 100.0, 250.0, cap=100.0, was_clamped=True),
        _r(30, 0.0, 0.0, ok=False),
    ]
    summary = format_clamp_summary(results)
    assert "Total:   3" in summary
    assert "Clamped: 1" in summary
    assert "Failed:  1" in summary


def test_print_clamp_report_runs_without_error(capsys):
    results = [
        _r(10, 40.0, 40.0),
        _r(20, 80.0, 120.0, cap=80.0, was_clamped=True),
    ]
    print_clamp_report(results)
    captured = capsys.readouterr()
    assert "Size" in captured.out
    assert "CLAMPED" in captured.out
