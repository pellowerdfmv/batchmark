"""Tests for batchmark.outlier_reporter module."""

import pytest
from batchmark.timer import TimingResult
from batchmark.outlier import OutlierResult, detect_outliers
from batchmark.outlier_reporter import (
    format_outlier_header,
    format_outlier_row,
    format_outlier_summary,
    print_outlier_report,
)


def _r(size: int, duration: float, success: bool = True) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=0 if success else 1, stdout="", stderr="")


def _or(size: int, duration: float, is_outlier: bool = False, success: bool = True) -> OutlierResult:
    return OutlierResult(
        result=_r(size, duration, success),
        is_outlier=is_outlier,
        lower_fence=0.05 if success else None,
        upper_fence=0.5 if success else None,
    )


def test_format_outlier_header_contains_columns():
    header = format_outlier_header()
    assert "Size" in header
    assert "Duration" in header
    assert "Status" in header


def test_format_outlier_row_ok():
    row = format_outlier_row(_or(64, 0.1))
    assert "64" in row
    assert "ok" in row


def test_format_outlier_row_outlier_status():
    row = format_outlier_row(_or(64, 5.0, is_outlier=True))
    assert "OUTLIER" in row


def test_format_outlier_row_fail_status():
    row = format_outlier_row(_or(64, 0.0, success=False))
    assert "FAIL" in row


def test_format_outlier_row_shows_fences():
    row = format_outlier_row(_or(64, 0.1))
    assert "ms" in row


def test_format_outlier_summary_counts():
    items = [
        _or(10, 0.1),
        _or(10, 5.0, is_outlier=True),
        _or(10, 0.0, success=False),
    ]
    summary = format_outlier_summary(items)
    assert "Total: 3" in summary
    assert "Outliers: 1" in summary
    assert "Failures: 1" in summary


def test_print_outlier_report_runs(capsys):
    items = [_or(32, 0.2), _or(64, 0.3, is_outlier=True)]
    print_outlier_report(items)
    captured = capsys.readouterr()
    assert "OUTLIER" in captured.out
    assert "Size" in captured.out
