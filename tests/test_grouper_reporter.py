"""Tests for batchmark.grouper_reporter."""

import io
from unittest.mock import patch

from batchmark.timer import TimingResult
from batchmark.grouper import GroupConfig, GroupedResult, group_results
from batchmark.grouper_reporter import (
    format_group_header,
    format_group_row,
    format_group_summary,
    print_group_report,
)


def _r(size: int, returncode: int = 0, duration: float = 0.1) -> TimingResult:
    return TimingResult(size=size, returncode=returncode, duration=duration, stdout="", stderr="")


def _g(size: int, label: str, returncode: int = 0, duration: float = 0.1) -> GroupedResult:
    return GroupedResult(result=_r(size, returncode, duration), label=label)


def test_format_group_header_contains_columns():
    header = format_group_header()
    assert "Label" in header
    assert "Size" in header
    assert "Duration" in header
    assert "Status" in header


def test_format_group_row_ok():
    g = _g(100, "small", returncode=0, duration=0.5)
    row = format_group_row(g)
    assert "small" in row
    assert "100" in row
    assert "OK" in row
    assert "500.00 ms" in row


def test_format_group_row_fail():
    g = _g(200, "medium", returncode=1, duration=0.05)
    row = format_group_row(g)
    assert "FAIL" in row
    assert "medium" in row


def test_format_group_summary_lists_labels():
    grouped = [
        _g(10, "small", returncode=0, duration=0.1),
        _g(20, "small", returncode=0, duration=0.3),
        _g(500, "medium", returncode=1, duration=0.2),
    ]
    summary = format_group_summary(grouped)
    assert "small" in summary
    assert "medium" in summary
    assert "2/2" in summary   # small: 2 ok of 2
    assert "0/1" in summary   # medium: 0 ok of 1


def test_format_group_summary_avg_na_when_all_failed():
    grouped = [_g(10, "small", returncode=1, duration=0.1)]
    summary = format_group_summary(grouped)
    assert "N/A" in summary


def test_print_group_report_outputs_rows(capsys):
    grouped = [
        _g(10, "small", returncode=0, duration=0.2),
        _g(500, "medium", returncode=0, duration=0.4),
    ]
    print_group_report(grouped)
    captured = capsys.readouterr()
    assert "small" in captured.out
    assert "medium" in captured.out
    assert "Group summary" in captured.out
