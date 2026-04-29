"""Tests for batchmark.trimmer_reporter."""
from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.trimmer import TrimmerConfig, trim_results
from batchmark.trimmer_reporter import (
    format_trim_header,
    format_trim_row,
    print_trim_report,
)


def _r(size: int, duration: float = 0.05, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration,
        returncode=returncode,
        stdout="",
        stderr="",
    )


def test_format_trim_header_contains_columns():
    header = format_trim_header()
    assert "size" in header
    assert "duration" in header
    assert "status" in header


def test_format_trim_row_ok():
    results = trim_results([_r(100, duration=0.05)])
    row = format_trim_row(results[0])
    assert "100" in row
    assert "OK" in row
    assert "50.00ms" in row


def test_format_trim_row_trimmed_shows_dashes():
    results = trim_results([_r(100), _r(100)], TrimmerConfig(head=1))
    trimmed_row = next(r for r in results if r.trimmed)
    row = format_trim_row(trimmed_row)
    assert "TRIMMED" in row
    assert "---" in row


def test_format_trim_row_fail():
    results = trim_results([_r(200, returncode=1)])
    row = format_trim_row(results[0])
    assert "FAIL" in row


def test_print_trim_report_runs_without_error(capsys):
    results = trim_results(
        [_r(10), _r(10), _r(10)],
        TrimmerConfig(head=1, tail=1),
    )
    print_trim_report(results)
    captured = capsys.readouterr()
    assert "size" in captured.out
    assert "TRIMMED" in captured.out
    assert "Trimmer:" in captured.out
