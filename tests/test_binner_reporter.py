"""Tests for batchmark.binner_reporter and batchmark.binner_exporter."""
from __future__ import annotations

import io
import sys

from batchmark.timer import TimingResult
from batchmark.binner import BinConfig, BinnedResult, BinSummary, bin_results, summarize_bins
from batchmark.binner_reporter import (
    format_bin_header,
    format_bin_row,
    format_bin_summary,
    print_bin_report,
)
from batchmark.binner_exporter import binned_to_csv, bin_summary_to_csv


def _r(size: int, duration: float = 0.05, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


_CFG = BinConfig(edges=[100, 500], labels=["small", "medium"])


def _b(size: int, label: str = "small", duration: float = 0.05, returncode: int = 0) -> BinnedResult:
    return BinnedResult(result=_r(size, duration, returncode), bin_label=label)


# --- reporter ---

def test_format_bin_header_contains_columns():
    header = format_bin_header()
    for col in ["Bin", "Size", "Duration", "Status"]:
        assert col in header


def test_format_bin_row_ok():
    row = format_bin_row(_b(50, "small", 0.1))
    assert "small" in row
    assert "50" in row
    assert "OK" in row


def test_format_bin_row_fail():
    row = format_bin_row(_b(50, "small", 0.1, returncode=1))
    assert "FAIL" in row
    assert "N/A" in row


def test_format_bin_summary_contains_labels():
    summaries = [BinSummary(label="small", count=3, successful=2, mean_ms=120.5)]
    out = format_bin_summary(summaries)
    assert "small" in out
    assert "120.50" in out


def test_format_bin_summary_none_mean_shows_na():
    summaries = [BinSummary(label="large", count=1, successful=0, mean_ms=None)]
    out = format_bin_summary(summaries)
    assert "N/A" in out


def test_print_bin_report_outputs_something(capsys):
    binned = bin_results([_r(50), _r(300)], _CFG)
    print_bin_report(binned)
    captured = capsys.readouterr()
    assert "Bin" in captured.out


# --- exporter ---

def test_binned_to_csv_has_header():
    binned = [_b(50, "small")]
    csv_text = binned_to_csv(binned)
    assert csv_text.splitlines()[0] == "bin,size,duration_ms,returncode,success"


def test_binned_to_csv_row_count():
    binned = [_b(50, "small"), _b(300, "medium")]
    lines = binned_to_csv(binned).strip().splitlines()
    assert len(lines) == 3  # header + 2 rows


def test_binned_to_csv_failed_row_has_empty_duration():
    binned = [_b(50, "small", returncode=1)]
    rows = binned_to_csv(binned).strip().splitlines()
    fields = rows[1].split(",")
    assert fields[2] == ""  # duration_ms empty


def test_bin_summary_to_csv_has_header():
    summaries = [BinSummary(label="small", count=2, successful=2, mean_ms=50.0)]
    csv_text = bin_summary_to_csv(summaries)
    assert csv_text.splitlines()[0] == "bin,count,successful,mean_ms"


def test_bin_summary_to_csv_none_mean_empty():
    summaries = [BinSummary(label="large", count=1, successful=0, mean_ms=None)]
    rows = bin_summary_to_csv(summaries).strip().splitlines()
    fields = rows[1].split(",")
    assert fields[3] == ""
