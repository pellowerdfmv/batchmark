"""Tests for batchmark/pruner_reporter.py."""
from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.pruner import PrunerConfig, PrunedResult, prune_results
from batchmark.pruner_reporter import (
    format_prune_header,
    format_prune_row,
    print_prune_report,
)


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


def _pr(size: int, duration: float, pruned: bool = False, reason=None) -> PrunedResult:
    return PrunedResult(
        result=_r(size, duration),
        pruned=pruned,
        reason=reason,
    )


def test_format_prune_header_contains_columns():
    header = format_prune_header()
    assert "Size" in header
    assert "Duration" in header
    assert "Status" in header


def test_format_prune_row_ok():
    row = format_prune_row(_pr(100, 0.25))
    assert "100" in row
    assert "250.00 ms" in row
    assert "OK" in row


def test_format_prune_row_pruned_above():
    row = format_prune_row(_pr(200, 9.9, pruned=True, reason="above_upper_pct"))
    assert "PRUNED" in row
    assert "above_upper_pct" in row


def test_format_prune_row_pruned_below():
    row = format_prune_row(_pr(50, 0.001, pruned=True, reason="below_lower_pct"))
    assert "PRUNED" in row
    assert "below_lower_pct" in row


def test_format_prune_row_fail():
    pr = PrunedResult(
        result=TimingResult(size=10, duration=None, returncode=1, stdout="", stderr=""),
        pruned=False,
        reason=None,
    )
    row = format_prune_row(pr)
    assert "FAIL" in row
    assert "N/A" in row


def test_print_prune_report_runs_without_error(capsys):
    results = [_r(i * 10, i * 0.1) for i in range(1, 6)]
    config = PrunerConfig(lower_pct=0.0, upper_pct=0.8)
    pruned = prune_results(results, config)
    print_prune_report(pruned)
    captured = capsys.readouterr()
    assert "Pruner:" in captured.out
    assert "Size" in captured.out
