"""Tests for batchmark.reporter."""

import io
import pytest
from batchmark.timer import TimingResult
from batchmark.reporter import (
    format_header,
    format_row,
    format_summary,
    print_results,
)


def _make_result(size=100, run=1, elapsed=1.5, returncode=0, stdout="", stderr=""):
    return TimingResult(
        size=size, run=run, elapsed=elapsed,
        returncode=returncode, stdout=stdout, stderr=stderr
    )


def test_format_header_contains_columns():
    header = format_header()
    assert "size" in header
    assert "run" in header
    assert "elapsed" in header
    assert "returncode" in header
    assert "status" in header


def test_format_row_ok():
    r = _make_result(size=500, run=2, elapsed=2.1234, returncode=0)
    row = format_row(r)
    assert "500" in row
    assert "2" in row
    assert "2.1234" in row
    assert "OK" in row


def test_format_row_fail():
    r = _make_result(returncode=1)
    row = format_row(r)
    assert "FAIL" in row


def test_format_summary_counts():
    results = [
        _make_result(elapsed=1.0, returncode=0),
        _make_result(elapsed=3.0, returncode=0),
        _make_result(elapsed=0.5, returncode=1),
    ]
    summary = format_summary(results)
    assert "2/3" in summary
    assert "2.0000" in summary  # avg of 1.0 and 3.0
    assert "1.0000" in summary  # min
    assert "3.0000" in summary  # max


def test_format_summary_empty():
    assert format_summary([]) == "No results."


def test_print_results_writes_output():
    results = [_make_result(size=100, run=1, elapsed=0.42, returncode=0)]
    buf = io.StringIO()
    print_results(results, file=buf)
    output = buf.getvalue()
    assert "100" in output
    assert "0.4200" in output
    assert "OK" in output
    assert "Summary" in output
