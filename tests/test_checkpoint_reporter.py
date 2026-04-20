"""Tests for batchmark.checkpoint_reporter."""

from batchmark.checkpoint import CheckpointEntry
from batchmark.checkpoint_reporter import (
    format_checkpoint_header,
    format_checkpoint_row,
    format_checkpoint_summary,
    print_checkpoint_report,
)


def _entry(size=100, run_index=0, duration=0.5, returncode=0):
    return CheckpointEntry(
        size=size, run_index=run_index, duration=duration,
        returncode=returncode, stdout="", stderr=""
    )


def test_format_checkpoint_header_contains_columns():
    header = format_checkpoint_header()
    assert "Size" in header
    assert "Run" in header
    assert "Duration" in header
    assert "Status" in header


def test_format_checkpoint_row_ok():
    row = format_checkpoint_row(_entry(size=256, run_index=1, duration=0.123, returncode=0))
    assert "256" in row
    assert "1" in row
    assert "OK" in row
    assert "123" in row  # ms portion


def test_format_checkpoint_row_fail():
    row = format_checkpoint_row(_entry(returncode=1))
    assert "FAIL" in row
    assert "1" in row


def test_format_checkpoint_summary_counts():
    entries = [
        _entry(size=100, run_index=0, returncode=0),
        _entry(size=100, run_index=1, returncode=1),
        _entry(size=200, run_index=0, returncode=0),
    ]
    summary = format_checkpoint_summary(entries)
    assert "3" in summary
    assert "2" in summary  # sizes
    assert "2 OK" in summary or "2 ok" in summary.lower()


def test_print_checkpoint_report_no_entries(capsys):
    print_checkpoint_report([])
    captured = capsys.readouterr()
    assert "No checkpoint" in captured.out


def test_print_checkpoint_report_with_entries(capsys):
    entries = [_entry(size=512, run_index=0, duration=0.25, returncode=0)]
    print_checkpoint_report(entries)
    captured = capsys.readouterr()
    assert "512" in captured.out
    assert "OK" in captured.out
