from __future__ import annotations

from batchmark.capper import CappedResult
from batchmark.timer import TimingResult
from batchmark.capper_reporter import (
    format_cap_header,
    format_cap_row,
    format_cap_summary,
    print_cap_report,
)


def _r(size: int, duration: float, success: bool = True) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=0 if success else 1, stdout="", stderr="")


def _cr(
    size: int,
    duration: float,
    original: float,
    cap_limit: float | None = None,
    capped: bool = False,
    success: bool = True,
) -> CappedResult:
    return CappedResult(
        result=_r(size, duration, success),
        original_duration=original,
        cap_limit=cap_limit,
        capped=capped,
    )


def test_format_cap_header_contains_columns():
    header = format_cap_header()
    assert "Size" in header
    assert "Duration" in header
    assert "Original" in header
    assert "Cap" in header
    assert "Status" in header


def test_format_cap_row_ok():
    row = format_cap_row(_cr(100, 0.05, 0.05, cap_limit=0.1, capped=False))
    assert "100" in row
    assert "OK" in row


def test_format_cap_row_capped():
    row = format_cap_row(_cr(200, 0.1, 0.25, cap_limit=0.1, capped=True))
    assert "CAPPED" in row
    assert "200" in row


def test_format_cap_row_fail():
    row = format_cap_row(_cr(300, 0.0, 0.0, success=False))
    assert "FAIL" in row


def test_format_cap_row_no_cap_limit_shows_none():
    row = format_cap_row(_cr(50, 0.02, 0.02, cap_limit=None, capped=False))
    assert "none" in row


def test_format_cap_summary_counts():
    results = [
        _cr(10, 0.01, 0.01),
        _cr(20, 0.1, 0.2, cap_limit=0.1, capped=True),
        _cr(30, 0.0, 0.0, success=False),
    ]
    summary = format_cap_summary(results)
    assert "Total : 3" in summary
    assert "Capped: 1" in summary
    assert "Failed: 1" in summary


def test_print_cap_report_runs_without_error(capsys):
    results = [
        _cr(100, 0.05, 0.05),
        _cr(200, 0.1, 0.15, cap_limit=0.1, capped=True),
    ]
    print_cap_report(results)
    captured = capsys.readouterr()
    assert "Size" in captured.out
    assert "CAPPED" in captured.out
