"""Tests for batchmark.classifier_reporter."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.classifier import ClassifiedResult, classify_results
from batchmark.classifier_reporter import (
    format_classified_header,
    format_classified_row,
    print_classified_report,
)


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


def _cr(size: int, duration: float, returncode: int = 0) -> ClassifiedResult:
    return classify_results([_r(size, duration, returncode)])[0]


def test_format_classified_header_contains_columns():
    header = format_classified_header()
    assert "Size" in header
    assert "Duration" in header
    assert "Status" in header
    assert "Class" in header


def test_format_classified_row_ok():
    row = format_classified_row(_cr(100, 0.05))
    assert "100" in row
    assert "OK" in row
    assert "fast" in row


def test_format_classified_row_fail():
    row = format_classified_row(_cr(100, 0.5, returncode=1))
    assert "FAIL" in row
    assert "failed" in row


def test_format_classified_row_slow():
    row = format_classified_row(_cr(100, 2.0))
    assert "slow" in row


def test_print_classified_report_runs(capsys):
    classified = classify_results([_r(10, 0.05), _r(20, 1.5), _r(30, 0.3, returncode=1)])
    print_classified_report(classified)
    captured = capsys.readouterr()
    assert "fast" in captured.out
    assert "slow" in captured.out
    assert "failed" in captured.out
    assert "Classification summary" in captured.out
