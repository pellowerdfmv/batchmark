"""Tests for batchmark.diffuser and batchmark.diffuser_reporter."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.diffuser import (
    DiffConfig,
    DiffEntry,
    diff_results,
    format_diff_summary,
    _mean_ms,
)
from batchmark.diffuser_reporter import (
    format_diff_header,
    format_diff_row,
    print_diff_report,
)


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


# ---------------------------------------------------------------------------
# _mean_ms
# ---------------------------------------------------------------------------

def test_mean_ms_basic():
    results = [_r(10, 0.1), _r(10, 0.3)]
    assert _mean_ms(results) == pytest.approx(200.0)


def test_mean_ms_ignores_failures():
    results = [_r(10, 0.1), _r(10, 0.9, returncode=1)]
    assert _mean_ms(results) == pytest.approx(100.0)


def test_mean_ms_all_failed_returns_none():
    assert _mean_ms([_r(10, 0.5, returncode=1)]) is None


def test_mean_ms_empty_returns_none():
    assert _mean_ms([]) is None


# ---------------------------------------------------------------------------
# diff_results
# ---------------------------------------------------------------------------

def test_diff_returns_one_row_per_size():
    a = [_r(10, 0.1), _r(20, 0.2)]
    b = [_r(10, 0.15), _r(20, 0.18)]
    rows = diff_results(a, b)
    assert len(rows) == 2
    assert {r.size for r in rows} == {10, 20}


def test_diff_sorted_by_size():
    a = [_r(30, 0.3), _r(10, 0.1)]
    b = [_r(30, 0.35), _r(10, 0.12)]
    rows = diff_results(a, b)
    assert [r.size for r in rows] == [10, 30]


def test_diff_delta_sign_positive_when_b_slower():
    a = [_r(10, 0.1)]
    b = [_r(10, 0.2)]
    rows = diff_results(a, b)
    assert rows[0].delta is not None and rows[0].delta > 0


def test_diff_delta_negative_when_b_faster():
    a = [_r(10, 0.2)]
    b = [_r(10, 0.1)]
    rows = diff_results(a, b)
    assert rows[0].delta is not None and rows[0].delta < 0


def test_diff_missing_size_in_b_gives_none_mean_b():
    a = [_r(10, 0.1)]
    b: list = []
    rows = diff_results(a, b)
    assert rows[0].mean_b is None
    assert rows[0].delta is None
    assert rows[0].pct is None


def test_diff_missing_size_in_a_gives_none_mean_a():
    a: list = []
    b = [_r(10, 0.1)]
    rows = diff_results(a, b)
    assert rows[0].mean_a is None


def test_diff_uses_config_labels():
    cfg = DiffConfig(label_a="baseline", label_b="candidate")
    a = [_r(10, 0.1)]
    b = [_r(10, 0.2)]
    rows = diff_results(a, b, config=cfg)
    assert rows[0].label_a == "baseline"
    assert rows[0].label_b == "candidate"


def test_format_diff_summary_counts():
    entries = [
        DiffEntry(10, "A", "B", 100.0, 200.0, 100.0, 100.0),
        DiffEntry(20, "A", "B", 100.0, 80.0, -20.0, -20.0),
    ]
    summary = format_diff_summary(entries)
    assert "2" in summary
    assert "1 slower" in summary
    assert "1 faster" in summary


# ---------------------------------------------------------------------------
# reporter
# ---------------------------------------------------------------------------

def test_format_diff_header_contains_columns():
    entry = DiffEntry(10, "A", "B", 100.0, 110.0, 10.0, 10.0)
    header = format_diff_header(entry)
    assert "size" in header
    assert "delta" in header


def test_format_diff_row_shows_size():
    entry = DiffEntry(512, "A", "B", 50.0, 60.0, 10.0, 20.0)
    row = format_diff_row(entry)
    assert "512" in row


def test_format_diff_row_shows_na_for_none():
    entry = DiffEntry(512, "A", "B", None, 60.0, None, None)
    row = format_diff_row(entry)
    assert "N/A" in row


def test_print_diff_report_empty(capsys):
    print_diff_report([])
    out = capsys.readouterr().out
    assert "No diff" in out


def test_print_diff_report_with_entries(capsys):
    entries = [
        DiffEntry(10, "A", "B", 100.0, 120.0, 20.0, 20.0),
    ]
    print_diff_report(entries)
    out = capsys.readouterr().out
    assert "10" in out
    assert "Summary" in out
